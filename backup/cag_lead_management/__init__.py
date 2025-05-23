"""
Plugin per la gestione dei lead con approccio CAG per Transizione 5.0.
Versione semplificata che sfrutta la KV-cache fornita da cag_document_manager.
"""
from cat.mad_hatter.decorators import plugin
from cat.log import log

@plugin
class LeadManagementCAGPlugin:
    def __init__(self, cat):
        self.cat = cat
        
        # Importa le dipendenze necessarie
        try:
            from .database_operations import initialize as db_initialize
            from .database_operations import verify_tables_exist
            from .security import security, check_dependencies
            
            # Inizializza moduli di sicurezza
            log.info("✅ Modulo di sicurezza inizializzato (CAG Lead Management)")
            
            # Esegui verifica dipendenze all'avvio
            check_dependencies()
            
            # Imposta flag in working memory
            cat.working_memory["transizione5_only"] = True
            cat.working_memory["strict_content_policy"] = True
            cat.working_memory["using_cag_mode"] = True
            
            # Usa direttamente le variabili d'ambiente
            import os
            
            # Carica impostazioni database
            settings = self.cat.mad_hatter.get_plugin_settings("Lead Management")
            if settings:
                db_config = {
                    "host": os.environ.get("POSTGRES_HOST", settings.get("db_host", "postgres")),
                    "port": os.environ.get("POSTGRES_PORT", settings.get("db_port", "5432")),
                    "database": os.environ.get("POSTGRES_DB", settings.get("db_name", "diratec_leads")),
                    "user": os.environ.get("POSTGRES_USER", settings.get("db_user", "diratec_user")),
                    "password": os.environ.get("POSTGRES_PASSWORD", settings.get("db_password", "securepassword"))
                }
                # Inizializza la configurazione del database
                db_initialize(db_config)
                
                # Verifica le tabelle (non tenta di crearle)
                tables_exist = verify_tables_exist()
                if tables_exist:
                    log.info("✅ Tabelle del database verificate con successo")
                else:
                    log.error("❌ Tabelle necessarie non trovate nel database. Verifica lo script di inizializzazione.")
            
            # Verifica che il plugin cag_document_manager sia attivo
            cag_document_manager_active = self._check_cag_document_manager_active()
            if not cag_document_manager_active:
                log.warning("⚠️ Plugin cag_document_manager non rilevato. Alcune funzionalità potrebbero essere limitate.")
                
            # Avvia task in background
            self._start_background_tasks()
            
            log.info("✅ Plugin CAG Lead Management inizializzato con successo")
            
        except Exception as e:
            log.error(f"❌ Errore nell'inizializzazione di CAG Lead Management: {str(e)}")
    
    def _check_cag_document_manager_active(self):
        """Verifica se il plugin cag_document_manager è attivo."""
        try:
            # Controlla se il plugin è caricato
            plugins = self.cat.mad_hatter.plugins
            for plugin_name in plugins:
                if plugin_name.lower() == "cag document manager":
                    return True
            
            return False
        except Exception as e:
            log.error(f"❌ Errore nel controllo di cag_document_manager: {str(e)}")
            return False
    
    def _start_background_tasks(self):
        """Avvia task in background per la manutenzione del sistema."""
        try:
            import threading
            import time
            
            def security_maintenance_task():
                """Task di manutenzione sicurezza in background"""
                log.info("🔄 Avvio task di manutenzione sicurezza (CAG Lead Management)")
                
                try:
                    # Importa i moduli necessari
                    from .security import check_dependencies, session_manager, rate_limiter
                    
                    while True:
                        try:
                            # Verifica le dipendenze ogni 24 ore
                            check_dependencies()
                            
                            # Pulisci le sessioni scadute
                            if hasattr(session_manager, 'clean_expired_sessions'):
                                cleaned = session_manager.clean_expired_sessions()
                                if cleaned > 0:
                                    log.info(f"🧹 Pulite {cleaned} sessioni scadute")
                            
                            # Pulisci le cache di rate limiting
                            if hasattr(rate_limiter, 'clear_cache'):
                                cleared = rate_limiter.clear_cache(older_than_minutes=120)
                                if cleared > 0:
                                    log.info(f"🧹 Puliti {cleared} elementi dalla cache di rate limiting")
                        except Exception as e:
                            log.error(f"❌ Errore nel task di manutenzione: {str(e)}")
                        
                        # Dormi per 12 ore
                        time.sleep(12 * 60 * 60)
                except Exception as e:
                    log.error(f"❌ Errore generale nel task di manutenzione: {str(e)}")
            
            # Avvia il thread di manutenzione
            maintenance_thread = threading.Thread(target=security_maintenance_task, daemon=True)
            maintenance_thread.start()
            log.info("✅ Task di manutenzione sicurezza avviato (CAG Lead Management)")
        except Exception as e:
            log.error(f"❌ Errore nell'avvio del task di manutenzione: {str(e)}")