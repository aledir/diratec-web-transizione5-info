"""
Plugin per la gestione del contesto CAG (Context Augmented Generation) di Transizione 5.0.
Crea e mantiene la KV-cache per il LLM.
"""
import os
import json
from pathlib import Path
from cat.mad_hatter.decorators import plugin
from cat.log import log

def ensure_directories_exist(documents_dir, context_dir, metadata_path=None):
    """Crea le directory necessarie e il file metadata.json se non esistono"""
    # Crea le directory necessarie
    os.makedirs(documents_dir, exist_ok=True)
    os.makedirs(documents_dir / "markdown", exist_ok=True)
    os.makedirs(context_dir, exist_ok=True)
    
    # Se non è specificato il percorso del file metadata, lo calcoliamo
    if metadata_path is None:
        metadata_path = documents_dir / "metadata.json"
    
    # Crea un file metadata.json vuoto se non esiste
    if not os.path.exists(metadata_path):
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump({
                "files": [],
                "categorie": [
                    "NORMATIVA SERVIZI",
                    "GUIDE",
                    "MODULI E MODELLI",
                    "PILLOLE INFORMATIVE"
                ],
                "tipi": [
                    "NORMATIVA",
                    "CIRCOLARE",
                    "FAQ",
                    "GUIDA",
                    "MODELLO"
                ]
            }, f, indent=2)
        log.info(f"✅ Creato file metadata.json vuoto in {metadata_path}")
    
    return True

@plugin
class CAGDocumentManager:
    def __init__(self, cat):
        self.cat = cat
        
        # Debug delle variabili d'ambiente
        mathpix_app_id_env = os.environ.get("MATHPIX_APP_ID", "")
        mathpix_app_key_env = os.environ.get("MATHPIX_APP_KEY", "")
        masked_key_env = "***" + mathpix_app_key_env[-4:] if mathpix_app_key_env else ""
        log.info(f"🔍 Debug - Variabili d'ambiente: MATHPIX_APP_ID={mathpix_app_id_env}, MATHPIX_APP_KEY={masked_key_env}")
        
        try:
            # Carica impostazioni dal plugin
            self.plugin_settings = cat.mad_hatter.get_plugin_settings("CAG Document Manager")
            log.info(f"🔍 Debug - Plugin settings ottenute: {type(self.plugin_settings)}")
            
            if self.plugin_settings:
                # Debug delle impostazioni del plugin
                log.info(f"🔍 Debug - Chiavi disponibili: {self.plugin_settings.keys() if hasattr(self.plugin_settings, 'keys') else 'Nessuna'}")
                
                # Leggi i valori specifici per Mathpix
                mathpix_app_id = self.plugin_settings.get("mathpix_app_id", "")
                mathpix_app_key = self.plugin_settings.get("mathpix_app_key", "")
                masked_key = "***" + mathpix_app_key[-4:] if mathpix_app_key else ""
                log.info(f"🔍 Debug - Plugin settings: mathpix_app_id={mathpix_app_id}, mathpix_app_key={masked_key}")
                
                # Se le impostazioni dal plugin sono vuote, prova a usare le variabili d'ambiente
                if not mathpix_app_id and mathpix_app_id_env:
                    log.info(f"📝 Utilizzo MATHPIX_APP_ID dalla variabile d'ambiente")
                    self.plugin_settings["mathpix_app_id"] = mathpix_app_id_env
                
                if not mathpix_app_key and mathpix_app_key_env:
                    log.info(f"📝 Utilizzo MATHPIX_APP_KEY dalla variabile d'ambiente")
                    self.plugin_settings["mathpix_app_key"] = mathpix_app_key_env
                
                # Verifica che le impostazioni necessarie siano presenti
                required_settings = ["documents_dir", "context_dir", "context_file"]
                for setting in required_settings:
                    if setting not in self.plugin_settings:
                        raise ValueError(f"Impostazione '{setting}' mancante per CAG Document Manager")
                
                log.info(f"🔍 CAG Document Manager - Impostazioni: {self.plugin_settings}")
                
                # Ottieni e verifica le directory
                documents_dir = Path(self.plugin_settings["documents_dir"])
                context_dir = Path(self.plugin_settings["context_dir"])
                
                # Assicura che le directory necessarie esistano
                ensure_directories_exist(documents_dir, context_dir)
                
                # Impostazioni KV-cache
                self.context_file = self.plugin_settings["context_file"]
                self.context_path = os.path.join(context_dir, self.context_file)
                log.info(f"📝 CAG Document Manager - File contesto: {self.context_path}")
                
            else:
                # Impostazioni predefinite se non sono disponibili quelle del plugin
                log.warning("⚠️ Impostazioni non trovate per CAG Document Manager, utilizzo valori predefiniti")
                documents_dir = Path("/app/cat/shared/documents")
                context_dir = Path("/app/cat/shared/documents/context")
                
                # Assicura che le directory necessarie esistano
                ensure_directories_exist(documents_dir, context_dir)
                
                # Crea impostazioni dalle variabili d'ambiente
                self.plugin_settings = {
                    "documents_dir": str(documents_dir),
                    "context_dir": str(context_dir),
                    "context_file": "cag_context.md",
                    "max_context_tokens": 180000,
                    "mathpix_app_id": mathpix_app_id_env,
                    "mathpix_app_key": mathpix_app_key_env
                }
                
                # Impostazioni KV-cache
                self.context_file = self.plugin_settings["context_file"]
                self.context_path = os.path.join(context_dir, self.context_file)
                log.info(f"📝 CAG Document Manager - File contesto: {self.context_path}")
            
            log.info("✅ CAG Document Manager inizializzato con successo")
            
        except Exception as e:
            log.error(f"❌ Errore nell'inizializzazione di CAG Document Manager: {str(e)}")
            # Non solleviamo l'eccezione per evitare che il plugin non venga caricato affatto
            documents_dir = Path("/app/cat/shared/documents")
            context_dir = Path("/app/cat/shared/documents/context")
            
            # Assicura che le directory necessarie esistano anche in caso di errore
            try:
                ensure_directories_exist(documents_dir, context_dir)
            except Exception as dir_error:
                log.error(f"❌ Errore nella creazione delle directory: {str(dir_error)}")
            
            self.plugin_settings = {
                "documents_dir": str(documents_dir),
                "context_dir": str(context_dir),
                "context_file": "cag_context.md",
                "max_context_tokens": 180000,
                "mathpix_app_id": mathpix_app_id_env,
                "mathpix_app_key": mathpix_app_key_env
            }
            self.context_file = "cag_context.md"
            self.context_path = os.path.join(context_dir, self.context_file)
    
    def get_settings(self):
        """Restituisce le impostazioni correnti del plugin."""
        return self.plugin_settings