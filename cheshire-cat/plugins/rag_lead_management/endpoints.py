# endpoints.py
from cat.mad_hatter.decorators import endpoint
from cat.log import log
from cat.auth.permissions import check_permissions
from pydantic import BaseModel
import uuid
from typing import Dict, Any, Optional

# Importa le operazioni necessarie
from .database_operations import get_leads_from_db, get_lead_details_from_db, update_lead_status_in_db, get_conversation, update_conversation
from .form_operations import extract_information_openai

class ExtractionInput(BaseModel):
    text: str
    process_message: bool = False
    session_id: Optional[str] = None

class LeadCreateInput(BaseModel):
    session_id: str

class LeadSaveInput(BaseModel):
    azienda: Optional[str] = None
    dimensione: Optional[str] = None
    settore: Optional[str] = None
    regione: Optional[str] = None
    investimento: Optional[str] = None
    budget: Optional[str] = None
    tempistiche: Optional[str] = None
    nome: Optional[str] = None
    cognome: Optional[str] = None
    ruolo: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    session_id: Optional[str] = None


@endpoint.get("/api/rag/leads")
def get_leads(cat=check_permissions("CONVERSATION", "READ")):
    """Endpoint per ottenere l'elenco dei lead"""
    try:
        return get_leads_from_db()
    except Exception as e:
        log.error(f"Errore nel recupero dei lead: {str(e)}")
        return {"error": f"Errore nel recupero dei lead: {str(e)}", "status": 500}

@endpoint.get("/api/rag/lead/{lead_id}")
def get_lead_details(lead_id, cat=check_permissions("CONVERSATION", "READ")):
    """Endpoint per ottenere i dettagli di un lead specifico"""
    try:
        result = get_lead_details_from_db(lead_id)
        if not result:
            return {"error": f"Lead non trovato: {lead_id}", "status": 404}
        return result
    except Exception as e:
        log.error(f"Errore nel recupero dei dettagli del lead: {str(e)}")
        return {"error": f"Errore nel recupero dei dettagli del lead: {str(e)}", "status": 500}

@endpoint.post("/api/rag/lead/update/{lead_id}")
def update_lead_status(lead_id, payload, cat=check_permissions("CONVERSATION", "WRITE")):
    """Endpoint per aggiornare lo stato di un lead"""
    try:
        if "stato" not in payload:
            return {"error": "Campo obbligatorio mancante: stato", "status": 400}
        
        success = update_lead_status_in_db(lead_id, payload["stato"])
        if not success:
            return {"error": f"Lead non trovato: {lead_id}", "status": 404}
        
        return {"success": True, "id": lead_id}
    except Exception as e:
        log.error(f"Errore nell'aggiornamento del lead: {str(e)}")
        return {"error": f"Errore nell'aggiornamento del lead: {str(e)}", "status": 500}

@endpoint.get("/api/rag/diagnostic")
def diagnostic():
    """Endpoint diagnostico per verificare che il plugin sia caricato"""
    return {
        "status": "Plugin is loaded",
        "plugin": "RAG Lead Management",
        "version": "1.0.0"
    }

#####################################################################
#
#
# ENDPOINT PER DEBUG
#
#
#
#####################################################################


# @endpoint.post("/api/rag/test-extraction")
# def test_extraction_post(payload: ExtractionInput, cat=check_permissions("CONVERSATION", "WRITE")):
#     """Endpoint di test per l'estrazione delle informazioni (POST)"""
#     try:
#         text = payload.text
#         session_id = payload.session_id or str(uuid.uuid4())
        
#         # Estrai informazioni
#         extracted_info = extract_information_openai(text)
        
#         # Se specificato, processa anche il messaggio utente
#         if payload.process_message:
#             from .form_operations import process_user_message
#             processed_result = process_user_message(session_id, text)
#             return {
#                 "extracted_info": extracted_info,
#                 "processed_result": processed_result,
#                 "session_id": session_id
#             }
        
#         return {
#             "extracted_info": extracted_info,
#             "session_id": session_id
#         }
#     except Exception as e:
#         log.error(f"Errore nel test di estrazione: {str(e)}")
#         import traceback
#         log.error(traceback.format_exc())
#         return {"error": f"Errore nel test di estrazione: {str(e)}", "status": 500}
    

@endpoint.post("/api/rag/test-extraction")
def test_extraction_post(payload: dict, cat=check_permissions("CONVERSATION", "WRITE")):
    """Endpoint di test per l'estrazione delle informazioni (POST)"""
    try:
        text = payload.get("text")
        process_message = payload.get("process_message", False)
        session_id = payload.get("session_id")
        
        if not text:
            return {"error": "Testo mancante", "success": False}
        
        # Se non viene fornito session_id, genera un UUID
        if not session_id:
            session_id = str(uuid.uuid4())
            log.info(f"🆔 Generato nuovo session_id: {session_id}")
            
        # Imposta il conversation_id e user_id nella working memory usando la notazione dot
        # (questo evita i deprecation warning nei log)
        if cat and hasattr(cat, "working_memory"):
            # Usa setattr invece della notazione dizionario
            setattr(cat.working_memory, "conversation_id", session_id)
            setattr(cat.working_memory, "user_id", session_id)  # Usare lo stesso valore come fallback
            log.info(f"🔄 Impostato conversation_id={session_id} e user_id={session_id} nella working_memory")
        
        # Estrai informazioni dal testo
        extracted_info = extract_information_openai(text)
        
        # Se richiesto, processa anche il messaggio
        if process_message:
            from .form_operations import process_user_message
            # Passa cat alla funzione process_user_message per condividere il contesto
            processed_result = process_user_message(session_id, text, cat)
            
            # Verifica lo stato conversazione
            from .database_operations import get_conversation
            conv = get_conversation(session_id)
            if conv:
                log.info(f"✅ Conversazione trovata dopo process_user_message, lead_data: {conv['data'].get('lead_data')}")
            else:
                log.warning(f"⚠️ Conversazione non trovata dopo process_user_message per session_id={session_id}")
            
            return {
                "success": True,
                "extracted_info": extracted_info,
                "processed": processed_result is not None,
                "session_id": session_id  # Importante restituire l'ID per riferimenti futuri
            }
        
        return {
            "success": True,
            "extracted_info": extracted_info,
            "session_id": session_id  # Importante restituire l'ID per riferimenti futuri
        }
    except Exception as e:
        log.error(f"❌ Errore nel test di estrazione: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return {"error": f"Errore nel test di estrazione: {str(e)}", "success": False}
    

@endpoint.post("/api/rag/lead/create")
def create_lead(payload: LeadCreateInput, cat=check_permissions("CONVERSATION", "WRITE")):
    """Endpoint per creare un lead a partire da una conversazione"""
    try:
        session_id = payload.session_id
        
        # Importa la funzione per creare il lead
        from .form_operations import create_lead_from_conversation
        
        # Crea il lead
        result = create_lead_from_conversation(session_id, cat)
        
        if not result["success"]:
            return {"error": result["error"], "status": 400}
        
        return {"success": True, "lead_id": result["lead_id"]}
    except Exception as e:
        log.error(f"Errore nella creazione del lead: {str(e)}")
        return {"error": f"Errore nella creazione del lead: {str(e)}", "status": 500}

@endpoint.post("/api/rag/lead/save")
def save_lead(payload: LeadSaveInput, cat=check_permissions("CONVERSATION", "WRITE")):
    """Endpoint per salvare i dati di un lead"""
    try:
        # Importa la funzione per salvare il lead
        from .form_operations import save_lead_data
        
        # Salva il lead
        result = save_lead_data(
            azienda=payload.azienda,
            dimensione=payload.dimensione,
            settore=payload.settore,
            regione=payload.regione,
            investimento=payload.investimento,
            budget=payload.budget,
            tempistiche=payload.tempistiche,
            nome=payload.nome,
            cognome=payload.cognome,
            ruolo=payload.ruolo,
            email=payload.email,
            telefono=payload.telefono,
            session_id=payload.session_id,
            cat=cat
        )
        
        return result
    except Exception as e:
        log.error(f"Errore nel salvataggio del lead: {str(e)}")
        return {"error": f"Errore nel salvataggio del lead: {str(e)}", "status": 500}
    

@endpoint.get("/api/rag/debug/get-conversation/{session_id}")
def debug_get_conversation(session_id, cat=check_permissions("CONVERSATION", "READ")):
    """Endpoint di debug per ottenere direttamente la conversazione"""
    try:
        # Recupera la conversazione
        conversation = get_conversation(session_id)
        
        if not conversation:
            return {"found": False, "session_id": session_id}
        
        return {"found": True, "conversation": conversation}
    except Exception as e:
        log.error(f"Errore nel recupero della conversazione: {str(e)}")
        return {"error": f"Errore nel recupero della conversazione: {str(e)}", "status": 500}
    
@endpoint.get("/api/rag/debug/create-conversation/{session_id}")
def debug_create_conversation(session_id, cat=check_permissions("CONVERSATION", "WRITE")):
    """Endpoint di debug per creare una conversazione direttamente"""
    try:
        # Prima verifica se la conversazione esiste
        existing = get_conversation(session_id)
        if existing:
            return {
                "already_exists": True,
                "conversation": existing
            }
        
        # Crea una nuova conversazione con dati minimi
        data = {
            "lead_data": {
                "azienda_data": {},
                "investimenti_data": {},
                "contatto_data": {}
            },
            "messaggi": []
        }
        
        # Usa create_conversation per la creazione iniziale
        from .database_operations import create_conversation
        result = create_conversation(session_id, data)
        
        if result:
            # Verifica che la conversazione sia stata creata
            new_conv = get_conversation(session_id)
            log.info(f"✅ Nuova conversazione creata: session_id {session_id}")
            return {
                "success": True,
                "conversation": new_conv
            }
        else:
            return {"success": False, "error": "Impossibile creare la conversazione"}
    except Exception as e:
        log.error(f"Errore nella creazione della conversazione di debug: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return {"error": f"Errore nella creazione della conversazione: {str(e)}", "status": 500}

@endpoint.post("/api/rag/debug/add-message-to-conversation")
def debug_add_message_to_conversation(payload: dict = None, cat=check_permissions("CONVERSATION", "WRITE")):
    """Endpoint di debug per aggiungere manualmente un messaggio a una conversazione"""
    try:
        # Controllo payload
        if not payload:
            return {"error": "Payload mancante", "status": 400}
            
        session_id = payload.get("session_id")
        user_message = payload.get("user_message", "")
        ai_message = payload.get("ai_message", "")
        
        if not session_id:
            return {"error": "Session ID mancante", "status": 400}
        
        # Log per debug
        log.info(f"📌 Richiesta di aggiunta messaggio: session_id={session_id}, user_message={user_message[:30]}..., ai_message={ai_message[:30]}...")
        
        # Recupera la conversazione
        conversation = get_conversation(session_id)
        if not conversation:
            return {"error": f"Conversazione non trovata: {session_id}", "status": 404}
        
        # Aggiorna i messaggi
        conversation_data = conversation["data"]
        if "messaggi" not in conversation_data:
            conversation_data["messaggi"] = []
        
        # Aggiungi messaggi
        if user_message:
            conversation_data["messaggi"].append({"role": "user", "content": user_message})
            log.info(f"📝 Aggiunto messaggio utente alla conversazione: {user_message[:50]}...")
        
        if ai_message:
            conversation_data["messaggi"].append({"role": "assistant", "content": ai_message})
            log.info(f"📝 Aggiunta risposta AI alla conversazione: {ai_message[:50]}...")
        
        # Salva la conversazione usando update_conversation
        success = update_conversation(session_id, conversation_data)
        
        if not success:
            return {"error": "Errore nell'aggiornamento della conversazione", "status": 500}
        
        # Recupera la conversazione aggiornata per verificare
        updated_conversation = get_conversation(session_id)
        
        return {
            "success": True,
            "before": conversation,
            "after": updated_conversation
        }
    except Exception as e:
        log.error(f"❌ Errore nell'aggiunta manuale del messaggio: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return {"error": str(e), "status": 500}