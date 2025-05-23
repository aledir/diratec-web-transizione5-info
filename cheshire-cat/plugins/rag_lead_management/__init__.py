"""
Plugin per la gestione dei lead di Transizione 5.0.
Implementa controlli di sicurezza per prevenire abusi e limitare le risposte al solo argomento Transizione 5.0.
"""
from cat.mad_hatter.decorators import plugin
from cat.log import log
import os
import json

# Carica la configurazione
CONFIG_PATH = os.path.join("/app/cat/shared", "config.json")
config = {}
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    log.info(f"✅ Configurazione caricata da: {CONFIG_PATH}")
except Exception as e:
    log.error(f"❌ Errore nel caricamento della configurazione: {str(e)}")
    config = {
        "assistant": {
            "id": "quinto",
            "displayName": "Quinto",
            "fullTitle": "Quinto - Assistente Transizione 5.0",
            "welcomeMessage": "Ciao! Sono Quinto, l'assistente virtuale specializzato in Transizione 5.0.",
            "description": "Assistente specializzato in Transizione 5.0"
        }
    }
    log.warning(f"⚠️ Utilizzo configurazione di fallback")

@plugin
class LeadManagementPlugin:
    def __init__(self, cat):
        self.cat = cat
        
        # Registra esplicitamente che il plugin è stato caricato
        log.info("🔄 Inizializzazione del plugin RAG Lead Management...")
        
        # Carica impostazioni dal plugin
        from .database_operations import initialize as db_initialize
        from .database_operations import verify_tables_exist

        # Inizializza il gestore degli errori LLM-agnostic
        from .error_handler import apply_error_handling_patches
        log.info("✅ Plugin LeadManagement: gestore errori LLM inizializzato")
        
        # Inizializza controlli di sicurezza
        from .security import security, check_dependencies
        log.info("✅ Modulo di sicurezza inizializzato")
        
        # Esegui verifica dipendenze all'avvio
        check_dependencies()
        
        # Imposta flag in working memory
        cat.working_memory["transizione5_only"] = True
        cat.working_memory["strict_content_policy"] = True
        
        # Carica il messaggio di benvenuto dalla configurazione
        welcome_message = config.get("assistant", {}).get("welcomeMessage", 
            "Benvenuto! Sono l'assistente virtuale di Transizione 5.0. Come posso aiutarti oggi?")
        cat.working_memory["welcome_message"] = welcome_message
        log.info("✅ Messaggio di benvenuto caricato dalla configurazione")
        
        # Usa direttamente le variabili d'ambiente se disponibili
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
                raise ValueError("❌ Tabelle necessarie non trovate nel database. Verifica lo script di inizializzazione.")
        
        # Test esplicito del sistema RAG
        test_query = "credito imposta transizione"
        log.info(f"🔍 Test RAG con query: '{test_query}'")
        memories = cat.retrieval(test_query, k=3)
        if memories and len(memories) > 0:
            log.info(f"✅ RAG test: trovati {len(memories)} documenti")
            for i, memory in enumerate(memories):
                meta = "N/A"
                if hasattr(memory[0], "metadata"):
                    meta = str(memory[0].metadata.get("titolo", "N/A"))
                log.info(f"📄 Documento {i+1}: {meta} (score: {memory[1]})")
        else:
            raise ValueError("⚠️ RAG test: nessun documento trovato")
        
        log.info("✅ Plugin LeadManagement inizializzato con successo con controlli di sicurezza attivi")