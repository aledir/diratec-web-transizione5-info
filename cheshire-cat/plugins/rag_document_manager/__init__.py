"""
Plugin per la gestione dei documenti di Transizione 5.0.
Implementa il flusso di lavoro:
1. Conversione PDF → Markdown con Mathpix (solo documenti con converti_cag=True)
2. Pulizia manuale dei file Markdown con clean_markers.py
3. Inserimento nel RAG dei documenti Markdown generati
"""
import os
import json
from pathlib import Path
from cat.mad_hatter.decorators import plugin
from cat.log import log

from .document_operations import initialize, set_plugin_settings

def ensure_directories_exist(documents_dir="/app/cat/shared"):
    """Crea le directory necessarie e i file essenziali se non esistono"""
    documents_dir = Path(documents_dir)
    metadata_path = documents_dir / "metadata.json"
    uuid_map_path = documents_dir / ".uuid_map.json"
    
    # Crea le directory necessarie
    os.makedirs(documents_dir, exist_ok=True)
    os.makedirs(documents_dir / "markdown", exist_ok=True)
    
    # Crea un file metadata.json vuoto se non esiste
    if not metadata_path.exists():
        error_msg = f"ERRORE CRITICO: File metadata.json non trovato in {metadata_path}"
        log.error(f"❌ {error_msg}")
        log.error("❌ Creazione di un file metadata.json vuoto - questo è per emergenza!")
        
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
        log.warning(f"⚠️ File .uuid_map.json non trovato in {uuid_map_path}")
        with open(uuid_map_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
        log.info(f"✅ Creato file .uuid_map.json vuoto in {uuid_map_path}")
    
    return documents_dir

@plugin
class DocumentManager:
    def __init__(self, cat):
        self.cat = cat
        
        # Carica impostazioni dal plugin
        plugin_settings = self.cat.mad_hatter.get_plugin_settings("RAG Document Manager")
        
        if plugin_settings:
            # Usa le impostazioni per configurare il plugin
            documents_dir = plugin_settings.get("documents_dir")
            
            # Assicura che Mathpix sia configurato
            mathpix_app_id = plugin_settings.get("mathpix_app_id") or os.environ.get("MATHPIX_APP_ID")
            mathpix_app_key = plugin_settings.get("mathpix_app_key") or os.environ.get("MATHPIX_APP_KEY")
            
            if not mathpix_app_id or not mathpix_app_key:
                log.error("❌ ERRORE CRITICO: Credenziali Mathpix non configurate!")
                log.error("❌ La funzionalità di conversione PDF→Markdown non sarà disponibile")
                log.error("❌ Configura MATHPIX_APP_ID e MATHPIX_APP_KEY nelle impostazioni del plugin o nelle variabili d'ambiente")
            
            # Assicura che le directory necessarie esistano
            if documents_dir:
                prepared_dir = ensure_directories_exist(documents_dir)
                initialize(prepared_dir)
                log.info(f"✅ Directory documenti configurata: {prepared_dir}")
            else:
                log.warning("⚠️ Directory documenti non configurata, utilizzo valore predefinito")
                prepared_dir = ensure_directories_exist()
                initialize(prepared_dir)
            
            # Passa le impostazioni al modulo document_operations
            plugin_settings["properly_configured"] = True
            set_plugin_settings(plugin_settings)
            
            # Log di riepilogo impostazioni
            log.info("✅ Impostazioni plugin caricate:")
            log.info(f"📁 Directory documenti: {prepared_dir}")
            log.info(f"🔑 Mathpix configurato: {bool(mathpix_app_id and mathpix_app_key)}")
            
        else:
            # Segnalare un errore più grave per impostazioni mancanti
            log.error("❌ ERRORE CRITICO: Impostazioni del plugin non trovate!")
            log.error("❌ La funzionalità di conversione PDF→Markdown non sarà disponibile")
            log.error("❌ Assicurati di configurare il plugin nelle impostazioni di Cheshire Cat")
            
            # Continuiamo comunque l'inizializzazione, ma con un avviso molto visibile
            prepared_dir = ensure_directories_exist()
            initialize(prepared_dir)
            
            # Crea impostazioni vuote con flag che indica la configurazione incompleta
            plugin_settings = {
                "mathpix_app_id": os.environ.get("MATHPIX_APP_ID", ""),
                "mathpix_app_key": os.environ.get("MATHPIX_APP_KEY", ""),
                "properly_configured": False  # Flag che indica configurazione incompleta
            }
            set_plugin_settings(plugin_settings)
        
        # Verifica finale dello stato del plugin
        if not plugin_settings.get("mathpix_app_id") or not plugin_settings.get("mathpix_app_key"):
            log.error("❌ Credenziali Mathpix mancanti! La conversione PDF→Markdown NON funzionerà!")
        else:
            log.info("✅ Credenziali Mathpix trovate, la conversione PDF→Markdown dovrebbe funzionare")
        
        # Riepilogo inizializzazione
        log.info("✅ Plugin RAG Document Manager inizializzato")
        
        # Verifica consistenza del sistema
        try:
            from .rag_utils import verify_rag_consistency
            log.info("🔄 Verifica consistenza del sistema RAG...")
            consistency = verify_rag_consistency(self.cat, prepared_dir)
            
            # Loghiamo i risultati della verifica
            log.info(f"📊 Documenti totali: {consistency.get('total_documents', 0)}")
            log.info(f"📊 Documenti con markdown: {consistency.get('documents_with_markdown', 0)}")
            log.info(f"📊 Documenti con UUID: {consistency.get('documents_with_uuid', 0)}")
            
            # Avvisi per inconsistenze
            if consistency.get('missing_markdown_files'):
                log.warning(f"⚠️ {len(consistency.get('missing_markdown_files'))} file markdown mancanti")
            
            if consistency.get('missing_uuid_mappings'):
                log.warning(f"⚠️ {len(consistency.get('missing_uuid_mappings'))} mappature UUID mancanti")
            
            if consistency.get('inconsistent_documents'):
                log.warning(f"⚠️ {len(consistency.get('inconsistent_documents'))} documenti inconsistenti")
            
            if consistency.get('orphaned_uuids'):
                log.warning(f"⚠️ {len(consistency.get('orphaned_uuids'))} UUID orfani")
                
        except Exception as e:
            log.error(f"❌ Errore nella verifica della consistenza: {str(e)}")