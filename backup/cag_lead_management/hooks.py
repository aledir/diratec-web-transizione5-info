"""Hook functions per il plugin CAG Lead Management."""
import uuid
from cat.mad_hatter.decorators import hook
from cat.log import log

from .form_operations import extract_information, process_user_message
from .analytics_operations import log_analytics_event
from .database_operations import get_conversation, create_conversation
from .safety_checks import is_off_topic, generate_stay_on_topic_response, filter_offensive_content
from .security import check_message_security

@hook(priority=25)  # Priorità più bassa di cag_document_manager per non interferire con la KV-cache
def before_chat_completion(params, cat):
    """Processa il messaggio dell'utente prima della generazione della risposta"""
    try:
        # Recupera l'ID di sessione
        user_message = params.get("user_message", "")
        session_id = params.get("session_id", str(uuid.uuid4()))

        # Salva l'IP del client nella working memory se disponibile
        client_ip = "unknown"
        if hasattr(cat, 'request') and hasattr(cat.request, 'client'):
            client_ip = cat.request.client.host
        cat.working_memory["client_ip"] = client_ip
        
        # Registra l'evento analytics per il messaggio originale
        log_analytics_event(
            evento="nuovo_messaggio",
            session_id=session_id,
            dati={"messaggio": user_message}
        )

        # Controlla la sicurezza del messaggio
        security_check = check_message_security(user_message, session_id)
        
        # Se il messaggio deve essere bloccato, imposta la risposta predefinita
        if security_check["should_block"]:
            params["llm_response"] = security_check["response"]
            cat.working_memory["skip_llm_generation"] = True
            return params
        
        # Usa il messaggio sanitizzato
        params["user_message"] = security_check["sanitized_message"]

        # Estrai informazioni dal messaggio utente
        extracted_info = extract_information(params["user_message"])

        if extracted_info:
            # Aggiorna le informazioni della conversazione
            process_user_message(session_id, params["user_message"])
            log.info(f"📊 Informazioni estratte dal messaggio utente: {extracted_info}")
        
        log.info(f"✅ Preprocessing del messaggio utente completato (CAG Lead Management)")
        return params
    except Exception as e:
        log.error(f"❌ Errore nel processing del messaggio: {str(e)}")
        return params

@hook
def after_chat_completion(params, cat):
    """Processa la risposta dell'AI dopo la generazione"""
    try:
        # Recupera l'ID di sessione e la risposta
        session_id = params.get("session_id", "")
        ai_message = params.get("llm_response", "")
        
        if not session_id or not ai_message:
            return params
        
        # Controlla se dobbiamo saltare la generazione LLM (messaggio off-topic)
        if cat.working_memory.get("skip_llm_generation", False):
            # Puliamo il flag dopo averlo usato
            cat.working_memory["skip_llm_generation"] = False
            
            # Usa la risposta già impostata in before_chat_completion
            log.info(f"✅ Risposta predefinita utilizzata per messaggio off-topic")
            
            # Recupera la conversazione
            conversation = get_conversation(session_id)
            if conversation:
                # Aggiorna la conversazione con la risposta predefinita
                conversation_data = conversation["data"]
                if "messaggi" not in conversation_data:
                    conversation_data["messaggi"] = []
                
                # Aggiungi la risposta predefinita
                conversation_data["messaggi"].append({"role": "assistant", "content": ai_message})
                
                # Salva la conversazione aggiornata
                create_conversation(session_id, conversation_data)
                
                # Registra l'evento analytics
                log_analytics_event(
                    evento="risposta_off_topic",
                    session_id=session_id,
                    dati={"messaggio": ai_message}
                )
            
            return params
        
        # Recupera la conversazione
        conversation = get_conversation(session_id)
        if not conversation:
            return params
        
        # Aggiorna la conversazione con la risposta dell'AI
        conversation_data = conversation["data"]
        if "messaggi" not in conversation_data:
            conversation_data["messaggi"] = []
        
        # Aggiungi la risposta dell'AI
        conversation_data["messaggi"].append({"role": "assistant", "content": ai_message})
        
        # Salva la conversazione aggiornata
        create_conversation(session_id, conversation_data)
        
        # Registra l'evento analytics
        log_analytics_event(
            evento="risposta_ai",
            session_id=session_id,
            dati={"messaggio": ai_message}
        )
        
        log.info(f"✅ Risposta AI salvata nella conversazione (CAG Lead Management)")
        return params
    except Exception as e:
        log.error(f"❌ Errore nel processing della risposta: {str(e)}")
        return params