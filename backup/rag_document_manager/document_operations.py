"""Operazioni per la gestione dei documenti e dei metadati."""
import json
import os
from pathlib import Path
from cat.log import log
from .pdf_converter import MathpixConverter

# Percorsi dei file
DOCUMENTS_DIR = Path("/app/cat/shared/documents")
METADATA_PATH = DOCUMENTS_DIR / "metadata.json"
UUID_MAP_PATH = DOCUMENTS_DIR / ".uuid_map.json"

# Variabile globale per le impostazioni
_plugin_settings = {}

def get_plugin_settings():
    """Ottiene le impostazioni del plugin"""
    global _plugin_settings
    return _plugin_settings


def initialize(documents_dir=None):
    """Inizializza i percorsi dei file"""
    global DOCUMENTS_DIR, METADATA_PATH, UUID_MAP_PATH
    
    if documents_dir:
        DOCUMENTS_DIR = Path(documents_dir)
        METADATA_PATH = DOCUMENTS_DIR / "metadata.json"
        UUID_MAP_PATH = DOCUMENTS_DIR / ".uuid_map.json"
    
    log.info(f"📁 DocumentManager - Percorso documenti: {DOCUMENTS_DIR}")
    log.info(f"📄 DocumentManager - Percorso metadata: {METADATA_PATH}")


def set_plugin_settings(settings):
    """Imposta le impostazioni del plugin"""
    global _plugin_settings
    _plugin_settings = settings
    log.info(f"✅ Impostazioni plugin caricate: {_plugin_settings.keys() if isinstance(_plugin_settings, dict) else 'Non disponibili'}")


def read_metadata():
    """Legge il file dei metadati"""
    try:
        log.info(f"Lettura del file metadata.json da: {METADATA_PATH}")
        
        if not DOCUMENTS_DIR.exists():
            log.error(f"La directory {DOCUMENTS_DIR} non esiste!")
            return {"files": [], "categorie": [], "tipi": []}
        
        if not METADATA_PATH.exists():
            log.error(f"Il file metadata.json non esiste in {METADATA_PATH}")
            return {"files": [], "categorie": [], "tipi": []}
        
        with open(METADATA_PATH, "r") as f:
            data = json.load(f)
            active_docs = [f for f in data.get("files", []) if f.get("stato") == "attivo"]
            log.info(f"Metadati letti con successo: {len(data.get('files', []))} documenti totali, {len(active_docs)} attivi e {len(data.get('files', [])) - len(active_docs)} inattivi")
            return data
    except Exception as e:
        log.error(f"Errore nella lettura del file metadata.json: {str(e)}")
        return {"files": [], "categorie": [], "tipi": []}


def save_metadata(metadata):
    """Salva il file dei metadati"""
    try:
        with open(METADATA_PATH, "w") as f:
            json.dump(metadata, f, indent=2)
        log.info(f"Metadati salvati con successo in {METADATA_PATH}")
        return True
    except Exception as e:
        log.error(f"Errore nel salvataggio del file metadata.json: {str(e)}")
        return False


def get_document_by_id(doc_id):
    """Ottiene un documento dai metadati in base all'ID"""
    metadata = read_metadata()
    doc_info = next((f for f in metadata.get("files", []) if f["id"] == doc_id), None)
    return doc_info


def set_document_status(doc_id, status):
    """Imposta lo stato di un documento (attivo/obsoleto)"""
    metadata = read_metadata()
    doc_idx = next((i for i, doc in enumerate(metadata.get("files", [])) if doc["id"] == doc_id), None)
    
    if doc_idx is None:
        log.error(f"Documento non trovato: {doc_id}")
        return False
    
    metadata["files"][doc_idx]["stato"] = status
    return save_metadata(metadata)


def update_document_markdown_path(doc_id, markdown_path):
    """Aggiorna il percorso del file markdown nei metadati del documento"""
    try:
        metadata = read_metadata()
        doc_idx = next((i for i, doc in enumerate(metadata.get("files", [])) 
                        if doc["id"] == doc_id), None)
        
        if doc_idx is None:
            log.error(f"Documento non trovato: {doc_id}")
            return False
        
        # Converte il percorso assoluto in percorso relativo alla directory dei documenti
        if isinstance(markdown_path, Path):
            markdown_path = str(markdown_path)
            
        # Se il percorso è assoluto, converti in relativo
        if os.path.isabs(markdown_path):
            relative_path = os.path.relpath(markdown_path, DOCUMENTS_DIR)
        else:
            relative_path = markdown_path
            
        # Aggiorna il percorso nel metadata
        metadata["files"][doc_idx]["markdown_path"] = relative_path
        log.info(f"Aggiornato percorso markdown per {doc_id}: {relative_path}")
        
        return save_metadata(metadata)
    except Exception as e:
        log.error(f"Errore nell'aggiornamento del percorso markdown: {str(e)}")
        return False


def get_active_documents(rag_only=False, max_priority=5):
    """
    Restituisce i documenti attivi
    
    Args:
        rag_only: Se True, restituisce solo i documenti con priorità RAG
        max_priority: Priorità massima da includere (solo se rag_only=True)
    """
    metadata = read_metadata()
    
    if rag_only:
        # Filtra per documenti con priorità RAG definita e minore/uguale a max_priority
        return [f for f in metadata.get("files", []) 
               if f.get("stato") == "attivo" 
               and f.get("priorita_rag") is not None 
               and f.get("priorita_rag") <= max_priority]
    else:
        # Comportamento originale
        return [f for f in metadata.get("files", []) if f.get("stato") == "attivo"]


def save_uuid_mapping(doc_id, uuid):
    """Salva la mappatura tra ID documento e UUID nella memoria vettoriale"""
    try:
        uuid_map = {}
        if UUID_MAP_PATH.exists():
            with open(UUID_MAP_PATH, "r") as f:
                uuid_map = json.load(f)
        
        uuid_map[doc_id] = uuid
        
        with open(UUID_MAP_PATH, "w") as f:
            json.dump(uuid_map, f, indent=2)
        
        log.info(f"✅ Mappatura UUID salvata per il documento '{doc_id}': {uuid}")
        return True
    except Exception as e:
        log.error(f"❌ Errore nel salvataggio della mappatura UUID: {str(e)}")
        return False


def get_uuid_mapping(doc_id):
    """Ottiene l'UUID memorizzato per un determinato ID di documento"""
    try:
        if UUID_MAP_PATH.exists():
            with open(UUID_MAP_PATH, "r") as f:
                uuid_map = json.load(f)
            return uuid_map.get(doc_id)
    except Exception as e:
        log.error(f"❌ Errore nella lettura della mappatura UUID: {str(e)}")
    return None


def delete_uuid_mapping(doc_id):
    """Elimina la mappatura UUID per un documento"""
    try:
        if UUID_MAP_PATH.exists():
            with open(UUID_MAP_PATH, "r") as f:
                uuid_map = json.load(f)
            
            if doc_id in uuid_map:
                del uuid_map[doc_id]
                
                with open(UUID_MAP_PATH, "w") as f:
                    json.dump(uuid_map, f, indent=2)
                
                log.info(f"✅ Mappatura UUID eliminata per il documento '{doc_id}'")
                return True
    except Exception as e:
        log.error(f"❌ Errore nell'eliminazione della mappatura UUID: {str(e)}")
    return False


# Funzione per convertire un documento
def convert_document_to_markdown(doc_id, force_conversion=False):
    """Converte un documento in markdown usando Mathpix"""
    try:
        # Ottieni le impostazioni Mathpix
        settings = get_plugin_settings()
        log.info(f"🔍 Debug - Settings in convert_document_to_markdown: {settings}")
        
        # Prova anche a leggere direttamente dalle variabili d'ambiente come fallback
        mathpix_app_id = settings.get("mathpix_app_id") or os.environ.get("MATHPIX_APP_ID")
        mathpix_app_key = settings.get("mathpix_app_key") or os.environ.get("MATHPIX_APP_KEY")
        
        # Debug delle credenziali
        masked_key = "***" + mathpix_app_key[-4:] if mathpix_app_key else ""
        log.info(f"🔑 Credenziali Mathpix: ID={mathpix_app_id}, Key={masked_key}")
        
        if not mathpix_app_id or not mathpix_app_key:
            err_msg = "❌ Credenziali Mathpix non configurate"
            log.error(err_msg)
            if not mathpix_app_id:
                log.error("   - MATHPIX_APP_ID non trovato")
            if not mathpix_app_key:
                log.error("   - MATHPIX_APP_KEY non trovato")
            return None
        
        # Inizializza il convertitore
        converter = MathpixConverter(mathpix_app_id, mathpix_app_key)
        
        # Ottieni il documento dai metadati
        doc_info = get_document_by_id(doc_id)
        if not doc_info:
            log.error(f"❌ Documento non trovato: {doc_id}")
            return None
        
        # Controlla se esiste già il markdown e non è richiesto il force
        if not force_conversion and doc_info.get("markdown_path"):
            markdown_path = DOCUMENTS_DIR / doc_info["markdown_path"]
            if os.path.exists(markdown_path):
                log.info(f"File markdown già esistente per {doc_id}: {markdown_path}")
                return markdown_path
            
        # Costruisci i percorsi
        pdf_path = DOCUMENTS_DIR / doc_info["path"]
        markdown_dir = DOCUMENTS_DIR / "markdown"
        os.makedirs(markdown_dir, exist_ok=True)
        
        # Verifica che il PDF esista
        if not os.path.exists(pdf_path):
            log.error(f"❌ File PDF non trovato: {pdf_path}")
            return None
        
        log.info(f"📄 Convertendo PDF: {pdf_path}")
        
        # Converti il PDF
        result = converter.convert_pdf(pdf_path, markdown_dir)
        
        if not result["success"]:
            log.error(f"❌ Errore nella conversione: {result.get('error')}")
            return None
        
        # Aggiorna i metadati con il percorso del markdown
        update_document_markdown_path(doc_id, result["markdown_path"])
        
        return result["markdown_path"]
    except Exception as e:
        log.error(f"❌ Errore nella conversione del documento: {str(e)}")
        import traceback
        log.error(f"Stack trace: {traceback.format_exc()}")
        return None


def convert_all_active_documents(force=False):
    """Converte tutti i documenti attivi in markdown"""
    active_docs = get_active_documents()
    results = {
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "details": []
    }
    
    log.info(f"Avvio conversione batch di {len(active_docs)} documenti attivi")
    
    for doc in active_docs:
        doc_id = doc["id"]
        
        try:
            # Verifica se il documento è già stato convertito
            if not force and doc.get("markdown_path"):
                markdown_path = DOCUMENTS_DIR / doc["markdown_path"]
                if Path(markdown_path).exists():
                    log.info(f"Documento {doc_id} già convertito - Percorso: {markdown_path}")
                    results["skipped"] += 1
                    results["details"].append({
                        "id": doc_id,
                        "status": "skipped",
                        "message": "Già convertito",
                        "path": str(markdown_path)
                    })
                    continue
            
            # Converti il documento
            log.info(f"Conversione documento {doc_id} - Titolo: {doc.get('titolo', '')}")
            markdown_path = convert_document_to_markdown(doc_id, force_conversion=force)
            
            if markdown_path:
                results["success"] += 1
                results["details"].append({
                    "id": doc_id,
                    "status": "success",
                    "path": str(markdown_path)
                })
                log.info(f"✅ Conversione riuscita per {doc_id}")
            else:
                results["failed"] += 1
                results["details"].append({
                    "id": doc_id,
                    "status": "failed",
                    "message": "Errore nella conversione"
                })
                log.error(f"❌ Conversione fallita per {doc_id}")
        
        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "id": doc_id,
                "status": "failed",
                "message": str(e)
            })
            log.error(f"❌ Errore durante la conversione di {doc_id}: {str(e)}")
    
    # Riepilogo finale
    log.info(f"Conversione batch completata: {results['success']} successi, {results['failed']} fallimenti, {results['skipped']} saltati")
    
    return results


def get_documents_with_markdown():
    """Restituisce i documenti che hanno un file markdown associato"""
    all_docs = read_metadata().get("files", [])
    return [doc for doc in all_docs if doc.get("markdown_path")]