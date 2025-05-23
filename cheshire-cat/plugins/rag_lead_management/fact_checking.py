"""Funzionalità per il controllo dei fatti, la riduzione delle allucinazioni e l'approccio commerciale positivo."""
from cat.log import log
from .utils import load_prompt_file

def verify_response(content, declarative_memories, cat):
    """
    Verifica che la risposta dell'AI sia basata sui fatti disponibili e mantenga un approccio commerciale positivo.
    """
    # Prepara il contesto dei fatti
    facts_context = ""
    
    # Carica le informazioni di base
    basic_info = load_prompt_file("06_prompt_basic_info.md")
    facts_context += basic_info + "\n\n"
    
    # Carica le istruzioni sulla priorità dei documenti e l'approccio commerciale
    document_priority = load_prompt_file("03_prompt_commercial.md")
    
    # Estrai le parti rilevanti per il fact checking
    if "IMPORTANTE - PRIORITÀ DEI DOCUMENTI:" in document_priority:
        start_index = document_priority.find("IMPORTANTE - PRIORITÀ DEI DOCUMENTI:")
        end_index = document_priority.find("IMPORTANTE -", start_index + 1)
        if end_index > 0:
            facts_context += document_priority[start_index:end_index].strip() + "\n\n"
        else:
            facts_context += document_priority[start_index:].strip() + "\n\n"
    else:
        raise ValueError("Sezione 'IMPORTANTE - PRIORITÀ DEI DOCUMENTI:' non trovata nel file 03_prompt_commercial.md")
    
    # Log per verificare il numero di memorie
    if declarative_memories:
        log.info(f"ℹ️ Verifica risposta con {len(declarative_memories)} memorie dichiarative")
    else:
        log.warning("⚠️ Nessuna memoria dichiarativa disponibile per verificare la risposta")
        facts_context += "(Nessun documento disponibile sulla Transizione 5.0)\n\n"
        
    # Aggiungi le memorie al contesto
    if declarative_memories:
        # Per ogni memoria, aggiungi un'indicazione della sua data/priorità
        for i, memory in enumerate(declarative_memories):
            doc_metadata = ""
            
            if hasattr(memory[0], "metadata"):
                # Estrai informazioni rilevanti dai metadati
                meta = memory[0].metadata
                doc_type = meta.get("tipo", "Documento")
                doc_date = meta.get("data", "N/A")
                doc_title = meta.get("titolo", "Documento senza titolo")
                
                # Determina se è un documento prioritario
                is_faq = doc_type.upper() == "FAQ"
                is_recent = False
                try:
                    # Verifica se è successivo alla Legge di Bilancio 2025
                    if doc_date >= "2025-01-01":
                        is_recent = True
                except:
                    pass
                
                # Crea l'indicatore di priorità
                priority = ""
                if is_faq:
                    priority = "[PRIORITÀ MASSIMA - FAQ] "
                elif is_recent:
                    priority = "[DOCUMENTO RECENTE] "
                
                doc_metadata = f"{priority}{doc_type} del {doc_date}: {doc_title}\n"
            
            # Aggiungi il contenuto con metadati
            facts_context += f"--- DOCUMENTO #{i+1} {doc_metadata}---\n{memory[0].page_content}\n---\n\n"
    
    # Aggiungi istruzioni per l'approccio commerciale positivo
    if "IMPORTANTE - APPROCCIO COMMERCIALE POSITIVO:" in document_priority:
        start_index = document_priority.find("IMPORTANTE - APPROCCIO COMMERCIALE POSITIVO:")
        end_index = document_priority.find("IMPORTANTE -", start_index + 1)
        if end_index > 0:
            facts_context += document_priority[start_index:end_index].strip()
        else:
            facts_context += document_priority[start_index:].strip()
    else:
        raise ValueError("Sezione 'IMPORTANTE - APPROCCIO COMMERCIALE POSITIVO:' non trovata nel file 03_prompt_commercial.md")
    
    # Carica e utilizza il template di fact checking
    fact_checking_template = load_prompt_file("05_prompt_fact_checking.md")
    
    # Sostituisci i placeholder nel template
    prompt = fact_checking_template.format(facts_context=facts_context, content=content)
    
    # Esegui il controllo dei fatti
    verified_response = cat.llm(prompt)
    
    log.info(f"✅ Risposta verificata con controllo priorità documenti e APPROCCIO COMMERCIALE POSITIVO")
    return verified_response