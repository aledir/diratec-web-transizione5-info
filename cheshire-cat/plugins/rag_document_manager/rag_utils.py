"""Utilità per l'integrazione con il sistema RAG."""
import hashlib
import time
import json
import os
from pathlib import Path
from cat.log import log

def generate_deterministic_uuid(doc_id):
    """Genera un UUID deterministico basato sull'ID del documento"""
    # Crea un UUID deterministico basato sull'ID del documento
    uuid_seed = f"{doc_id}_{int(time.time() / 3600)}"  # Cambia ogni ora
    uuid = hashlib.md5(uuid_seed.encode()).hexdigest()
    return uuid

def delete_document_from_memory(doc_id, cat, uuid=None, documents_dir="/app/cat/shared"):
    """Elimina un documento dalla memoria RAG"""
    try:
        # Importa le funzioni necessarie
        from .document_operations import get_uuid_mapping, delete_uuid_mapping
        
        # Ottieni l'UUID se non fornito
        if not uuid:
            uuid = get_uuid_mapping(doc_id)
            
        if not uuid:
            error_msg = f"UUID non trovato per il documento '{doc_id}' - Impossibile eliminare dal RAG"
            log.error(f"❌ {error_msg}")
            # Log dei dettagli per diagnostica
            try:
                from .document_operations import get_all_uuid_mappings
                log.error(f"Contenuto corrente di .uuid_map.json: {json.dumps(get_all_uuid_mappings(), indent=2)}")
            except:
                log.error("Impossibile ottenere il contenuto completo di .uuid_map.json")
            
            return {
                "success": False,
                "error": error_msg,
                "doc_id": doc_id,
                "action": "delete",
                "reason": "missing_uuid"
            }
        
        # Elimina il documento dalla memoria vettoriale
        if hasattr(cat.memory, 'vectors') and hasattr(cat.memory.vectors, 'declarative'):
            try:
                metadata_filter = {"id": doc_id}
                log.info(f"🔍 Eliminazione documento '{doc_id}' (UUID: {uuid}) tramite filtro metadati")
                
                if hasattr(cat.memory.vectors.declarative, 'delete_points_by_metadata_filter'):
                    result = cat.memory.vectors.declarative.delete_points_by_metadata_filter(metadata_filter)
                    log.info(f"✅ Risultato eliminazione: {result}")
                    
                    # Rimuovi la mappatura UUID
                    delete_success = delete_uuid_mapping(doc_id)
                    log.info(f"Mappatura UUID eliminata: {delete_success}")
                    
                    return True
                else:
                    error_msg = "Funzione delete_points_by_metadata_filter non disponibile nell'API"
                    log.error(f"❌ {error_msg}")
                    return {
                        "success": False, 
                        "error": error_msg,
                        "doc_id": doc_id
                    }
            except Exception as e:
                error_msg = f"Errore nell'eliminazione del documento: {str(e)}"
                log.error(f"❌ {error_msg}")
                return {
                    "success": False, 
                    "error": error_msg,
                    "doc_id": doc_id,
                    "exception": str(e)
                }
        else:
            error_msg = "API memoria vettoriale non disponibile"
            log.error(f"❌ {error_msg}")
            return {
                "success": False, 
                "error": error_msg,
                "doc_id": doc_id
            }
    except Exception as e:
        error_msg = f"Errore nella funzione delete_document_from_memory: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False, 
            "error": error_msg,
            "doc_id": doc_id,
            "exception": str(e)
        }

def insert_markdown_into_rag(doc_id, cat, documents_dir="/app/cat/shared"):
    """Inserisce un singolo documento markdown nel RAG con i parametri di chunking specificati."""
    try:
        # Importa le funzioni necessarie
        from .document_operations import save_uuid_mapping, get_document_by_id, get_uuid_mapping
        
        # Carica i metadati del documento
        doc_info = get_document_by_id(doc_id)
        
        if not doc_info:
            error_msg = f"Documento non trovato: {doc_id}"
            log.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status": 404
            }
        
        # Verifica se il documento è attivo
        if doc_info.get("stato") != "attivo":
            error_msg = f"Il documento {doc_id} non è attivo"
            log.warning(f"⚠️ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status": 400
            }
        
        # Verifica se il documento ha un percorso markdown
        if not doc_info.get("markdown_path"):
            error_msg = f"Nessun percorso markdown per il documento {doc_id}"
            log.warning(f"⚠️ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status": 400
            }
        
        # Costruisci il percorso completo del file markdown
        markdown_path = os.path.join(documents_dir, doc_info["markdown_path"])
        if not os.path.exists(markdown_path):
            error_msg = f"File markdown non trovato: {markdown_path}"
            log.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status": 404
            }

        # Leggi il contenuto del file markdown
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        
        # Controlla se il contenuto è vuoto
        if not markdown_content.strip():
            error_msg = f"Contenuto markdown vuoto: {doc_id}"
            log.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status": 400
            }
        
        # Logga dettagli sul file
        file_size = os.path.getsize(markdown_path)
        log.info(f"📁 File markdown: {markdown_path} ({file_size} bytes)")
        newline_count = markdown_content.count('\n')
        log.info(f"📄 Contenuto: {len(markdown_content)} caratteri, {newline_count} righe")
        
        # Applica opzioni di pulizia se presenti
        clean_options = doc_info.get("clean_options", {})
        original_length = len(markdown_content)
        
        if clean_options:
            taglia_inizio = clean_options.get("taglia_caratteri_inizio", 0)
            taglia_fine = clean_options.get("taglia_caratteri_fine", 0)
            
            if taglia_inizio > 0:
                log.info(f"🔄 Rimozione di {taglia_inizio} caratteri all'inizio")
                markdown_content = markdown_content[taglia_inizio:]
            
            if taglia_fine > 0:
                log.info(f"🔄 Rimozione di {taglia_fine} caratteri alla fine")
                content_length = len(markdown_content)
                markdown_content = markdown_content[:content_length - taglia_fine]
            
            # Logga dati sulla pulizia
            new_length = len(markdown_content)
            reduction_percent = ((original_length - new_length) / original_length) * 100 if original_length > 0 else 0
            log.info(f"🔄 Pulizia: originale {original_length} → pulito {new_length} caratteri ({reduction_percent:.1f}% rimosso)")
        
        # Verifica che il contenuto non sia vuoto dopo la pulizia
        if not markdown_content.strip():
            error_msg = f"Contenuto markdown vuoto dopo la pulizia: {doc_id}"
            log.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status": 400
            }
        
        # Crea un file temporaneo con il contenuto pulito
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False, encoding="utf-8")
        try:
            # Scrivi il contenuto pulito nel file temporaneo
            temp_file.write(markdown_content)
            temp_file.flush()
            temp_file.close()
            
            # Crea metadati personalizzati per il documento
            custom_metadata = {
                "id": doc_id,
                "titolo": doc_info["titolo"],
                "categoria": doc_info["categoria"],
                "tipo": doc_info["tipo"],
                "data": doc_info["data"],
                "tags": doc_info.get("tags", []),
                "stato": "attivo",
                "path": os.path.relpath(markdown_path, documents_dir),
                # Aggiungiamo metadati per tracciamento
                "original_path": doc_info["markdown_path"],
                "original_file": os.path.basename(doc_info["markdown_path"]),
                "temp_file": temp_file.name  # Per debugging
            }
            
            # Parametri di chunking
            chunk_size = doc_info.get("chunk_size", 1000)
            chunk_overlap = doc_info.get("chunk_overlap", 200)
            
            # Log dei parametri di ingestione
            log.info(f"🔄 Ingestione documento markdown '{doc_id}' - File: {markdown_path}")
            log.info(f"📊 Chunking: size={chunk_size}, overlap={chunk_overlap}")
            log.info(f"🔄 File temporaneo: {temp_file.name}")
            
            # Prima rimuovi eventuali versioni precedenti
            # Verifica se esiste un UUID per questo documento
            existing_uuid = get_uuid_mapping(doc_id)
            if existing_uuid:
                log.info(f"🔄 Rimozione versione precedente del documento '{doc_id}' (UUID: {existing_uuid})")
                delete_result = delete_document_from_memory(doc_id, cat, uuid=existing_uuid)
                log.info(f"🔄 Risultato rimozione: {delete_result}")
            else:
                log.info(f"ℹ️ Nessuna versione precedente da rimuovere per il documento '{doc_id}'")
            
            # Genera un nuovo UUID per il documento
            uuid = generate_deterministic_uuid(doc_id)
            log.info(f"🔑 UUID generato: {uuid}")
            
            # Disabilita temporaneamente i messaggi websocket durante l'ingestione
            original_send_ws = None
            if hasattr(cat, 'send_ws_message'):
                original_send_ws = cat.send_ws_message
                
                def silent_send_ws_message(*args, **kwargs):
                    # Ignora silenziosamente gli errori websocket
                    return None
                
                # Sostituisci temporaneamente il metodo originale
                cat.send_ws_message = silent_send_ws_message
            
            # Ingestisci il documento
            try:
                log.info(f"🔄 Inizio ingestione file: {temp_file.name}")
                
                # Invece di usare ingest_file, usiamo le funzioni di livello inferiore
                # per avere più controllo sul campo source
                
                # 1. Convertiamo il file in docs usando file_to_docs
                docs = cat.rabbit_hole.file_to_docs(
                    cat=cat,
                    file=temp_file.name,  # Usiamo ancora il file temporaneo
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                
                log.info(f"📑 Generati {len(docs)} documenti dal file")
                
                # 2. Chiamiamo direttamente store_documents con un source personalizzato
                # Usiamo il percorso originale come source invece del percorso del file temporaneo
                source = os.path.join(documents_dir, doc_info["markdown_path"])
                log.info(f"🔄 Utilizzo source originale: {source}")
                
                # 3. Memorizziamo i docs con il source corretto
                ingest_result = cat.rabbit_hole.store_documents(
                    cat=cat,
                    docs=docs,
                    source=source,  # Qui è la chiave: usiamo il percorso originale
                    metadata=custom_metadata
                )
                
                log.info(f"🔄 Ingestione documento completata")
                
                # Ripristina il metodo originale se necessario
                if original_send_ws is not None:
                    cat.send_ws_message = original_send_ws
                
                # Verifica il risultato dell'ingestione
                if ingest_result is None:
                    log.info(f"🔄 Documento elaborato in {len(docs)} chunks")
                    chunks_count = len(docs)  # Usa il numero di chunks generati
                    
                    # Salva la mappatura UUID
                    uuid_saved = save_uuid_mapping(doc_id, uuid)
                    if uuid_saved:
                        log.info(f"✅ Mappatura UUID salvata per '{doc_id}': {uuid}")
                    else:
                        log.warning(f"⚠️ Impossibile salvare la mappatura UUID per '{doc_id}'")
                    
                    log.info(f"✅ Documento '{doc_id}' aggiunto al RAG con successo ({chunks_count} chunks)")
                    
                    return {
                        "success": True,
                        "message": f"Documento markdown '{doc_id}' aggiunto al RAG con successo",
                        "chunks_count": chunks_count,
                        "file_size_kb": round(os.path.getsize(markdown_path) / 1024, 1),
                        "uuid": uuid,
                        "status": 200
                    }
                
                # Verifica la presenza dell'attributo chunks
                if not hasattr(ingest_result, 'chunks'):
                    error_msg = f"L'oggetto risultato dell'ingestione non ha l'attributo 'chunks'. Tipo: {type(ingest_result)}"
                    log.error(f"❌ {error_msg}")
                    # Loghiamo più dettagli sull'oggetto per diagnosticare meglio
                    log.error(f"Dettagli oggetto: {ingest_result}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "status": 500
                    }
                
                # Determina il numero di chunks generati
                chunks_count = len(ingest_result.chunks)
                
                # Analisi dei chunks
                if chunks_count == 0:
                    log.warning(f"⚠️ Nessun chunk generato per il documento '{doc_id}' - Possibile problema di configurazione")
                elif chunks_count == 1 and len(markdown_content) > chunk_size * 2:
                    log.warning(f"⚠️ Documento '{doc_id}' con {len(markdown_content)} caratteri ha generato solo 1 chunk - Possibile problema di chunking")
                    log.warning(f"⚠️ Parametri usati: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
                
                # Salva la mappatura UUID
                save_uuid_mapping(doc_id, uuid)
                log.info(f"✅ Documento ingerito con UUID: {uuid}")
                log.info(f"✅ {chunks_count} chunks generati")
                
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
            
            # Log e restituzione risultato
            log.info(f"✅ Documento markdown '{doc_id}' aggiunto al RAG con successo")
            
            return {
                "success": True,
                "message": f"Documento markdown '{doc_id}' aggiunto al RAG con successo",
                "chunks_count": chunks_count,
                "file_size_kb": round(os.path.getsize(markdown_path) / 1024, 1),
                "uuid": uuid,
                "status": 200
            }
        
        finally:
            # Assicurati di eliminare il file temporaneo
            try:
                os.unlink(temp_file.name)
                log.info(f"🧹 File temporaneo eliminato: {temp_file.name}")
            except Exception as e:
                log.warning(f"⚠️ Impossibile eliminare file temporaneo {temp_file.name}: {str(e)}")
    
    except Exception as e:
        error_msg = f"Errore nell'aggiunta del documento markdown '{doc_id}' al RAG: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }

def insert_all_markdown_into_rag(cat, documents_dir="/app/cat/shared"):
    """Inserisce tutti i documenti markdown nel RAG."""
    try:
        # Importa le funzioni necessarie
        from .document_operations import get_active_documents
        
        # Ottieni tutti i documenti attivi
        active_docs = get_active_documents()
        docs_with_markdown = [doc for doc in active_docs if doc.get("markdown_path")]
        
        if not docs_with_markdown:
            return {
                "success": True,
                "message": "Nessun documento markdown trovato",
                "processed": 0,
                "failed": 0,
                "details": [],
                "status": 200
            }
        
        log.info(f"🔄 Inserimento di {len(docs_with_markdown)} documenti markdown nel RAG")
        
        results = {
            "processed": 0,
            "failed": 0,
            "details": []
        }
        
        for doc in docs_with_markdown:
            doc_id = doc["id"]
            log.info(f"🔄 Elaborazione documento: {doc_id}")
            
            result = insert_markdown_into_rag(doc_id, cat, documents_dir)
            
            if result.get("success"):
                results["processed"] += 1
                results["details"].append({
                    "id": doc_id,
                    "success": True,
                    "chunks": result.get("chunks_count", 0),
                    "size_kb": result.get("file_size_kb", 0)
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "id": doc_id,
                    "success": False,
                    "error": result.get("error", "Errore sconosciuto")
                })
        
        log.info(f"✅ Inserimento completato: {results['processed']} documenti elaborati, {results['failed']} falliti")
        
        return {
            "success": True,
            "message": f"Inserimento completato: {results['processed']} documenti elaborati, {results['failed']} falliti",
            "processed": results["processed"],
            "failed": results["failed"],
            "details": results["details"],
            "status": 200
        }
    
    except Exception as e:
        error_msg = f"Errore nell'inserimento dei documenti markdown nel RAG: {str(e)}"
        log.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "status": 500
        }

def verify_rag_consistency(cat, documents_dir="/app/cat/shared/documents"):
    """Verifica la coerenza tra documenti nel RAG e metadati."""
    try:
        from .document_operations import read_metadata, get_uuid_mapping, get_all_uuid_mappings
        
        metadata = read_metadata()
        active_docs = [f for f in metadata.get("files", []) if f.get("stato") == "attivo"]
        uuid_map = get_all_uuid_mappings()
        
        results = {
            "total_documents": len(active_docs),
            "documents_with_markdown": 0,
            "documents_with_uuid": 0,
            "documents_in_rag": 0,
            "missing_markdown_files": [],
            "missing_uuid_mappings": [],
            "inconsistent_documents": [],
            "orphaned_uuids": []
        }
        
        # Set di tutti gli ID documento attivi
        active_doc_ids = {doc.get("id") for doc in active_docs}
        
        # Verifica UUID orfani (UUID map contiene documenti non più attivi)
        for doc_id in uuid_map:
            if doc_id not in active_doc_ids:
                results["orphaned_uuids"].append({
                    "id": doc_id,
                    "uuid": uuid_map[doc_id]
                })
        
        # Verifica ogni documento attivo
        for doc in active_docs:
            doc_id = doc.get("id")
            
            # Verifica file markdown
            has_markdown = False
            if doc.get("markdown_path"):
                markdown_path = Path(documents_dir) / doc["markdown_path"]
                if markdown_path.exists():
                    results["documents_with_markdown"] += 1
                    has_markdown = True
                    
                    # Verifica dimensione del file
                    file_size = os.path.getsize(markdown_path)
                    if file_size < 100:  # Dimensione minima ragionevole
                        results["inconsistent_documents"].append({
                            "id": doc_id,
                            "issue": "markdown_too_small",
                            "size_bytes": file_size,
                            "path": str(markdown_path)
                        })
                else:
                    results["missing_markdown_files"].append({
                        "id": doc_id,
                        "expected_path": str(markdown_path)
                    })
            
            # Verifica UUID mapping
            uuid = get_uuid_mapping(doc_id)
            if uuid:
                results["documents_with_uuid"] += 1
            else:
                if has_markdown:  # Segnala solo se il markdown esiste
                    results["missing_uuid_mappings"].append({
                        "id": doc_id
                    })
        
        return results
    except Exception as e:
        log.error(f"❌ Errore nella verifica della coerenza RAG: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }