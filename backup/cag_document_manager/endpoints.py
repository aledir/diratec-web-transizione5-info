"""Endpoint API per CAG Document Manager."""
import os
from cat.mad_hatter.decorators import endpoint
from cat.log import log
from .context_builder import ContextBuilder
from . import hooks
from .pdf_operations import (
    get_document_by_id,
    convert_document_to_markdown,
    convert_all_active_documents
)

@endpoint.get("/api/cag/regenerate-context")
def regenerate_context():
    try:
        # Ottieni le impostazioni senza usare cat
        documents_dir = "/app/cat/shared/documents"  # Valore predefinito
        context_dir = "/app/cat/shared/documents/context"  # Valore predefinito
        context_file = "cag_context.md"  # Valore predefinito
        
        # Costruisci path completo
        context_path = os.path.join(context_dir, context_file)
        
        # Crea un'istanza di ContextBuilder direttamente
        from .context_builder import ContextBuilder
        context_builder = ContextBuilder(documents_dir, context_path)
        
        # Forza la rigenerazione del contesto
        context = context_builder.build_full_context(force=True)
        
        # Estrai metadati
        metadata = {}
        if context.startswith("<!--"):
            metadata_end = context.find("-->")
            if metadata_end > 0:
                metadata_text = context[4:metadata_end].strip()
                for line in metadata_text.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
        
        # Aggiorna anche la cache nelle hooks se possibile
        try:
            hooks._context_cache = context
        except:
            pass
        
        return {
            "status": "ok",
            "message": "Contesto rigenerato con successo",
            "file_path": context_path,
            "metadata": metadata,
            "context_length": len(context)
        }
    except Exception as e:
        log.error(f"❌ Errore nella rigenerazione del contesto: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
    
@endpoint.get("/api/cag/check-tokens")
def check_tokens():
    """Endpoint per verificare il numero di token nella KV-cache."""
    try:
        # Importazioni necessarie
        import os
        import tiktoken
        
        # Percorsi
        documents_dir = "/app/cat/shared/documents"
        context_dir = "/app/cat/shared/documents/context"
        context_file = "cag_context.md"
        context_path = os.path.join(context_dir, context_file)
        
        # Valori predefiniti
        max_context_tokens = 180000  # Valore predefinito se non disponibile nelle impostazioni
        
        # Verifica che il file esista
        if not os.path.exists(context_path):
            return {
                "status": "warning",
                "message": f"File contesto non trovato: {context_path}",
                "tokens": 0,
                "chars": 0,
                "words": 0
            }
        
        # Carica il contesto
        with open(context_path, "r", encoding="utf-8") as f:
            context = f.read()
        
        # Conta caratteri e parole
        char_count = len(context)
        word_count = len(context.split())
        
        # Stima token (approx)
        estimated_tokens_by_chars = char_count // 4  # ~4 caratteri per token
        estimated_tokens_by_words = int(word_count / 0.75)  # ~0.75 parole per token
        
        # Prova con tiktoken se disponibile
        tiktoken_count = None
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")  # encoding usato da Claude
            tiktoken_count = len(encoding.encode(context))
            estimated_tokens = tiktoken_count
        except ImportError:
            estimated_tokens = max(estimated_tokens_by_chars, estimated_tokens_by_words)
        
        # Verifica se supera il limite
        is_over_limit = estimated_tokens > max_context_tokens
        
        # Stima la percentuale di utilizzo
        usage_percentage = (estimated_tokens / max_context_tokens) * 100
        
        # Prepara info metadati
        metadata = {}
        if context.startswith("<!--"):
            metadata_end = context.find("-->")
            if metadata_end > 0:
                metadata_text = context[4:metadata_end].strip()
                for line in metadata_text.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
        
        return {
            "status": "ok",
            "file_path": context_path,
            "tokens": {
                "estimated": estimated_tokens,
                "tiktoken": tiktoken_count,
                "by_chars": estimated_tokens_by_chars,
                "by_words": estimated_tokens_by_words
            },
            "chars": char_count,
            "words": word_count,
            "limit": max_context_tokens,
            "usage_percentage": round(usage_percentage, 2),
            "is_over_limit": is_over_limit,
            "metadata": metadata
        }
    except Exception as e:
        from cat.log import log
        log.error(f"❌ Errore nella verifica dei token: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

   

@endpoint.get("/api/cag/documents/convert-all")
def convert_all_documents_endpoint():
    """Endpoint per convertire tutti i documenti marcati per conversione CAG"""
    try:
        log.info(f"📄 Richiesta di conversione dei documenti marcati per CAG in markdown")
        
        # Usiamo direttamente le impostazioni predefinite
        settings = {
            "documents_dir": "/app/cat/shared/documents"
        }
        
        # Passiamo converti_cag=True per selezionare solo i documenti marcati
        results = convert_all_active_documents(settings, converti_cag=True)
        
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