"""Endpoints API per il plugin."""
from cat.mad_hatter.decorators import endpoint
from cat.log import log

# Importa le operazioni
from .document_operations import (
    get_document_by_id, 
    set_document_status, 
    get_active_documents,
    convert_document_to_markdown,  # Aggiunta questa importazione
    convert_all_active_documents   # Aggiunta questa importazione
)
from .rag_operations import (
    add_document_to_rag, 
    update_all_documents, 
    delete_document_from_memory
)

@endpoint.get("/api/rag/documents/add-to-rag/{doc_id}")
def add_document_to_rag_endpoint(doc_id: str):
    """Endpoint per aggiungere un singolo documento al RAG"""
    log.info(f"🔄 Richiesta all'endpoint /api/rag/documents/add-to-rag/{doc_id}")
    return add_document_to_rag(doc_id)


@endpoint.get("/api/rag/documents/update-rag")
def update_all_documents_endpoint():
    """Endpoint per aggiornare tutti i documenti attivi nel RAG"""
    log.info(f"🔄 Richiesta all'endpoint /api/rag/documents/update-rag")
    return update_all_documents()


@endpoint.get("/api/rag/documents/remove-from-rag/{doc_id}")
def remove_document_from_rag_endpoint(doc_id: str):
    """Endpoint per rimuovere un documento dal RAG e marcarlo come obsoleto"""
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
        
        # 1. Rimozione dalla memoria
        delete_success = delete_document_from_memory(doc_id)
        
        # 2. Marcatura come obsoleto nei metadati
        status_success = set_document_status(doc_id, "obsoleto")
        
        # Risultato combinato
        if delete_success and status_success:
            return {
                "success": True,
                "message": f"Documento '{doc_id}' rimosso dal RAG e marcato come obsoleto",
                "status": 200
            }
        elif status_success:
            return {
                "success": True,
                "warning": "Documento marcato come obsoleto, ma potrebbero esserci stati problemi nella rimozione dalla memoria",
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
    
@endpoint.get("/api/rag/documents/convert/{doc_id}")
def convert_document_endpoint(doc_id: str):
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
        
        # Converti il documento
        markdown_path = convert_document_to_markdown(doc_id)
        
        if markdown_path:
            return {
                "success": True,
                "document_id": doc_id,
                "title": doc_info.get("titolo", ""),
                "markdown_path": str(markdown_path),
                "status": 200
            }
        else:
            return {
                "success": False,
                "error": "Errore nella conversione del documento",
                "status": 500
            }
    except Exception as e:
        error_msg = f"Errore nella conversione del documento: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }

@endpoint.get("/api/rag/documents/convert-all")
def convert_all_documents_endpoint():
    """Endpoint per convertire tutti i documenti attivi"""
    try:
        log.info(f"📄 Richiesta di conversione di tutti i documenti attivi in markdown")
        
        # Esegui la conversione batch
        results = convert_all_active_documents()
        
        # Aggiungi ulteriori informazioni
        return {
            "success": True,
            "total_documents": results["success"] + results["failed"] + results["skipped"],
            "converted": results["success"],
            "failed": results["failed"],
            "skipped": results["skipped"],
            "details": results["details"],
            "status": 200
        }
    except Exception as e:
        error_msg = f"Errore nella conversione batch dei documenti: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }