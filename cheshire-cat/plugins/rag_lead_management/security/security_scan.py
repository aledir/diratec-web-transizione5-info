"""
Scansione e verifica delle dipendenze per vulnerabilità.
"""
import subprocess
import json
import sys
import re
import pkg_resources
from datetime import datetime
from cat.log import log

def check_dependencies():
    """
    Verifica le vulnerabilità nelle dipendenze Python installate.
    
    Utilizza un metodo più leggero di scansione senza dipendenze esterne.
    
    Returns:
        bool: True se non ci sono vulnerabilità, False altrimenti
    """
    log.info(f"[{datetime.now().isoformat()}] Avvio verifica dipendenze...")
    
    try:
        # Ottieni le dipendenze installate
        installed_packages = [(d.project_name, d.version) for d in pkg_resources.working_set]
        log.info(f"Pacchetti installati: {len(installed_packages)}")
        
        # Controlla le versioni con problemi noti di sicurezza
        vulnerable_packages = []
        
        # Pacchetti vulnerabili noti (versione obsoleta o con CVE noti)
        # Formato: nome_pacchetto: (versione_vulnerabile, descrizione)
        known_vulnerabilities = {
            'jinja2': [
                ('<=2.11.2', 'Vulnerabilità XSS in Jinja2 nei template HTML'),
            ],
            'flask': [
                ('<=1.1.2', 'Possibile attacco path traversal in Flask'),
            ],
            'requests': [
                ('<=2.25.0', 'Vulnerabilità di divulgazione delle credenziali'),
            ],
            'urllib3': [
                ('<=1.26.4', 'Possibile SSRF in urllib3'),
            ],
            'pyyaml': [
                ('<=5.4.0', 'Deserializzazione insicura che può portare a RCE'),
            ],
            'sqlalchemy': [
                ('<=1.3.23', 'Possibile SQL injection in alcune configurazioni'),
            ],
            'cryptography': [
                ('<=3.3.2', 'Vulnerabilità nelle operazioni crittografiche'),
            ],
            'pillow': [
                ('<=8.1.2', 'Diverse vulnerabilità nell\'elaborazione delle immagini'),
            ],
            'django': [
                ('<=3.1.6', 'Vulnerabilità XSS e CSRF in Django'),
            ],
            'fastapi': [
                ('<=0.65.1', 'Vulnerabilità path traversal in alcune configurazioni'),
            ]
        }
        
        # Controlla ogni pacchetto installato
        for package_name, version in installed_packages:
            package_lower = package_name.lower()
            if package_lower in known_vulnerabilities:
                # Controlla se la versione è vulnerabile
                for vuln_version, description in known_vulnerabilities[package_lower]:
                    if version_compare(version, vuln_version):
                        vulnerable_packages.append({
                            'name': package_name,
                            'version': version,
                            'vulnerable_version': vuln_version,
                            'advisory': description
                        })
        
        if vulnerable_packages:
            log.warning(f"⚠️ Trovate {len(vulnerable_packages)} vulnerabilità:")
            for vuln in vulnerable_packages:
                log.warning(f"- {vuln['name']} {vuln['version']}: {vuln['advisory']}")
            
            # Registra nel database
            try:
                from .security_audit import audit_logger
                audit_logger.log_security_event(
                    "dependency_vulnerabilities",
                    "system",
                    {"vulnerabilities": vulnerable_packages},
                    "warning"
                )
            except (ImportError, AttributeError):
                pass  # Ignora se security_audit.py non è disponibile
            
            return False
        else:
            log.info("✅ Nessuna vulnerabilità nota trovata nelle dipendenze.")
            return True
            
    except Exception as e:
        log.error(f"❌ Errore durante la verifica delle dipendenze: {str(e)}")
        return False

def version_compare(current, constraint):
    """
    Verifica se una versione soddisfa un vincolo
    
    Args:
        current: Versione attuale
        constraint: Vincolo di versione (es. "<=1.2.3", ">=2.0.0")
        
    Returns:
        bool: True se la versione soddisfa il vincolo
    """
    operator_match = re.match(r'([<>=!]+)(.*)', constraint)
    if not operator_match:
        return current == constraint
    
    operator, version = operator_match.groups()
    
    # Converti in tuple per confronto
    current_parts = tuple(map(int, re.sub(r'[^0-9.]', '', current).split('.')))
    version_parts = tuple(map(int, re.sub(r'[^0-9.]', '', version).split('.')))
    
    # Estendi tuple alla stessa lunghezza
    max_len = max(len(current_parts), len(version_parts))
    current_parts = current_parts + (0,) * (max_len - len(current_parts))
    version_parts = version_parts + (0,) * (max_len - len(version_parts))
    
    if operator == '==':
        return current_parts == version_parts
    elif operator == '!=':
        return current_parts != version_parts
    elif operator == '<':
        return current_parts < version_parts
    elif operator == '<=':
        return current_parts <= version_parts
    elif operator == '>':
        return current_parts > version_parts
    elif operator == '>=':
        return current_parts >= version_parts
    else:
        return False

def check_dependencies_with_pip_audit():
    """
    Verifica le vulnerabilità nelle dipendenze Python usando pip-audit.
    NOTA: Richiede l'installazione di pip-audit, non raccomandato per uso automatico
    """
    log.info(f"[{datetime.now().isoformat()}] Avvio verifica dipendenze con pip-audit...")
    
    try:
        # Controlla se pip-audit è installato
        try:
            subprocess.run(["pip-audit", "--version"], 
                           capture_output=True, 
                           check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            log.error("❌ pip-audit non è installato o non è disponibile nel PATH")
            return False
        
        # Esegui pip-audit per verificare le vulnerabilità
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Analizza i risultati
        audit_data = json.loads(result.stdout)
        vulnerabilities = audit_data.get("vulnerabilities", [])
        
        if vulnerabilities:
            log.warning(f"⚠️ Trovate {len(vulnerabilities)} vulnerabilità:")
            for vuln in vulnerabilities:
                log.warning(f"- {vuln['name']} {vuln['version']}: {vuln['advisory']}")
            
            # Registra nel database
            try:
                from .security_audit import audit_logger
                audit_logger.log_security_event(
                    "dependency_vulnerabilities",
                    "system",
                    {"vulnerabilities": vulnerabilities},
                    "warning"
                )
            except (ImportError, AttributeError):
                pass  # Ignora se security_audit.py non è disponibile
            
            return False
        else:
            log.info("✅ Nessuna vulnerabilità trovata nelle dipendenze.")
            return True
            
    except subprocess.CalledProcessError as e:
        log.error(f"❌ Errore durante la verifica delle dipendenze: {e}")
        log.error(f"Output: {e.stderr}")
        return False
    except Exception as e:
        log.error(f"❌ Errore imprevisto: {str(e)}")
        return False

if __name__ == "__main__":
    """
    Questo permette di eseguire la verifica manualmente con:
    python -m lead_management.security.security_scan
    """
    success = check_dependencies()
    sys.exit(0 if success else 1)