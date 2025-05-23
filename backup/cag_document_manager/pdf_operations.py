"""Operazioni di gestione dei documenti PDF e Markdown."""
import os
import json
from pathlib import Path
from cat.log import log
from .pdf_converter import MathpixConverter

def get_document_by_id(doc_id, documents_dir="/app/cat/shared/documents"):
    """Ottiene un documento dai metadati in base all'ID."""
    try:
        # Carica i metadati
        metadata_path = Path(documents_dir) / "metadata.json"
        if not metadata_path.exists():
            log.error(f"File metadata.json non trovato: {metadata_path}")
            return None
            
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
        # Trova il documento con l'ID specificato
        doc_info = next((f for f in metadata.get("files", []) if f["id"] == doc_id), None)
        
        if not doc_info:
            log.warning(f"⚠️ Documento non trovato: {doc_id}")
            
        return doc_info
    except Exception as e:
        log.error(f"❌ Errore nel recupero del documento {doc_id}: {str(e)}")
        return None

def get_active_documents(documents_dir="/app/cat/shared/documents", rag_only=False, max_priority=5, converti_cag=False):
    """
    Restituisce i documenti attivi.
    
    Args:
        documents_dir: Directory contenente i documenti
        rag_only: Se True, restituisce solo i documenti con priorità RAG
        max_priority: Priorità massima da includere (solo se rag_only=True)
        converti_cag: Se True, restituisce solo i documenti marcati per conversione CAG
    """
    try:
        # Carica i metadati
        metadata_path = Path(documents_dir) / "metadata.json"
        if not metadata_path.exists():
            log.error(f"File metadata.json non trovato: {metadata_path}")
            return []
            
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
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
            
        log.info(f"Trovati {len(active_docs)} documenti attivi" + 
                 (f" con converti_cag=True" if converti_cag else "") +
                 (f" con priorità RAG ≤ {max_priority}" if rag_only else ""))
        return active_docs
    except Exception as e:
        log.error(f"❌ Errore nel recupero dei documenti attivi: {str(e)}")
        return []

def update_document_markdown_path(doc_id, markdown_path, documents_dir="/app/cat/shared/documents"):
    """Aggiorna il percorso del file markdown nei metadati del documento."""
    try:
        # Carica i metadati
        metadata_path = Path(documents_dir) / "metadata.json"
        if not metadata_path.exists():
            log.error(f"File metadata.json non trovato: {metadata_path}")
            return False
            
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Trova l'indice del documento
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
            relative_path = os.path.relpath(markdown_path, documents_dir)
        else:
            relative_path = markdown_path
            
        # Aggiorna il percorso nel metadata
        metadata["files"][doc_idx]["markdown_path"] = relative_path
        log.info(f"Aggiornato percorso markdown per {doc_id}: {relative_path}")
        
        # Salva i metadati
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
            
        return True
    except Exception as e:
        log.error(f"❌ Errore nell'aggiornamento del percorso markdown: {str(e)}")
        return False

def convert_document_to_markdown(doc_id, settings=None):
    """Converte un documento in markdown usando Mathpix."""
    try:
        documents_dir = settings.get("documents_dir", "/app/cat/shared/documents") if settings else "/app/cat/shared/documents"
        
        # Ottieni le credenziali Mathpix
        mathpix_app_id = os.environ.get("MATHPIX_APP_ID")
        mathpix_app_key = os.environ.get("MATHPIX_APP_KEY")
        
        if not mathpix_app_id or not mathpix_app_key:
            log.error("❌ Credenziali Mathpix non trovate nelle variabili d'ambiente")
            return None
        
        # Ottieni il documento dai metadati
        doc_info = get_document_by_id(doc_id, documents_dir)
        if not doc_info:
            log.error(f"❌ Documento non trovato: {doc_id}")
            return None
        
        # Controlla se esiste già il markdown e non è richiesto il force
        if doc_info.get("markdown_path"):
            markdown_path = Path(documents_dir) / doc_info["markdown_path"]
            if os.path.exists(markdown_path):
                log.info(f"File markdown già esistente per {doc_id}: {markdown_path}")
                return markdown_path
            
        # Costruisci i percorsi
        pdf_path = Path(documents_dir) / doc_info["path"]
        markdown_dir = Path(documents_dir) / "markdown"
        os.makedirs(markdown_dir, exist_ok=True)
        
        # Verifica che il PDF esista
        if not os.path.exists(pdf_path):
            log.error(f"❌ File PDF non trovato: {pdf_path}")
            return None
        
        log.info(f"📄 Convertendo PDF: {pdf_path}")
        
        # Inizializza il convertitore
        converter = MathpixConverter(mathpix_app_id, mathpix_app_key)
        
        # Converti il PDF
        result = converter.convert_pdf(pdf_path, markdown_dir)
        
        if not result["success"]:
            log.error(f"❌ Errore nella conversione: {result.get('error')}")
            return None
        
        # Aggiorna i metadati con il percorso del markdown
        update_document_markdown_path(doc_id, result["markdown_path"], documents_dir)
        
        return result["markdown_path"]
    except Exception as e:
        log.error(f"❌ Errore nella conversione del documento: {str(e)}")
        return None

def convert_all_active_documents(settings=None, converti_cag=True):
    """Converte tutti i documenti attivi in markdown."""
    try:
        documents_dir = settings.get("documents_dir", "/app/cat/shared/documents") if settings else "/app/cat/shared/documents"
        
        # Utilizza il nuovo parametro converti_cag
        active_docs = get_active_documents(documents_dir, converti_cag=converti_cag)
        
        results = {
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        log.info(f"Avvio conversione batch di {len(active_docs)} documenti" + 
                 (" marcati per conversione CAG" if converti_cag else ""))
        
        # Resto della funzione invariato...
        for doc in active_docs:
            doc_id = doc["id"]
            
            try:
                # Verifica se il documento è già stato convertito
                if doc.get("markdown_path"):
                    markdown_path = Path(documents_dir) / doc["markdown_path"]
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
                markdown_path = convert_document_to_markdown(doc_id, {"documents_dir": documents_dir})
                
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
    except Exception as e:
        log.error(f"❌ Errore generale nella conversione batch: {str(e)}")
        return {
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": [{"status": "error", "message": str(e)}]
        }