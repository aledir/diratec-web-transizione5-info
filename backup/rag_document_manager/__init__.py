"""
Plugin per la gestione dei documenti di Transizione 5.0.
Versione semplificata che gestisce solo le operazioni RAG essenziali.
"""
import os
import json
from pathlib import Path
from cat.mad_hatter.decorators import plugin
from cat.log import log

from .document_operations import initialize, set_plugin_settings

def ensure_directories_exist(documents_dir="/app/cat/shared/documents"):
    """Crea le directory necessarie e i file essenziali se non esistono"""
    documents_dir = Path(documents_dir)
    metadata_path = documents_dir / "metadata.json"
    uuid_map_path = documents_dir / ".uuid_map.json"
    
    # Crea le directory necessarie
    os.makedirs(documents_dir, exist_ok=True)
    os.makedirs(documents_dir / "markdown", exist_ok=True)
    
    # Crea un file metadata.json vuoto se non esiste
    if not metadata_path.exists():
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
    
    # Crea un file .uuid_map.json vuoto se non esiste
    if not uuid_map_path.exists():
        with open(uuid_map_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        log.info(f"✅ Creato file .uuid_map.json vuoto in {uuid_map_path}")
    
    return documents_dir

@plugin
class DocumentManager:
    def __init__(self, cat):
        self.cat = cat
        
        # Debug delle variabili d'ambiente
        mathpix_app_id_env = os.environ.get("MATHPIX_APP_ID", "")
        mathpix_app_key_env = os.environ.get("MATHPIX_APP_KEY", "")
        masked_key_env = "***" + mathpix_app_key_env[-4:] if mathpix_app_key_env else ""
        log.info(f"🔍 Debug - Variabili d'ambiente: MATHPIX_APP_ID={mathpix_app_id_env}, MATHPIX_APP_KEY={masked_key_env}")
        
        # Carica impostazioni dal plugin
        plugin_settings = self.cat.mad_hatter.get_plugin_settings("RAG Document Manager")
        log.info(f"🔍 Debug - Plugin settings ottenute: {type(plugin_settings)}")
        
        if plugin_settings:
            # Debug delle impostazioni del plugin
            log.info(f"🔍 Debug - Chiavi disponibili: {plugin_settings.keys() if hasattr(plugin_settings, 'keys') else 'Nessuna'}")
            
            # Leggi i valori specifici per Mathpix
            mathpix_app_id = plugin_settings.get("mathpix_app_id", "")
            mathpix_app_key = plugin_settings.get("mathpix_app_key", "")
            masked_key = "***" + mathpix_app_key[-4:] if mathpix_app_key else ""
            log.info(f"🔍 Debug - Plugin settings: mathpix_app_id={mathpix_app_id}, mathpix_app_key={masked_key}")
            
            # Se le impostazioni dal plugin sono vuote, prova a usare le variabili d'ambiente
            if not mathpix_app_id and mathpix_app_id_env:
                log.info(f"📝 Utilizzo MATHPIX_APP_ID dalla variabile d'ambiente")
                plugin_settings["mathpix_app_id"] = mathpix_app_id_env
            
            if not mathpix_app_key and mathpix_app_key_env:
                log.info(f"📝 Utilizzo MATHPIX_APP_KEY dalla variabile d'ambiente")
                plugin_settings["mathpix_app_key"] = mathpix_app_key_env
            
            # Passa le impostazioni al modulo document_operations
            set_plugin_settings(plugin_settings)
            
            documents_dir = plugin_settings.get("documents_dir")
            if documents_dir:
                # Assicura che le directory necessarie esistano
                prepared_dir = ensure_directories_exist(documents_dir)
                initialize(prepared_dir)
            else:
                # Assicura che le directory predefinite esistano
                prepared_dir = ensure_directories_exist()
                initialize(prepared_dir)
        else:
            # Crea impostazioni dalle variabili d'ambiente
            log.info(f"⚠️ Nessuna impostazione plugin trovata, utilizzo variabili d'ambiente")
            plugin_settings = {
                "mathpix_app_id": mathpix_app_id_env,
                "mathpix_app_key": mathpix_app_key_env
            }
            set_plugin_settings(plugin_settings)
            
            # Assicura che le directory predefinite esistano
            prepared_dir = ensure_directories_exist()
            initialize(prepared_dir)
            
        log.info("✅ Plugin RAG Document Manager inizializzato con successo")