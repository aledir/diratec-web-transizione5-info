"""Operazioni sulla memoria RAG."""
import json
import os
from pathlib import Path
from datetime import datetime
import hashlib
import time
from fastapi import FastAPI
from cat.log import log

# Importa le funzioni per la gestione dei metadati
from .document_operations import (
    read_metadata, get_document_by_id, save_uuid_mapping, 
    get_uuid_mapping, delete_uuid_mapping, DOCUMENTS_DIR,
    get_active_documents
)

# Variabile globale per l'istanza di CheshireCat
_cat_instance = None

def get_cat_instance():
    """Ottiene una singola istanza di CheshireCat o StrayCat (singleton)"""
    global _cat_instance
    
    if _cat_instance is None:
        try:
            # Metodo 1: Cerca una StrayCat dal contesto della richiesta
            try:
                import inspect
                import sys
                from fastapi import Request
                
                # Ispeziona lo stack delle chiamate per vedere se c'è una richiesta
                frame = inspect.currentframe()
                while frame:
                    args = frame.f_locals
                    # Cerca un oggetto richiesta nei parametri delle funzioni
                    for arg_name, arg_value in args.items():
                        if isinstance(arg_value, Request):
                            # Controlla se la richiesta ha un attributo 'state' che contiene la StrayCat
                            if hasattr(arg_value, 'state') and hasattr(arg_value.state, 'stray_cat'):
                                log.info("✅ Utilizzando StrayCat dall'oggetto richiesta")
                                _cat_instance = arg_value.state.stray_cat
                                return _cat_instance
                    frame = frame.f_back
                
                # Metodo alternativo: cerca nei moduli caricati
                from cat.looking_glass.stray_cat import StrayCat
                for module_name in list(sys.modules.keys()):
                    module = sys.modules[module_name]
                    if hasattr(module, 'stray_cat') and isinstance(module.stray_cat, StrayCat):
                        log.info(f"✅ Trovata istanza StrayCat esistente nel modulo {module_name}")
                        _cat_instance = module.stray_cat
                        return _cat_instance
            except Exception as e:
                log.debug(f"Debug: Tentativo di ottenere StrayCat fallito: {str(e)}")
            
            # Metodo 2: Prova a ottenere CheshireCat dal modulo main
            try:
                import sys
                from cat.looking_glass.cheshire_cat import CheshireCat
                for module_name in list(sys.modules.keys()):
                    module = sys.modules[module_name]
                    if hasattr(module, 'cat') and isinstance(module.cat, CheshireCat):
                        log.info(f"✅ Trovata istanza CheshireCat esistente nel modulo {module_name}")
                        _cat_instance = module.cat
                        break
                
                # Se l'istanza è stata trovata, usala
                if _cat_instance is not None:
                    log.info("✅ Utilizzo istanza CheshireCat già esistente")
                    return _cat_instance
            except Exception as e:
                log.warning(f"⚠️ Impossibile trovare un'istanza CheshireCat esistente: {str(e)}")
            
            # Metodo 3: Prova con approccio diretto
            try:
                # Importa CheshireCat dal path corretto
                from cat.looking_glass.cheshire_cat import CheshireCat
                _cat_instance = CheshireCat.get_instance()
                log.info("✅ Ottenuta istanza CheshireCat tramite get_instance()")
            except Exception as instance_error:
                log.warning(f"⚠️ Impossibile ottenere istanza CheshireCat con get_instance(): {str(instance_error)}")
                
                # Metodo 4: Fallback finale
                try:
                    from cat.looking_glass.cheshire_cat import CheshireCat
                    from fastapi import FastAPI
                    app = FastAPI()
                    _cat_instance = CheshireCat(fastapi_app=app)
                    
                    # Disabilita i messaggi websocket per evitare l'errore
                    if hasattr(_cat_instance, 'send_ws_message'):
                        original_send_ws = _cat_instance.send_ws_message
                        
                        def silent_send_ws_message(*args, **kwargs):
                            try:
                                return original_send_ws(*args, **kwargs)
                            except Exception:
                                # Ignora silenziosamente gli errori websocket
                                return None
                        
                        _cat_instance.send_ws_message = silent_send_ws_message
                    
                    log.info("⚠️ Creata nuova istanza CheshireCat con FastAPI")
                except Exception as final_error:
                    log.error(f"❌ Fallback finale fallito: {str(final_error)}")
                    raise RuntimeError("Impossibile creare istanza CheshireCat")
        except Exception as e:
            error_msg = f"❌ Impossibile ottenere istanza CheshireCat o StrayCat: {str(e)}"
            log.error(error_msg)
            raise RuntimeError(error_msg)
    
    return _cat_instance

def generate_deterministic_uuid(doc_id):
    """Genera un UUID deterministico basato sull'ID del documento"""
    # Crea un UUID deterministico basato sull'ID del documento
    uuid_seed = f"{doc_id}_{int(time.time() / 3600)}"  # Cambia ogni ora
    uuid = hashlib.md5(uuid_seed.encode()).hexdigest()
    return uuid

def add_document_to_rag(doc_id):
    """Aggiunge un singolo documento al RAG"""
    try:
        # 1. Verifica il documento nei metadati
        doc_info = get_document_by_id(doc_id)
        
        if not doc_info:
            return {
                "success": False,
                "error": f"Documento non trovato: {doc_id}",
                "status": 404
            }
        
        # 2. Verifica che sia attivo
        if doc_info["stato"] != "attivo":
            return {
                "success": False, 
                "error": f"Impossibile aggiungere al RAG: documento '{doc_id}' è '{doc_info['stato']}' (non attivo)",
                "status": 400
            }
        
        # 3. Verifica che il file esista
        file_path = DOCUMENTS_DIR / doc_info["path"]
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File non trovato: {file_path}",
                "status": 404
            }
        
        # 4. Rimuovi eventuali versioni precedenti
        old_uuid = get_uuid_mapping(doc_id)
        if old_uuid:
            delete_document_from_memory(doc_id, uuid=old_uuid)
        
        # 5. Parametri di chunking
        file_ext = file_path.suffix.lower()
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / 1024 / 1024
        
        # Imposta parametri di chunking basati sul tipo e dimensione del file
        chunk_size = doc_info.get("chunk_size")
        chunk_overlap = doc_info.get("chunk_overlap")

        log.info(f"🔄 Ingestione documento '{doc_id}' - File: {file_path}")
        log.info(f"📊 Chunking: size={chunk_size}, overlap={chunk_overlap}")
        
        # 6. Crea metadati personalizzati per il documento
        custom_metadata = {
            "id": doc_id,
            "titolo": doc_info["titolo"],
            "categoria": doc_info["categoria"],
            "tipo": doc_info["tipo"],
            "data": doc_info["data"],
            "tags": doc_info.get("tags", []),
            "stato": "attivo",
            "path": str(file_path.relative_to(DOCUMENTS_DIR))
        }
        
        # 7. Ottieni l'istanza di CheshireCat/StrayCat
        cat = get_cat_instance()
        
        # Log dei parametri di ingestione
        log.info(f"🔄 Ingestione documento '{doc_id}' - File: {file_path}")
        log.info(f"📊 Chunking: size={chunk_size}, overlap={chunk_overlap}")
        
        # 8. Genera UUID deterministico prima dell'ingestione
        uuid = generate_deterministic_uuid(doc_id)
        
        # 9. Ingestisci il documento
        chunks_count = 0
        try:
            # Disabilita temporaneamente i messaggi websocket durante l'ingestione
            original_send_ws = None
            if hasattr(cat, 'send_ws_message'):
                original_send_ws = cat.send_ws_message
                
                def silent_send_ws_message(*args, **kwargs):
                    # Ignora silenziosamente gli errori websocket
                    return None
                
                # Sostituisci temporaneamente il metodo originale
                cat.send_ws_message = silent_send_ws_message
            
            # Usa l'API CheshireCat per ingestire il documento
            ingest_result = cat.rabbit_hole.ingest_file(
                cat=cat,
                file=str(file_path),
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                metadata=custom_metadata
            )
            
            # Ripristina il metodo originale se necessario
            if original_send_ws is not None:
                cat.send_ws_message = original_send_ws
            
            # Salviamo direttamente la mappatura UUID
            save_uuid_mapping(doc_id, uuid)
            log.info(f"✅ Documento ingerito con UUID: {uuid}")
            
            # Determina il numero di chunks generati (se disponibile)
            chunks_count = len(ingest_result.chunks) if ingest_result and hasattr(ingest_result, 'chunks') else 0
            
        except Exception as ingest_error:
            # Ripristina il metodo originale in caso di errore
            if original_send_ws is not None:
                cat.send_ws_message = original_send_ws
                
            error_msg = f"Errore durante l'ingestione del documento '{doc_id}': {str(ingest_error)}"
            log.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status": 500
            }
        
        # 10. Log e restituzione risultato
        log.info(f"✅ Documento '{doc_id}' aggiunto al RAG con successo")
        if chunks_count > 0:
            log.info(f"   📄 {chunks_count} chunks generati")
        
        return {
            "success": True,
            "message": f"Documento '{doc_id}' aggiunto al RAG con successo",
            "chunks_count": chunks_count,
            "file_size_kb": round(file_size / 1024, 1),
            "uuid": uuid,
            "status": 200
        }
    except Exception as e:
        error_msg = f"Errore nell'aggiunta del documento '{doc_id}' al RAG: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }
    

def update_all_documents():
    """Aggiorna tutti i documenti attivi nel RAG"""
    try:
        active_documents = get_active_documents(rag_only=True, max_priority=5)
        
        if not active_documents:
            return {
                "success": True,
                "message": "Nessun documento attivo da elaborare",
                "status": 200
            }
        
        log.info(f"🔄 Aggiornamento di {len(active_documents)} documenti attivi")
        
        # Verifica che l'istanza di CheshireCat sia inizializzata correttamente
        try:
            cat = get_cat_instance()
            log.info("✅ Istanza CheshireCat disponibile per l'aggiornamento")
        except Exception as e:
            error_msg = f"Errore nell'inizializzazione di CheshireCat: {str(e)}"
            log.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status": 500
            }
        
        results = {
            "success": True,
            "processed": 0,
            "failed": 0,
            "details": []
        }
        
        for doc in active_documents:
            doc_id = doc["id"]
            result = add_document_to_rag(doc_id)
            
            if result.get("success", False):
                results["processed"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "id": doc_id,
                "success": result.get("success", False),
                "error": result.get("error", None) if not result.get("success", False) else None
            })
        
        log.info(f"✅ Aggiornamento completato: {results['processed']} documenti elaborati, {results['failed']} falliti")
        return results
    except Exception as e:
        error_msg = f"Errore nell'aggiornamento dei documenti: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }


def delete_document_from_memory(doc_id, uuid=None):
    """Elimina un documento dalla memoria"""
    try:
        # 1. Ottieni l'UUID del documento se non fornito
        if not uuid:
            uuid = get_uuid_mapping(doc_id)
            
        if not uuid:
            log.warning(f"⚠️ UUID non trovato per il documento '{doc_id}'")
            return False
        
        # 2. Ottieni l'istanza di CheshireCat/StrayCat
        cat = get_cat_instance()
        
        # 3. Elimina direttamente tramite filtro metadati (metodo preferito)
        success = False
        if hasattr(cat.memory, 'vectors') and hasattr(cat.memory.vectors, 'declarative'):
            try:
                metadata_filter = {"id": doc_id}
                if hasattr(cat.memory.vectors.declarative, 'delete_points_by_metadata_filter'):
                    log.info(f"🔍 Eliminazione documento '{doc_id}' (UUID: {uuid}) tramite filtro metadati")
                    result = cat.memory.vectors.declarative.delete_points_by_metadata_filter(metadata_filter)
                    log.info(f"✅ Risultato eliminazione: {result}")
                    success = True
            except Exception as e:
                log.warning(f"⚠️ Errore nell'eliminazione tramite filtro metadati: {str(e)}")
        
        # 4. Se l'eliminazione è avvenuta con successo, rimuovi anche la mappatura UUID
        if success:
            delete_uuid_mapping(doc_id)
            log.info(f"✅ Documento '{doc_id}' eliminato dalla memoria con successo")
            
        return success
    except Exception as e:
        log.error(f"❌ Errore generale nell'eliminazione del documento '{doc_id}': {str(e)}")
        return False