"""
Funzionalità di audit e logging di sicurezza.
"""
from datetime import datetime
from cat.log import log
import json

class AuditLogger:
    """Gestisce l'audit trail e il logging di sicurezza."""
    
    def log_security_event(self, evento, session_id, dati=None, severity="warning"):
        """
        Registra un evento di sicurezza
        
        Args:
            evento: Tipo di evento
            session_id: ID della sessione
            dati: Dati aggiuntivi
            severity: Livello di gravità (info, warning, error)
        """
        try:
            # Importa localmente per evitare dipendenze circolari
            from ..analytics_operations import log_analytics_event
            
            # Prepara i dati dell'evento
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "severity": severity
            }
            
            # Aggiungi dati aggiuntivi se presenti
            if dati:
                event_data.update(dati)
            
            # Logga l'evento
            if severity == "warning":
                log.warning(f"⚠️ {evento}: session_id={session_id}")
            elif severity == "error":
                log.error(f"🚨 {evento}: session_id={session_id}")
            else:
                log.info(f"ℹ️ {evento}: session_id={session_id}")
            
            # Registra nel database
            log_analytics_event(
                evento=f"security_{evento}",
                session_id=session_id,
                dati=event_data
            )
        except Exception as e:
            log.error(f"❌ Errore nella registrazione dell'evento di sicurezza: {str(e)}")
    
    def log_lead_change(self, lead_id, user_id, action, old_data=None, new_data=None):
        """
        Registra una modifica a un lead nel log di audit
        
        Args:
            lead_id: ID del lead modificato
            user_id: ID dell'utente che ha effettuato la modifica
            action: Tipo di azione (create, update, delete)
            old_data: Dati precedenti (opzionale)
            new_data: Nuovi dati (opzionale)
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        try:
            # Importa localmente per evitare dipendenze circolari
            from ..database_operations import connect_db
            
            # Maschera dati sensibili dai log
            from .security_core import security
            
            if old_data:
                old_data = security.mask_sensitive_data(old_data)
            if new_data:
                new_data = security.mask_sensitive_data(new_data)

            # Connessione al database
            conn = connect_db()
            if not conn:
                return False

            # Verifica se esiste già la tabella audit_log
            with conn.cursor() as cursor:
                # Crea la tabella se non esiste
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id SERIAL PRIMARY KEY,
                        lead_id INTEGER REFERENCES leads(id),
                        user_id VARCHAR(100) NOT NULL,
                        action VARCHAR(50) NOT NULL,
                        old_data JSONB,
                        new_data JSONB,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Inserisci il log
                cursor.execute(
                    """
                    INSERT INTO audit_log (lead_id, user_id, action, old_data, new_data)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (lead_id, user_id, action, 
                     json.dumps(old_data) if old_data else None, 
                     json.dumps(new_data) if new_data else None)
                )

                conn.commit()
                return True
        except Exception as e:
            log.error(f"❌ Errore nella registrazione dell'audit trail: {str(e)}")
            if 'conn' in locals() and conn:
                conn.rollback()
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()

# Istanza singleton
audit_logger = AuditLogger()