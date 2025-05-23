"""Funzionalità per la gestione della priorità dei documenti."""
from cat.log import log
from datetime import datetime
from .utils import load_prompt_file

def prioritize_documents(memories):
    """
    Ordina le memorie in base alla loro priorità e attualità.
    
    Args:
        memories: Lista di memorie dichiarative
        
    Returns:
        list: Memorie ordinate per priorità
    """
    # Se non ci sono memorie, solleva un'eccezione
    if not memories:
        log.warning("⚠️ Nessuna memoria da prioritizzare")
        raise ValueError("Nessuna memoria disponibile per la prioritizzazione")
    
    # Log il numero di memorie da prioritizzare
    log.info(f"ℹ️ Prioritizzazione di {len(memories)} memorie")
    
    # Classifica le memorie in base a tipo e data
    classified_memories = []
    for memory in memories:
        # Valori predefiniti
        priority = 0
        doc_type = "documento"
        doc_date = "2000-01-01"
        is_faq = False
        is_post_2025 = False
        doc_id = "unknown"
        
        # Estrai i metadati se disponibili
        if hasattr(memory[0], "metadata"):
            meta = memory[0].metadata
            
            # Debug log dei metadati completi
            log.debug(f"ℹ️ Metadati del documento: {meta}")
            
            # Estrai l'ID del documento se disponibile
            if "id" in meta:
                doc_id = meta["id"]
            
            # Determina il tipo di documento
            if "tipo" in meta:
                doc_type = meta["tipo"].upper()
                if doc_type == "FAQ":
                    is_faq = True
                    priority += 100  # Massima priorità alle FAQ
            
            # Determina la data del documento
            if "data" in meta:
                doc_date = meta["data"]
                # Verifica se è successivo alla Legge di Bilancio 2025
                try:
                    if doc_date >= "2025-01-01":
                        is_post_2025 = True
                        priority += 50  # Alta priorità ai documenti post-2025
                except:
                    pass
            
            # Assegna priorità in base al tipo di documento
            if doc_type == "CIRCOLARE":
                priority += 40
            elif doc_type == "NORMATIVA":
                priority += 30
            elif doc_type == "GUIDA":
                priority += 20
            elif doc_type == "MODELLO":
                priority += 10
        
        # Aggiungi alla lista classificata
        classified_memories.append({
            "memory": memory,
            "priority": priority,
            "doc_type": doc_type,
            "doc_date": doc_date,
            "is_faq": is_faq,
            "is_post_2025": is_post_2025,
            "doc_id": doc_id
        })
    
    # Ordina le memorie per priorità decrescente e data più recente
    classified_memories.sort(key=lambda x: (x["priority"], x["doc_date"]), reverse=True)
    
    # Estrai e restituisci solo le memorie ordinate
    sorted_memories = [item["memory"] for item in classified_memories]
    
    # Logga l'ordine delle memorie
    log_order = []
    for i, item in enumerate(classified_memories[:5]):  # Limita a 5 per brevità
        log_order.append(f"{item['doc_id']} ({item['doc_type']}, {item['doc_date']}, priorità: {item['priority']})")
    
    log.info(f"✅ Ordine priorità documenti: {', '.join(log_order)}")
    
    return sorted_memories

def format_memory_context(memories):
    """
    Formatta le memorie come contesto per il modello linguistico, evidenziando le priorità.
    """
    # Se non ci sono memorie, solleva un'eccezione
    if not memories or len(memories) == 0:
        raise ValueError("Nessuna memoria disponibile per la formattazione del contesto")
    
    # Carica i prompt da file
    technical_prompt = load_prompt_file("02_prompt_technical.md")
    update_info_prompt = load_prompt_file("07_prompt_updates_info.md")
    
    # Inizia il contesto con le informazioni aggiornate
    context = update_info_prompt + "\n\n"
    
    # Estrai la sezione sulle aliquote del credito d'imposta
    aliquote_info = ""
    if "3. ALIQUOTE DEL CREDITO D'IMPOSTA" in technical_prompt:
        start_index = technical_prompt.find("3. ALIQUOTE DEL CREDITO D'IMPOSTA")
        end_index = technical_prompt.find("4. FOTOVOLTAICO", start_index)
        if end_index > 0:
            aliquote_info = technical_prompt[start_index:end_index].strip()
        else:
            raise ValueError("Sezione sulle aliquote del credito d'imposta non trovata correttamente")
    else:
        raise ValueError("Sezione sulle aliquote del credito d'imposta non trovata nel file technical_prompt")
    
    # Aggiungi le informazioni aggiornate sulle aliquote
    context += f"\n{aliquote_info}\n"
    
    # Aggiungi ogni memoria al contesto, con nota sulla priorità
    for i, memory in enumerate(memories):
        doc_metadata = ""
        
        if hasattr(memory[0], "metadata"):
            # Estrai informazioni rilevanti dai metadati
            meta = memory[0].metadata
            doc_type = meta.get("tipo", "Documento").upper()
            doc_date = meta.get("data", "N/A")
            doc_title = meta.get("titolo", "Documento senza titolo")
            
            # Determina la priorità visiva del documento
            priority_label = ""
            if doc_type == "FAQ":
                priority_label = "⭐⭐⭐ [MASSIMA PRIORITÀ - FAQ] "
            elif doc_date >= "2025-01-01":
                priority_label = "⭐⭐ [ALTA PRIORITÀ - DOCUMENTO 2025] "
            elif doc_type == "CIRCOLARE":
                priority_label = "⭐ [MEDIA PRIORITÀ - CIRCOLARE] "
            
            # Formatta i metadati
            doc_metadata = f"{priority_label}{doc_type} DEL {doc_date}: {doc_title}\n"
            
            # Avviso speciale per documenti obsoleti
            if doc_date < "2025-01-01" and doc_type != "FAQ":
                doc_metadata += "(ATTENZIONE: Questo documento potrebbe contenere informazioni obsolete su scaglioni e aliquote. In caso di conflitto, fare riferimento ai documenti più recenti)\n"
        
        # Aggiungi il contenuto con metadati e priorità in modo più evidente
        context += f"\n\n{'='*50}\nDOCUMENTO #{i+1}: {doc_metadata}\n{'='*50}\n\n{memory[0].page_content}\n"
    
    # Aggiungi una riga finale per marcare la fine dei documenti
    context += f"\n\n{'='*50}\n FINE DEI DOCUMENTI UFFICIALI TRANSIZIONE 5.0 {'='*50}\n"
    
    return context