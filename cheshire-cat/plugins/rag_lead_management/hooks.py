"""Funzionalità per la gestione degli hook di Cheshire Cat."""
from cat.mad_hatter.decorators import hook
from cat.log import log
import os
import json

from .conversation_instructions import get_phase_prompt
from .utils import load_prompt_file

# Carica la configurazione
CONFIG_PATH = os.path.join("/app/cat/shared", "config.json")
config = {}
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    log.info(f"✅ Configurazione caricata da: {CONFIG_PATH}")
except Exception as e:
    log.error(f"❌ Errore nel caricamento della configurazione: {str(e)}")
    config = {
        "assistant": {
            "id": "quinto",
            "displayName": "Quinto",
            "fullTitle": "Quinto - Assistente Transizione 5.0",
            "welcomeMessage": "Ciao! Sono Quinto, l'assistente virtuale specializzato in Transizione 5.0.",
            "description": "Assistente specializzato in Transizione 5.0"
        }
    }
    log.warning(f"⚠️ Utilizzo configurazione di fallback")

def check_declarative_memory(cat):
    """Verifica che la memoria dichiarativa contenga documenti"""
    try:
        # Verifica se cat.memory esiste
        if not hasattr(cat, 'memory'):
            log.warning("⚠️ Sistema di memoria non disponibile")
            return False
            
        # L'API corretta per verificare il conteggio dei documenti
        if hasattr(cat.memory, 'vectors') and hasattr(cat.memory.vectors, 'langchain_store'):
            # Accedi al vector store di LangChain
            vector_store = cat.memory.vectors.langchain_store
            
            # Ottieni il nome della collezione
            collection_name = "declarative_memory"
            
            # Verifica se la collezione esiste e conta i documenti
            try:
                # Utilizzo dell'API di langchain per ottenere la dimensione della collezione
                count = vector_store._collection.count()
                log.info(f"✅ Memoria dichiarativa: {count} documenti trovati")
                return count > 0
            except Exception as inner_e:
                log.warning(f"⚠️ Errore nel conteggio dei documenti: {str(inner_e)}")
                # Prova con un approccio alternativo
                try:
                    # In alcune versioni potrebbe essere disponibile direttamente
                    if hasattr(vector_store, 'index'):
                        count = len(vector_store.index)
                        log.info(f"✅ Memoria dichiarativa: {count} documenti trovati")
                        return count > 0
                except:
                    pass
                
                # Se arriviamo qui, non siamo riusciti a contare i documenti
                log.info("ℹ️ Impossibile contare i documenti, ma il sistema di memoria è disponibile")
                return True
        else:
            log.info("ℹ️ Il vector store non è accessibile direttamente, ma il sistema di memoria è disponibile")
            return True
    except Exception as e:
        log.error(f"❌ Errore nel controllo della memoria dichiarativa: {str(e)}")
        return False
    

@hook
def before_cat_recalls_declarative_memories(declarative_recall_config, cat):
    """
    Configura il recupero delle memorie dichiarative (documenti)
    prima che il Cat le ricerchi.
    
    Args:
        declarative_recall_config: Configurazione per il recall delle memorie dichiarative
        cat: Istanza di Cheshire Cat
        
    Returns:
        dict: Configurazione aggiornata
    """
    try:
        # Aumenta il numero di documenti da recuperare per avere più contesto
        declarative_recall_config["k"] = 5
        
        # Abbassa leggermente la soglia per recuperare più documenti pertinenti
        declarative_recall_config["threshold"] = 0.2
        
        log.info(f"✅ Configurazione recall dichiarativo personalizzata applicata: k={declarative_recall_config['k']}, threshold={declarative_recall_config['threshold']}")
        return declarative_recall_config
    except Exception as e:
        log.error(f"❌ Errore nella configurazione del recall dichiarativo: {str(e)}")
        return declarative_recall_config

@hook
def after_cat_recalls_memories(cat):
    """
    Interviene dopo che il Cat ha recuperato le memorie,
    applicando la prioritizzazione dei documenti.
    
    Args:
        cat: Istanza di Cheshire Cat
    """
    try:
        # Recupera le memorie dichiarative
        if hasattr(cat.working_memory, "declarative_memories") and cat.working_memory.declarative_memories:
            # Applica la prioritizzazione utilizzando il modulo document_priority
            from .document_priority import prioritize_documents
            
            # Prioritizza le memorie recuperate
            original_memories = cat.working_memory.declarative_memories
            log.info(f"ℹ️ Memorie dichiarative recuperate prima della prioritizzazione: {len(original_memories)}")
            
            # Prioritizza i documenti
            sorted_memories = prioritize_documents(original_memories)
            
            # Sostituisci le memorie originali con quelle prioritizzate
            cat.working_memory.declarative_memories = sorted_memories
            
            log.info(f"✅ Memorie dichiarative prioritizzate: {len(sorted_memories)}")
            
            # Log dei documenti prioritizzati per debug
            for i, memory in enumerate(sorted_memories[:3]):  # Log solo i primi 3 per brevità
                if hasattr(memory[0], "metadata"):
                    doc_type = memory[0].metadata.get("tipo", "N/A")
                    doc_date = memory[0].metadata.get("data", "N/A")
                    doc_title = memory[0].metadata.get("titolo", "N/A")
                    log.info(f"📄 Doc #{i+1}: {doc_title} ({doc_type}, {doc_date})")
        else:
            log.warning(f"⚠️ Nessuna memoria dichiarativa recuperata dal RAG")
    except Exception as e:
        log.error(f"❌ Errore nella prioritizzazione delle memorie dopo il recall: {str(e)}")

@hook
def before_agent_starts(agent_input, cat):
    """
    Prepara l'input per l'agente prima che inizi a generare una risposta.
    """
    try:
        # Gestione delle memorie dichiarative (codice esistente)
        if hasattr(cat.working_memory, "declarative_memories") and cat.working_memory.declarative_memories:
            # Usa il modulo document_priority per formattare le memorie
            from .document_priority import format_memory_context
            
            # Ottieni le memorie dichiarative dall'input o dalla working memory
            declarative_memories = cat.working_memory.declarative_memories
            
            # Formatta il contesto delle memorie
            formatted_context = format_memory_context(declarative_memories)
            
            # Aggiorna l'input dell'agente con il contesto formattato
            # Usa setattr per evitare warning
            setattr(agent_input, "declarative_memory", formatted_context)
            log.info("✅ Contesto delle memorie dichiarative formattato per l'agente")
        else:
            log.warning("⚠️ Nessuna memoria dichiarativa disponibile per l'agente")
        
        # Imposta valori di default per tutte le variabili richieste
        setattr(agent_input, "email", "")
        setattr(agent_input, "regione", "")
        setattr(agent_input, "budget", "")
        setattr(agent_input, "nome_azienda", "")
        
        # Ottieni i dati del lead dalla conversazione attiva
        try:
            # Ottieni l'ID della conversazione corrente
            conversation_id = cat.working_memory.conversation_id if hasattr(cat.working_memory, "conversation_id") else None
            
            if conversation_id:
                # Recupera la conversazione dal database
                from .database_operations import get_conversation
                conversation = get_conversation(conversation_id)
                
                if conversation and "data" in conversation:
                    # Estrai i dati del lead
                    lead_data = conversation.get("data", {}).get("lead_data", {})
                    
                    # Estrai valori specifici con valori predefiniti
                    email = lead_data.get("contatto_data", {}).get("email", "")
                    regione = lead_data.get("azienda_data", {}).get("regione", "")
                    budget = lead_data.get("investimenti_data", {}).get("budget", 0)
                    nome_azienda = lead_data.get("azienda_data", {}).get("nome_azienda", "")
                    
                    # Aggiungi i dati all'input dell'agente
                    setattr(agent_input, "email", email)
                    setattr(agent_input, "regione", regione)
                    setattr(agent_input, "budget", budget)
                    setattr(agent_input, "nome_azienda", nome_azienda)
                    
                    # Aggiungi anche alla working_memory per availability in altre funzioni
                    setattr(cat.working_memory, "email", email)
                    setattr(cat.working_memory, "regione", regione)
                    setattr(cat.working_memory, "budget", budget)
                    setattr(cat.working_memory, "nome_azienda", nome_azienda)
                    
                    log.info(f"✅ Dati del lead aggiunti per il template del prompt: email={email}, regione={regione}, budget={budget}, nome_azienda={nome_azienda}")
        except Exception as e:
            # Se c'è un errore nella parte nuova, logga ma non interrompere il flusso
            log.error(f"❌ Errore nell'aggiunta dei dati del lead: {str(e)}")
            import traceback
            log.error(traceback.format_exc())

        # Verifica che tutte le variabili richieste siano impostate
        log.info(f"Agent input contains: email={hasattr(agent_input, 'email')}, regione={hasattr(agent_input, 'regione')}, budget={hasattr(agent_input, 'budget')}")
            
        return agent_input
    except Exception as e:
        # Gestione eccezioni per l'intera funzione
        log.error(f"❌ Errore nella preparazione dell'input per l'agente: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return agent_input

@hook
def after_cat_bootstrap(cat):
    """Avvia task in background dopo l'avvio del sistema"""
    try:
        import threading
        import time
        
        def security_maintenance_task():
            """Task di manutenzione sicurezza in background"""
            log.info("🔄 Inizializzazione task periodico di manutenzione sicurezza...")
            
            try:
                # Importa i moduli necessari - Usa il percorso relativo corretto
                from .security import check_dependencies, session_manager, rate_limiter
                
                # Log di conferma avvio
                log.info("✅ Task periodico di manutenzione sicurezza inizializzato e pronto per l'esecuzione")
                
                while True:
                    try:
                        log.info("🔄 Esecuzione ciclo di manutenzione sicurezza...")
                        
                        # Verifica le dipendenze ogni 24 ore
                        log.info("- Verifica dipendenze in corso...")
                        check_dependencies()
                        
                        # Pulisci le sessioni scadute
                        log.info("- Pulizia sessioni scadute in corso...")
                        if hasattr(session_manager, 'clean_expired_sessions'):
                            cleaned = session_manager.clean_expired_sessions()
                            if cleaned > 0:
                                log.info(f"  🧹 Pulite {cleaned} sessioni scadute")
                        
                        # Pulisci le cache di rate limiting
                        log.info("- Pulizia cache rate limiting in corso...")
                        if hasattr(rate_limiter, 'clear_cache'):
                            cleared = rate_limiter.clear_cache(older_than_minutes=120)
                            if cleared > 0:
                                log.info(f"  🧹 Puliti {cleared} elementi dalla cache di rate limiting")
                                
                        log.info("✅ Ciclo di manutenzione sicurezza completato con successo")
                    except Exception as e:
                        log.error(f"❌ Errore nel ciclo di manutenzione: {str(e)}")
                    
                    # Log prima di dormire
                    log.info(f"💤 Task manutenzione in pausa per 12 ore")
                    
                    # Dormi per 12 ore
                    time.sleep(12 * 60 * 60)
            except Exception as e:
                log.error(f"❌ Errore critico nel task di manutenzione sicurezza: {str(e)}")
        
        # Avvia il thread di manutenzione
        maintenance_thread = threading.Thread(target=security_maintenance_task, daemon=True)
        maintenance_thread.start()
        log.info("✅ Task di manutenzione sicurezza avviato")
        
        # Verifica la memoria dichiarativa
        try:
            from .document_priority import prioritize_documents
            log.info("✅ Modulo di prioritizzazione documenti caricato")
            
            # Verificare la memoria dichiarativa
            memory_status = check_declarative_memory(cat)
            if memory_status:
                log.info("✅ Memoria dichiarativa verificata e pronta")
            else:
                log.warning("⚠️ Memoria dichiarativa non disponibile o vuota")
        except Exception as e:
            log.error(f"❌ Errore nella verifica della memoria dichiarativa: {str(e)}")
            
    except Exception as e:
        log.error(f"❌ Errore nell'avvio del task di manutenzione: {str(e)}")

@hook(priority=1)
def agent_prompt_prefix(prefix, cat):
    """
    Sostituisce completamente il prompt di sistema con istruzioni personalizzate.
    """
    try:
        # Recupera l'ID sessione dalla working_memory
        session_id = None
        if hasattr(cat, "working_memory"):
            session_id = getattr(cat.working_memory, "conversation_id", None)
        
        # Se non è presente nella working_memory, usa un valore di default
        if not session_id:
            session_id = "default"
        
        # Ottieni i dati del lead dalla working_memory
        email = ""
        regione = ""
        budget = ""
        nome_azienda = ""
        
        if hasattr(cat, "working_memory"):
            if hasattr(cat.working_memory, "email"):
                email = cat.working_memory.email
            if hasattr(cat.working_memory, "regione"):
                regione = cat.working_memory.regione
            if hasattr(cat.working_memory, "budget"):
                budget = cat.working_memory.budget
            if hasattr(cat.working_memory, "nome_azienda"):
                nome_azienda = cat.working_memory.nome_azienda
               
        # Formato base dei dati utente
        user_data = ""
        if email or regione or budget or nome_azienda:
            user_data += "\n\nDATI UTENTE:\n"
            if nome_azienda:
                user_data += f"- Azienda: {nome_azienda}\n"
            if regione:
                user_data += f"- Regione: {regione}\n"
            if budget:
                user_data += f"- Budget investimento: {budget}\n"
            if email:
                user_data += f"- Contatto: {email}\n"

        # Carica i contenuti dei prompt
        system_message = load_prompt_file("00_system_message.md")
        base_prompt = load_prompt_file("01_prompt_base.md")
        technical_prompt = load_prompt_file("02_prompt_technical.md")
        commercial_prompt = load_prompt_file("03_prompt_commercial.md")
        
        # Sostituisci i placeholders con i dati dal config.json
        assistant_name = config.get("assistant", {}).get("displayName", "Quinto")
        system_message = system_message.format(assistant_name=assistant_name)
        base_prompt = base_prompt.format(assistant_name=assistant_name)
        
        # IMPORTANTE: Restituisci un nuovo prompt completo, non aggiungere al prefix esistente
        return f"""{system_message}

{base_prompt}
{user_data}
{technical_prompt}
{commercial_prompt}
"""
        log.info(f"✅ Prompt di sistema completamente sostituito con istruzioni specifiche per Transizione 5.0")
    except Exception as e:
        log.error(f"❌ Errore nella sostituzione del prompt di sistema: {str(e)}")
        return prefix  # In caso di errore, mantieni il comportamento attuale

@hook(priority=100)
def before_cat_reads_message(user_message, cat):
    """
    Intercetta i messaggi in ingresso e garantisce che il conversation_id venga salvato
    nella working_memory per essere utilizzato successivamente.
    
    Args:
        user_message: Un oggetto UserMessage, non un dizionario come ipotizzato in precedenza
        cat: Istanza di StrayCat
    """
    try:
        log.info(f"🔍 Hook before_cat_reads_message attivato")
        
        # Estrai informazioni dall'oggetto messaggio
        text = ""
        user_id = ""
        conversation_id = None
        
        # Verifica se stiamo ricevendo un dizionario o un oggetto UserMessage
        if isinstance(user_message, dict) and "text" in user_message:
            text = user_message.get("text", "")
            user_id = user_message.get("user_id", "")
            conversation_id = user_message.get("conversation_id")
        elif hasattr(user_message, "text") and hasattr(user_message, "user_id"):
            text = getattr(user_message, "text", "")
            user_id = getattr(user_message, "user_id", "")
            conversation_id = getattr(user_message, "conversation_id", None)
        else:
            log.warning(f"⚠️ Formato messaggio non riconosciuto: {type(user_message)}")
            return user_message
        
        # Se non è specificato un conversation_id, usa user_id come fallback
        if not conversation_id and user_id:
            conversation_id = user_id
            log.info(f"ℹ️ Nessun conversation_id specifico, utilizzo user_id come fallback: {user_id}")
        
        # Log dettagliato
        log.info(f"📥 Messaggio ricevuto: text={text[:30]}..., " 
                 f"user_id={user_id}, conversation_id={conversation_id}")
        
        # Salva informazioni nella working_memory
        if hasattr(cat, "working_memory"):
            # Salva il messaggio originale
            cat.working_memory.original_user_message = {
                "text": text,
                "user_id": user_id,
                "conversation_id": conversation_id
            }
            
            # Salva il conversation_id per uso futuro
            if conversation_id:
                cat.working_memory.conversation_id = conversation_id
                log.info(f"✅ conversation_id={conversation_id} salvato nella working_memory")
                
                # Aggiorna la conversazione nel database
                try:
                    # Importa le funzioni necessarie
                    from .database_operations import get_conversation, create_conversation, update_conversation
                    
                    # Recupera o crea la conversazione
                    conversation = get_conversation(conversation_id)
                    if not conversation:
                        log.info(f"⚠️ Conversazione non trovata, creazione nuova conversazione: {conversation_id}")
                        data = {
                            "lead_data": {
                                "azienda_data": {},
                                "investimenti_data": {},
                                "contatto_data": {}
                            },
                            "messaggi": []
                        }
                        create_conversation(conversation_id, data)
                        conversation = get_conversation(conversation_id)
                    
                    # Aggiorna i messaggi
                    if conversation and "data" in conversation:
                        messaggi = conversation["data"].get("messaggi", [])
                        
                        # Aggiungi il messaggio dell'utente
                        messaggi.append({"role": "user", "content": text})
                        
                        # Aggiorna la conversazione
                        update_data = {"messaggi": messaggi}
                        success = update_conversation(conversation_id, update_data)
                        
                        if success:
                            log.info(f"✅ Messaggio utente aggiunto alla conversazione: {conversation_id}")
                        else:
                            log.error(f"❌ Errore nell'aggiornamento della conversazione: {conversation_id}")
                    
                    # Processa il messaggio per estrarre informazioni
                    try:
                        from .form_operations import process_user_message
                        extracted_info = process_user_message(conversation_id, text)
                        
                        if extracted_info:
                            log.info(f"✅ Informazioni estratte dal messaggio: {extracted_info}")
                            
                            # Registra evento analytics
                            try:
                                from .analytics_operations import log_analytics_event
                                log_analytics_event(
                                    evento="informazioni_estratte_automaticamente",
                                    session_id=conversation_id,
                                    dati={"estratto": extracted_info}
                                )
                            except Exception as analytics_error:
                                log.warning(f"⚠️ Errore nel log analytics: {str(analytics_error)}")
                    except Exception as extract_error:
                        log.warning(f"⚠️ Errore nell'estrazione delle informazioni: {str(extract_error)}")
                except Exception as db_error:
                    log.error(f"❌ Errore nell'aggiornamento del database: {str(db_error)}")
            else:
                log.warning(f"⚠️ Nessun conversation_id trovato nel messaggio")
        else:
            log.warning(f"⚠️ cat.working_memory non disponibile")
            
        # Mantieni l'oggetto messaggio originale invariato
        return user_message
    except Exception as e:
        log.error(f"❌ Errore nell'hook before_cat_reads_message: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return user_message

@hook
def before_cat_sends_message(message, cat):
    """
    Intercetta i messaggi in uscita e garantisce che mantengano il conversation_id originale.
    Salva anche la risposta dell'AI nella conversazione nel database.
    
    Args:
        message: Un oggetto CatMessage o un dizionario
        cat: Istanza di StrayCat
    """
    try:
        log.info(f"🔍 Hook before_cat_sends_message attivato")
        
        # Estrai informazioni dal messaggio in uscita
        ai_content = ""
        user_id = ""
        
        # Verifica se stiamo lavorando con un dizionario o un oggetto CatMessage
        if isinstance(message, dict):
            ai_content = message.get("content", "")
            user_id = message.get("user_id", "")
        elif hasattr(message, "content") and hasattr(message, "user_id"):
            ai_content = getattr(message, "content", "")
            user_id = getattr(message, "user_id", "")
        else:
            log.warning(f"⚠️ Formato messaggio non riconosciuto: {type(message)}")
            # Se non riusciamo a estrarre il contenuto, restituisci il messaggio invariato
            return message
        
        # Recupera il conversation_id dalla working_memory
        conversation_id = None
        if hasattr(cat, "working_memory") and hasattr(cat.working_memory, "conversation_id"):
            conversation_id = cat.working_memory.conversation_id
            log.info(f"📤 Trovato conversation_id={conversation_id} nella working_memory")
        
        # Se non abbiamo ancora un conversation_id, fallback su user_id
        if not conversation_id and user_id:
            conversation_id = user_id
            log.info(f"📤 Nessun conversation_id trovato, usando user_id={user_id} come fallback")
        
        # Se abbiamo un conversation_id, aggiorna la conversazione nel database
        if conversation_id and ai_content:
            try:
                # Importa le funzioni necessarie
                from .database_operations import get_conversation, create_conversation, update_conversation
                
                # Recupera o crea la conversazione
                conversation = get_conversation(conversation_id)
                if not conversation:
                    # Crea una nuova conversazione
                    data = {
                        "lead_data": {
                            "azienda_data": {},
                            "investimenti_data": {},
                            "contatto_data": {}
                        },
                        "messaggi": []
                    }
                    create_conversation(conversation_id, data)
                    conversation = get_conversation(conversation_id)
                
                if conversation and "data" in conversation:
                    # Recupera i messaggi esistenti
                    messaggi = conversation["data"].get("messaggi", [])
                    
                    # Verifica se l'ultimo messaggio è già questa risposta per evitare duplicati
                    is_duplicate = False
                    if messaggi and messaggi[-1].get("role") == "assistant" and messaggi[-1].get("content") == ai_content:
                        is_duplicate = True
                    
                    # Aggiungi il messaggio dell'AI solo se non è un duplicato
                    if not is_duplicate:
                        messaggi.append({"role": "assistant", "content": ai_content})
                        
                        # Aggiorna la conversazione
                        update_data = {"messaggi": messaggi}
                        result = update_conversation(conversation_id, update_data)
                        
                        if result:
                            log.info(f"✅ Risposta AI salvata nella conversazione: {conversation_id}")
                            
                            # Registra evento analytics
                            try:
                                from .analytics_operations import log_analytics_event
                                log_analytics_event(
                                    evento="risposta_ai_salvata",
                                    session_id=conversation_id,
                                    dati={"num_messaggi": len(messaggi)}
                                )
                            except Exception as analytics_error:
                                log.warning(f"⚠️ Errore nel log analytics: {str(analytics_error)}")
                        else:
                            log.error(f"❌ Errore nell'aggiornamento della conversazione")
                    else:
                        log.info(f"ℹ️ Risposta AI già presente nella conversazione, nessun duplicato aggiunto")
            except Exception as db_error:
                log.error(f"❌ Errore nell'aggiornamento del database: {str(db_error)}")
                import traceback
                log.error(traceback.format_exc())
        
        # Imposta il conversation_id nel messaggio in uscita, se possibile
        try:
            if isinstance(message, dict) and conversation_id:
                message["conversation_id"] = conversation_id
                log.info(f"✅ Impostato conversation_id={conversation_id} nel messaggio in uscita (dict)")
            elif hasattr(message, "__dict__") and conversation_id:
                message.__dict__["conversation_id"] = conversation_id
                log.info(f"✅ Impostato conversation_id={conversation_id} nel messaggio in uscita (__dict__)")
        except Exception as attr_error:
            log.warning(f"⚠️ Errore nell'impostazione del conversation_id: {str(attr_error)}")
        
        return message
    except Exception as e:
        log.error(f"❌ Errore nell'hook before_cat_sends_message: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return message