"""Operazioni base per la gestione dei documenti e dei metadati."""
import json
import os
from pathlib import Path
from cat.log import log

# Percorsi dei file
DOCUMENTS_DIR = Path("/app/cat/shared")
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
        if not METADATA_PATH.exists():
            error_msg = f"ERRORE CRITICO: Il file metadata.json non esiste in {METADATA_PATH}"
            log.error(f"❌ {error_msg}")
            # Potremmo anche sollevare un'eccezione se questo è realmente critico
            # raise FileNotFoundError(error_msg)
            
            # In alternativa, loghiamo l'errore ma restituiamo una struttura vuota
            # indicando chiaramente che si tratta di una fallback di emergenza
            log.error("❌ Restituendo struttura vuota di emergenza - Il sistema non funzionerà correttamente!")
            return {"files": [], "categorie": [], "tipi": [], "error": "File metadata.json mancante"}
        
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            active_docs = [f for f in data.get("files", []) if f.get("stato") == "attivo"]
            log.info(f"Metadati letti con successo: {len(data.get('files', []))} documenti totali, {len(active_docs)} attivi")
            return data
    except Exception as e:
        log.error(f"Errore nella lettura del file metadata.json: {str(e)}")
        return {"files": [], "categorie": [], "tipi": []}

def save_metadata(metadata):
    """Salva il file dei metadati"""
    try:
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
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
    if doc_info is None:
        log.warning(f"⚠️ Documento non trovato: '{doc_id}'")
        # Potremmo anche aggiungere più dettagli sul contesto
        log.warning(f"IDs disponibili: {[f['id'] for f in metadata.get('files', [])]}")
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
        doc_idx = next((i for i, doc in enumerate(metadata.get("files", [])) if doc["id"] == doc_id), None)
        
        if doc_idx is None:
            log.error(f"Documento non trovato: {doc_id}")
            return False
        
        # Converte il percorso assoluto in percorso relativo alla directory dei documenti
        if isinstance(markdown_path, Path):
            markdown_path = str(markdown_path)
            
        # Se il percorso è assoluto, converti in relativo
        # Assicuriamoci che il percorso sia gestito correttamente
        if os.path.isabs(markdown_path):
            # Verifichiamo che il percorso sia all'interno della directory dei documenti
            if not os.path.commonpath([markdown_path, str(DOCUMENTS_DIR)]) == str(DOCUMENTS_DIR):
                error_msg = f"Percorso markdown {markdown_path} è al di fuori della directory dei documenti {DOCUMENTS_DIR}"
                log.error(f"❌ {error_msg}")
                return False
            
            relative_path = os.path.relpath(markdown_path, DOCUMENTS_DIR)
            log.info(f"Convertito percorso assoluto in relativo: {markdown_path} → {relative_path}")
        else:
            relative_path = markdown_path
            # Verifica che il percorso relativo punta effettivamente a un file esistente
            full_path = os.path.join(DOCUMENTS_DIR, relative_path)
            if not os.path.exists(full_path):
                log.warning(f"⚠️ Il file markdown {full_path} non esiste - Aggiornando comunque i metadati")
            
        # Aggiorna il percorso nel metadata
        metadata["files"][doc_idx]["markdown_path"] = relative_path
        log.info(f"Aggiornato percorso markdown per {doc_id}: {relative_path}")
        
        return save_metadata(metadata)
    except Exception as e:
        log.error(f"Errore nell'aggiornamento del percorso markdown: {str(e)}")
        return False

def get_active_documents(rag_only=False, max_priority=5, converti_cag=False):
    """
    Restituisce i documenti attivi
    
    Args:
        rag_only: Se True, restituisce solo i documenti con priorità RAG
        max_priority: Priorità massima da includere (solo se rag_only=True)
        converti_cag: Se True, restituisce solo i documenti marcati per conversione CAG
    """
    metadata = read_metadata()
    
    # Filtro base: solo documenti attivi
    active_docs = [f for f in metadata.get("files", []) if f.get("stato") == "attivo"]
    
    # Aggiunge filtro per documenti da convertire per CAG
    if converti_cag:
        active_docs = [f for f in active_docs if f.get("converti_cag", False) == True]
    
    # Aggiunge filtro per priorità RAG se richiesto
    if rag_only:
        active_docs = [f for f in active_docs 
                      if f.get("priorita_rag") is not None 
                      and f.get("priorita_rag") <= max_priority]
        
    return active_docs

def save_uuid_mapping(doc_id, uuid):
    """Salva la mappatura tra ID documento e UUID nella memoria vettoriale"""
    try:
        # Assicurati che la directory esista
        os.makedirs(os.path.dirname(UUID_MAP_PATH), exist_ok=True)
        
        # Carica la mappa UUID esistente o crea una nuova
        uuid_map = {}
        if os.path.exists(UUID_MAP_PATH):
            try:
                with open(UUID_MAP_PATH, "r", encoding="utf-8") as f:
                    uuid_map = json.load(f)
            except json.JSONDecodeError:
                log.error(f"❌ File UUID_MAP_PATH corrotto, creazione di una nuova mappa")
                uuid_map = {}
        
        # Aggiorna la mappa
        uuid_map[doc_id] = uuid
        
        # Scrivi la mappa aggiornata
        with open(UUID_MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(uuid_map, f, indent=2)
        
        log.info(f"✅ Mappatura UUID salvata per il documento '{doc_id}': {uuid}")
        return True
    except Exception as e:
        log.error(f"❌ Errore nel salvataggio della mappatura UUID: {str(e)}")
        # Log di debug più dettagliati
        try:
            log.error(f"❌ Percorso file: {UUID_MAP_PATH}")
            log.error(f"❌ Esiste directory: {os.path.exists(os.path.dirname(UUID_MAP_PATH))}")
            log.error(f"❌ Permessi directory: {oct(os.stat(os.path.dirname(UUID_MAP_PATH)).st_mode)}")
            if os.path.exists(UUID_MAP_PATH):
                log.error(f"❌ Permessi file: {oct(os.stat(UUID_MAP_PATH).st_mode)}")
        except Exception as debug_error:
            log.error(f"❌ Errore nel debug: {str(debug_error)}")
        return False

def get_uuid_mapping(doc_id):
    """Ottiene l'UUID memorizzato per un determinato ID di documento"""
    try:
        if UUID_MAP_PATH.exists():
            with open(UUID_MAP_PATH, "r", encoding="utf-8") as f:
                uuid_map = json.load(f)
            return uuid_map.get(doc_id)
    except Exception as e:
        log.error(f"❌ Errore nella lettura della mappatura UUID: {str(e)}")
    return None

def delete_uuid_mapping(doc_id):
    """Elimina la mappatura UUID per un documento"""
    try:
        if UUID_MAP_PATH.exists():
            with open(UUID_MAP_PATH, "r", encoding="utf-8") as f:
                uuid_map = json.load(f)
            
            if doc_id in uuid_map:
                del uuid_map[doc_id]
                
                with open(UUID_MAP_PATH, "w", encoding="utf-8") as f:
                    json.dump(uuid_map, f, indent=2)
                
                log.info(f"✅ Mappatura UUID eliminata per il documento '{doc_id}'")
                return True
    except Exception as e:
        log.error(f"❌ Errore nell'eliminazione della mappatura UUID: {str(e)}")
    return False

def get_all_uuid_mappings():
    """Ottiene tutte le mappature UUID"""
    try:
        if UUID_MAP_PATH.exists():
            with open(UUID_MAP_PATH, "r", encoding="utf-8") as f:
                uuid_map = json.load(f)
            return uuid_map
        else:
            log.warning(f"⚠️ File mappatura UUID non trovato: {UUID_MAP_PATH}")
            return {}
    except Exception as e:
        log.error(f"❌ Errore nella lettura delle mappature UUID: {str(e)}")
        return {}