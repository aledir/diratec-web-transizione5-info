"""Endpoints API per il plugin."""
from cat.mad_hatter.decorators import endpoint
from cat.auth.permissions import check_permissions
from cat.log import log
from pathlib import Path
import os

# Importa le operazioni e funzioni necessarie
from .document_operations import (
    get_document_by_id, get_active_documents, update_document_markdown_path,
    get_plugin_settings, DOCUMENTS_DIR, read_metadata
)
from .pdf_converter import MathpixConverter
from .rag_utils import insert_markdown_into_rag, insert_all_markdown_into_rag, delete_document_from_memory

@endpoint.get("/rag/documents/remove-from-rag/{doc_id}")
def remove_document_from_rag_endpoint(doc_id: str, cat=check_permissions("MEMORY", "WRITE")):
    """Endpoint per rimuovere un documento dal RAG"""
    try:
        log.info(f"🗑️ Richiesta di rimozione del documento '{doc_id}' dal RAG")
        
        # Verifica che il documento esista
        doc_info = get_document_by_id(doc_id)
        if not doc_info:
            return {
                "success": False,
                "error": f"Documento non trovato: {doc_id}",
                "status": 404
            }
        
        # Rimozione dalla memoria - passa cat
        delete_result = delete_document_from_memory(doc_id, cat)
        
        # Verifica se il risultato è un dizionario (indicazione di errore)
        if isinstance(delete_result, dict) and delete_result.get("success") is False:
            return {
                "success": False,
                "error": delete_result.get("error", "Errore nella rimozione del documento"),
                "status": 400
            }
        elif delete_result is True:
            return {
                "success": True,
                "message": f"Documento '{doc_id}' rimosso dal RAG con successo",
                "status": 200
            }
        else:
            return {
                "success": False,
                "error": "Errore nella rimozione del documento",
                "status": 500
            }
    except Exception as e:
        error_msg = f"Errore nella rimozione del documento dal RAG: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }

@endpoint.get("/rag/documents/convert/{doc_id}")
def convert_document_endpoint(doc_id: str, cat=check_permissions("MEMORY", "WRITE")):
    """Endpoint per convertire un documento in markdown"""
    try:
        log.info(f"📄 Richiesta di conversione del documento '{doc_id}' in markdown")
        
        # Verifica che il documento esista
        doc_info = get_document_by_id(doc_id)
        if not doc_info:
            return {
                "success": False,
                "error": f"Documento non trovato: {doc_id}",
                "status": 404
            }
        
        # Prepara i risultati
        results = {
            "success": True,
            "document_id": doc_id,
            "title": doc_info.get("titolo", ""),
            "status": 200
        }
        
        # Controlla se esiste già un file markdown
        if doc_info.get("markdown_path"):
            markdown_path = Path(DOCUMENTS_DIR) / doc_info["markdown_path"]
            if markdown_path.exists():
                log.info(f"File markdown già esistente: {markdown_path}")
                # Non aggiornare i metadati, solo riporta che è stato saltato
                results["skipped"] = True
                results["message"] = "File markdown già esistente"
                results["path"] = str(markdown_path)
                return results
        
        # Costruisci i percorsi
        pdf_path = Path(DOCUMENTS_DIR) / doc_info["path"]
        markdown_dir = Path(DOCUMENTS_DIR) / "markdown"
        os.makedirs(markdown_dir, exist_ok=True)
        
        # Verifica che il PDF esista
        if not os.path.exists(pdf_path):
            log.error(f"❌ File PDF non trovato: {pdf_path}")
            return {
                "success": False,
                "error": f"File PDF non trovato: {pdf_path}",
                "status": 404
            }
        
        # Ottieni le credenziali Mathpix
        settings = get_plugin_settings()
        mathpix_app_id = settings.get("mathpix_app_id") or os.environ.get("MATHPIX_APP_ID")
        mathpix_app_key = settings.get("mathpix_app_key") or os.environ.get("MATHPIX_APP_KEY")
        
        if not mathpix_app_id or not mathpix_app_key:
            return {
                "success": False,
                "error": "Credenziali Mathpix non configurate",
                "status": 500
            }
        
        # Inizializza il convertitore
        converter = MathpixConverter(mathpix_app_id, mathpix_app_key)
        
        # Converti il PDF
        result = converter.convert_pdf(pdf_path, markdown_dir)
        
        if not result["success"]:
            log.error(f"❌ Errore nella conversione: {result.get('error')}")
            return {
                "success": False,
                "error": f"Errore nella conversione: {result.get('error')}",
                "status": 500
            }
        
        # Aggiorna i metadati con il percorso del markdown
        update_document_markdown_path(doc_id, result["markdown_path"])
        
        # Aggiorna i risultati
        results["converted"] = True
        results["path"] = str(result["markdown_path"])
        results["message"] = "Documento convertito con successo"
        
        return results
    except Exception as e:
        error_msg = f"Errore nella conversione del documento: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }
    
@endpoint.get("/rag/documents/convert-cag")
def convert_cag_documents_endpoint(cat=check_permissions("MEMORY", "WRITE")):
    """Endpoint per convertire tutti i documenti marcati con converti_cag=True"""
    try:
        log.info(f"📄 Richiesta di conversione dei documenti con converti_cag=True")
        
        # Ottieni i documenti attivi con converti_cag=True
        cag_docs = get_active_documents(converti_cag=True)
        
        if not cag_docs:
            return {
                "success": True,
                "message": "Nessun documento con converti_cag=True trovato",
                "converted": 0,
                "failed": 0,
                "details": [],
                "status": 200
            }
        
        # Ottieni le credenziali Mathpix
        settings = get_plugin_settings()
        mathpix_app_id = settings.get("mathpix_app_id") or os.environ.get("MATHPIX_APP_ID")
        mathpix_app_key = settings.get("mathpix_app_key") or os.environ.get("MATHPIX_APP_KEY")
        
        if not mathpix_app_id or not mathpix_app_key:
            return {
                "success": False,
                "error": "Credenziali Mathpix non configurate",
                "status": 500
            }
        
        # Inizializza il convertitore
        converter = MathpixConverter(mathpix_app_id, mathpix_app_key)
        
        # Prepara la directory per i file markdown
        markdown_dir = Path(DOCUMENTS_DIR) / "markdown"
        os.makedirs(markdown_dir, exist_ok=True)
        
        results = {
            "converted": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        # Converti ogni documento
        for doc in cag_docs:
            doc_id = doc["id"]
            
            try:
                # Controlla se esiste già un file markdown
                if doc.get("markdown_path"):
                    markdown_path = Path(DOCUMENTS_DIR) / doc["markdown_path"]
                    if markdown_path.exists():
                        results["skipped"] += 1
                        results["details"].append({
                            "id": doc_id,
                            "status": "skipped",
                            "message": "File markdown già esistente",
                            "path": str(markdown_path)
                        })
                        continue
                
                # Costruisci il percorso del PDF
                pdf_path = Path(DOCUMENTS_DIR) / doc["path"]
                
                # Verifica che il PDF esista
                if not pdf_path.exists():
                    results["failed"] += 1
                    results["details"].append({
                        "id": doc_id,
                        "status": "failed",
                        "message": f"File PDF non trovato: {pdf_path}"
                    })
                    continue
                
                # Converti il PDF
                log.info(f"🔄 Conversione documento '{doc_id}' - File: {pdf_path}")
                result = converter.convert_pdf(pdf_path, markdown_dir)
                
                if result["success"]:
                    # Aggiorna i metadati con il percorso del markdown
                    update_document_markdown_path(doc_id, result["markdown_path"])
                    
                    results["converted"] += 1
                    results["details"].append({
                        "id": doc_id,
                        "status": "success",
                        "path": str(result["markdown_path"]),
                        "from_cache": result.get("from_cache", False)
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "id": doc_id,
                        "status": "failed",
                        "message": result.get("error", "Errore sconosciuto")
                    })
            
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "id": doc_id,
                    "status": "failed",
                    "message": str(e)
                })
                log.error(f"❌ Errore nella conversione di {doc_id}: {str(e)}")
        
        return {
            "success": True,
            "total_documents": len(cag_docs),
            "converted": results["converted"],
            "failed": results["failed"],
            "skipped": results["skipped"],
            "details": results["details"],
            "status": 200
        }
            
    except Exception as e:
        error_msg = f"Errore nella conversione dei documenti CAG: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }

@endpoint.get("/rag/documents/insert-markdown/{doc_id}")
def insert_markdown_endpoint(doc_id: str, cat=check_permissions("MEMORY", "WRITE")):
    """Endpoint per inserire un singolo documento markdown nel RAG"""
    log.info(f"🔄 Richiesta di inserimento del documento markdown '{doc_id}' nel RAG")
    return insert_markdown_into_rag(doc_id, cat)

@endpoint.get("/rag/documents/insert-all-markdown")
def insert_all_markdown_endpoint(cat=check_permissions("MEMORY", "WRITE")):
    """Endpoint per inserire tutti i documenti markdown nel RAG"""
    log.info(f"🔄 Richiesta di inserimento di tutti i documenti markdown nel RAG")
    return insert_all_markdown_into_rag(cat)


#########################################################################################
#
#
# ENDPOINT DI DEBUG
#
#
#########################################################################################

@endpoint.get("/rag/documents/analyze-chunking/{doc_id}")
def analyze_document_chunking_endpoint(doc_id: str, cat=check_permissions("MEMORY", "READ")):
    """Endpoint per analizzare il processo di chunking di un documento specifico"""
    try:
        log.info(f"🔍 Analisi chunking per documento '{doc_id}'")
        
        # Verifica che il documento esista
        doc_info = get_document_by_id(doc_id)
        if not doc_info:
            return {
                "success": False,
                "error": f"Documento non trovato: {doc_id}",
                "status": 404
            }
        
        # Verifica che il documento abbia un percorso markdown
        if not doc_info.get("markdown_path"):
            return {
                "success": False,
                "error": f"Documento senza percorso markdown: {doc_id}",
                "status": 400
            }
        
        # Costruisci il percorso completo del file markdown
        markdown_path = os.path.join(DOCUMENTS_DIR, doc_info["markdown_path"])
        if not os.path.exists(markdown_path):
            return {
                "success": False,
                "error": f"File markdown non trovato: {markdown_path}",
                "status": 404
            }
        
        # Leggi il contenuto del file markdown
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        
        # Statistiche di base sul contenuto
        content_stats = {
            "file_size_bytes": os.path.getsize(markdown_path),
            "content_length": len(markdown_content),
            "lines_count": markdown_content.count('\n') + 1,
            "avg_line_length": len(markdown_content) / (markdown_content.count('\n') + 1) if markdown_content.count('\n') > 0 else len(markdown_content)
        }
        
        # Estrae i parametri di chunking dai metadati
        chunk_size = doc_info.get("chunk_size", 1000)
        chunk_overlap = doc_info.get("chunk_overlap", 200)
        
        # Stima del numero di chunk previsti (un'approssimazione)
        estimated_chunks = max(1, (content_stats["content_length"] - chunk_overlap) / (chunk_size - chunk_overlap))
        
        # Applica le opzioni di pulizia se presenti
        clean_options = doc_info.get("clean_options", {})
        cleaned_content = markdown_content
        
        if clean_options:
            taglia_inizio = clean_options.get("taglia_caratteri_inizio", 0)
            taglia_fine = clean_options.get("taglia_caratteri_fine", 0)
            
            if taglia_inizio > 0:
                cleaned_content = cleaned_content[taglia_inizio:]
            
            if taglia_fine > 0:
                content_length = len(cleaned_content)
                cleaned_content = cleaned_content[:content_length - taglia_fine]
        
        # Statistiche sul contenuto pulito
        cleaned_stats = {
            "content_length": len(cleaned_content),
            "lines_count": cleaned_content.count('\n') + 1,
            "chars_removed": len(markdown_content) - len(cleaned_content),
            "percent_removed": (len(markdown_content) - len(cleaned_content)) / len(markdown_content) * 100 if len(markdown_content) > 0 else 0
        }
        
        # Ora simuliamo il processo di chunking usando la funzione di Cheshire Cat (se possibile)
        actual_chunks = []
        if hasattr(cat.rabbit_hole, 'string_to_docs'):
            try:
                # Usa la stessa funzione che verrebbe usata per il chunking effettivo
                docs = cat.rabbit_hole.string_to_docs(
                    cat=cat,
                    file_bytes=cleaned_content,
                    source=markdown_path,
                    content_type="text/markdown",
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                
                # Ottieni informazioni sui chunk
                for i, doc in enumerate(docs):
                    actual_chunks.append({
                        "index": i,
                        "length": len(doc.page_content),
                        "tokens_estimate": len(doc.page_content.split()) * 1.3,  # stima rozza dei token
                        "first_words": doc.page_content[:50] + "..." if len(doc.page_content) > 50 else doc.page_content
                    })
            except Exception as e:
                log.error(f"❌ Errore nella simulazione chunking: {str(e)}")
                return {
                    "success": False,
                    "error": f"Errore nella simulazione chunking: {str(e)}",
                    "status": 500
                }
        
        # Verifica quanti chunk sono effettivamente memorizzati nel RAG
        rag_chunks = []
        if hasattr(cat.memory, 'vectors') and hasattr(cat.memory.vectors, 'declarative'):
            try:
                # Cerca i chunk per questo documento nel RAG usando metadati
                if hasattr(cat.memory.vectors.declarative, 'search_by_metadata'):
                    search_results = cat.memory.vectors.declarative.search_by_metadata(
                        {"id": doc_id},
                        limit=100  # Un limite ragionevole
                    )
                    
                    # Conta i chunk reali nel RAG
                    if search_results:
                        for result in search_results:
                            rag_chunks.append({
                                "uuid": result.get("id", "unknown"),
                                "text_preview": result.get("text", "")[:50] + "..." if len(result.get("text", "")) > 50 else result.get("text", ""),
                                "source": result.get("source", "unknown")
                            })
            except Exception as e:
                log.error(f"❌ Errore nella ricerca chunk nel RAG: {str(e)}")
        
        # Prepara il risultato complessivo
        result = {
            "success": True,
            "doc_id": doc_id,
            "title": doc_info.get("titolo", ""),
            "path": markdown_path,
            "chunking_params": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap
            },
            "content_stats": content_stats,
            "cleaned_stats": cleaned_stats,
            "chunking_analysis": {
                "estimated_chunks": estimated_chunks, 
                "simulated_chunks": len(actual_chunks),
                "actual_chunks_in_rag": len(rag_chunks)
            },
            "simulated_chunks": actual_chunks,
            "rag_chunks": rag_chunks,
            "status": 200
        }
        
        return result
    
    except Exception as e:
        error_msg = f"Errore nell'analisi del chunking: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }
    

@endpoint.get("/rag/documents/system-status")
def system_status_endpoint(cat=check_permissions("MEMORY", "READ")):
    """Endpoint per verificare lo stato complessivo del sistema RAG"""
    try:
        log.info(f"🔍 Analisi stato complessivo del sistema RAG")
        
        from .rag_utils import verify_rag_consistency
        consistency_results = verify_rag_consistency(cat, DOCUMENTS_DIR)
        
        # Aggiungi statistiche sulla memoria vettoriale
        memory_stats = {}
        if hasattr(cat.memory, 'vectors') and hasattr(cat.memory.vectors, 'declarative'):
            try:
                if hasattr(cat.memory.vectors.declarative, 'count_points'):
                    total_points = cat.memory.vectors.declarative.count_points()
                    memory_stats["total_points"] = total_points
                
                # Conta i documenti per categoria
                if hasattr(cat.memory.vectors.declarative, 'search_by_metadata'):
                    # Ottieni categorie dai metadati
                    metadata = read_metadata()
                    categorie = metadata.get("categorie", [])
                    
                    category_counts = {}
                    for categoria in categorie:
                        try:
                            results = cat.memory.vectors.declarative.search_by_metadata(
                                {"categoria": categoria},
                                limit=1  # Solo per contare
                            )
                            if results:
                                category_counts[categoria] = len(results)
                        except:
                            pass
                    
                    memory_stats["category_counts"] = category_counts
            except Exception as e:
                log.error(f"❌ Errore nel recupero statistiche memoria: {str(e)}")
        
        # Aggiungi statistiche sui file
        file_stats = {
            "total_markdown_files": len(list(Path(DOCUMENTS_DIR).glob("markdown/*.md"))),
            "total_pdf_files": (
                len(list(Path(DOCUMENTS_DIR).glob("normativa/*.pdf"))) +
                len(list(Path(DOCUMENTS_DIR).glob("circolari/*.pdf"))) +
                len(list(Path(DOCUMENTS_DIR).glob("faq/*.pdf"))) +
                len(list(Path(DOCUMENTS_DIR).glob("guide/*.pdf"))) +
                len(list(Path(DOCUMENTS_DIR).glob("modelli/*.pdf")))
            )
        }
        
        # Combinare i risultati
        result = {
            "success": True,
            "consistency": consistency_results,
            "memory_stats": memory_stats,
            "file_stats": file_stats,
            "status": 200
        }
        
        return result
    
    except Exception as e:
        error_msg = f"Errore nell'analisi dello stato del sistema: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }