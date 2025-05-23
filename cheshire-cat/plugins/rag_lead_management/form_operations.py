"""Operazioni per la gestione del form conversazionale."""
import os
import re
import uuid
import json
from openai import OpenAI
from cat.log import log
from datetime import datetime
from typing import Dict, Any, List, Optional

from .utils import load_prompt_file
from .database_operations import (
    create_conversation,
    get_conversation,
    update_lead,
    finalize_lead_from_conversation,
    log_analytics_event
)

# Inizializza il client OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def extract_information_openai(text):
    """Estrae informazioni dal testo usando OpenAI gpt-4o-mini"""
    if not text or len(text.strip()) < 10:
        return {}  # Testo troppo breve, non estrarre nulla
        
    try:
        # Carica il prompt da file invece di averlo hardcoded
        prompt_template = load_prompt_file("08_prompt_extraction.md")
        
        # Inserisci il testo nel template
        prompt = prompt_template.format(text=text)
        
        # Chiamata API a OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sei un assistente specializzato nell'estrazione di informazioni strutturate in formato JSON. Presta particolare attenzione all'estrazione del ruolo della persona."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=300,
            response_format={"type": "json_object"}  # Forza output in formato JSON
        )
        
        # Estrai la risposta
        json_response = response.choices[0].message.content
        
        # Converti in dizionario Python
        extracted_info = json.loads(json_response)
        
        log.info(f"✅ Informazioni estratte con OpenAI: {extracted_info}")
        return extracted_info
        
    except Exception as e:
        log.error(f"❌ Errore nell'estrazione con OpenAI: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return {}
    

def process_user_message(session_id, user_message, cat=None):
    """Elabora il messaggio dell'utente e aggiorna la conversazione"""
    # Imposta il conversation_id e user_id nella working memory usando notazione dot
    if cat and hasattr(cat, "working_memory"):
        # Usa setattr invece della notazione dizionario
        setattr(cat.working_memory, "conversation_id", session_id)
        setattr(cat.working_memory, "user_id", session_id)
        log.info(f"🔄 Impostato conversation_id={session_id} e user_id={session_id} nella working_memory")
    
    # Estrai informazioni dal messaggio usando OpenAI
    extracted_info = extract_information_openai(user_message)
    
    if not extracted_info:
        log.info(f"ℹ️ Nessuna informazione estratta dal messaggio")
        return None
    
    # Recupera la conversazione esistente
    from .database_operations import get_conversation
    conversation = get_conversation(session_id)
    
    if not conversation:
        # Crea una nuova conversazione se non esiste
        log.info(f"🆕 Creazione nuova conversazione per session_id={session_id}")
        from .database_operations import create_conversation
        conversation_data = {
            "messaggi": [{"role": "user", "content": user_message}],
            "lead_data": {
                "azienda_data": {},
                "contatto_data": {},
                "investimenti_data": {}
            }
        }
        create_conversation(session_id, conversation_data)
        conversation = get_conversation(session_id)
        if not conversation:
            log.error(f"❌ Impossibile creare una nuova conversazione per session_id={session_id}")
            return None
    
    # Usa la conversazione esistente
    conversation_data = conversation["data"]
    
    # Assicurati che lead_data esista con la struttura corretta
    if "lead_data" not in conversation_data:
        conversation_data["lead_data"] = {
            "azienda_data": {},
            "contatto_data": {},
            "investimenti_data": {}
        }
        
    # Assicurati che tutti i sottodizionari esistano
    if "azienda_data" not in conversation_data["lead_data"]:
        conversation_data["lead_data"]["azienda_data"] = {}
    if "contatto_data" not in conversation_data["lead_data"]:
        conversation_data["lead_data"]["contatto_data"] = {}
    if "investimenti_data" not in conversation_data["lead_data"]:
        conversation_data["lead_data"]["investimenti_data"] = {}
    
    # Organizza le informazioni estratte nelle categorie appropriate
    for key, value in extracted_info.items():
        if value is None:
            continue  # Salta valori nulli
        
        if key in ['nome_azienda', 'dimensione', 'regione', 'settore']:
            conversation_data["lead_data"]["azienda_data"][key] = value
        elif key in ['email', 'telefono', 'ruolo', 'nome', 'cognome']:
            conversation_data["lead_data"]["contatto_data"][key] = value
        elif key in ['budget', 'tipo_investimento', 'tempistiche']:
            conversation_data["lead_data"]["investimenti_data"][key] = value
    
    # Log per debug
    log.info(f"🔄 Lead data aggiornato: {conversation_data['lead_data']}")
    
    # Aggiorna la conversazione nel database
    from .database_operations import create_conversation
    create_conversation(session_id, conversation_data)
    
    # Registra l'evento analytics
    from .database_operations import log_analytics_event
    log_analytics_event(
        evento="aggiornamento_lead",
        session_id=session_id,
        dati={"lead_data": conversation_data["lead_data"], "estratto_da": "openai"}
    )
    
    log.info(f"✅ Dati del lead aggiornati con successo per session_id={session_id}")
    return extracted_info


def save_lead_data(azienda=None, dimensione=None, settore=None, regione=None,
                 investimento=None, budget=None, tempistiche=None,
                 nome=None, cognome=None, ruolo=None,
                 email=None, telefono=None, session_id=None, cat=None):
    """
    Salva i dati del lead nel sistema.
    
    Args:
        azienda: Nome dell'azienda
        dimensione: Dimensione dell'azienda (piccola, media, grande)
        settore: Settore dell'azienda
        regione: Regione dell'azienda
        investimento: Tipo di investimento
        budget: Budget previsto per l'investimento
        tempistiche: Tempistiche previste per l'investimento
        nome: Nome del contatto
        cognome: Cognome del contatto
        ruolo: Ruolo del contatto nell'azienda
        email: Indirizzo email del contatto
        telefono: Numero di telefono del contatto
        session_id: ID di sessione della conversazione
        cat: Istanza di Cheshire Cat
        
    Returns:
        Dict: Risultato dell'operazione
    """
    try:
        # Importa il modulo di sicurezza
        from .security import security
        
        # Se non è specificato l'ID di sessione, utilizza quello corrente
        if not session_id and cat:
            session_id = cat.working_memory.get("conversation_id", "default")
        
        if not session_id:
            session_id = str(uuid.uuid4())
            log.warning(f"⚠️ Nessun session_id fornito, generato nuovo ID: {session_id}")
        
        # Validazione dati sensibili
        if email and not security.validate_email(email):
            log.warning(f"⚠️ Email non valida o da dominio temporaneo: {email}")
            return {
                "success": False, 
                "error": "Email non valida o da dominio temporaneo. Per favore, utilizza un indirizzo email valido."
            }
            
        # Sanitizzazione degli input testuali
        if azienda:
            azienda = security.sanitize_input(azienda)
        if settore:
            settore = security.sanitize_input(settore)
        if regione:
            regione = security.sanitize_input(regione)
        if investimento:
            investimento = security.sanitize_input(investimento)
        if nome:
            nome = security.sanitize_input(nome)
        if cognome:
            cognome = security.sanitize_input(cognome)
        if ruolo:
            ruolo = security.sanitize_input(ruolo)
        if telefono:
            # Sanitizzazione specifica per numeri di telefono
            telefono = re.sub(r'[^\d\+\-\s\(\)]', '', telefono)
        
        # Validazione dimensioni azienda
        if dimensione and dimensione.lower() not in ["piccola", "media", "grande"]:
            dimensione = None
        
        # Recupera la conversazione attiva o crea una nuova
        conversation = get_conversation(session_id)
        
        if not conversation:
            # Crea una nuova conversazione
            conversation_data = {
                "lead_data": {
                    "azienda_data": {},
                    "investimenti_data": {},
                    "contatto_data": {}
                }
            }
        else:
            # Usa la conversazione esistente
            conversation_data = conversation["data"]
        
        # Assicurati che la struttura dei dati sia corretta
        if "lead_data" not in conversation_data:
            conversation_data["lead_data"] = {
                "azienda_data": {},
                "investimenti_data": {},
                "contatto_data": {}
            }
        
        lead_data = conversation_data["lead_data"]
        
        # Aggiorna i dati dell'azienda
        azienda_data = lead_data.get("azienda_data", {})
        if azienda:
            azienda_data["nome_azienda"] = azienda
        if dimensione:
            azienda_data["dimensione"] = dimensione
        if settore:
            azienda_data["settore"] = settore
        if regione:
            azienda_data["regione"] = regione
        lead_data["azienda_data"] = azienda_data
        
        # Aggiorna i dati dell'investimento
        investimenti_data = lead_data.get("investimenti_data", {})
        if investimento:
            investimenti_data["tipo_investimento"] = investimento
        if budget:
            investimenti_data["budget"] = budget
        if tempistiche:
            investimenti_data["tempistiche"] = tempistiche
        lead_data["investimenti_data"] = investimenti_data
        
        # Aggiorna i dati del contatto
        contatto_data = lead_data.get("contatto_data", {})
        if nome:
            contatto_data["nome"] = nome
        if cognome:
            contatto_data["cognome"] = cognome
        if ruolo:
            contatto_data["ruolo"] = ruolo
        if email:
            contatto_data["email"] = email
        if telefono:
            contatto_data["telefono"] = telefono
        lead_data["contatto_data"] = contatto_data
        
        # Aggiorna la conversazione
        create_conversation(session_id, conversation_data)
        
        # Registra l'evento analytics
        log_analytics_event(
            evento="aggiornamento_lead",
            session_id=session_id,
            dati={"lead_data": lead_data, "origine": "tool"}
        )
        
        # Registra evento di sicurezza se ci sono dati di contatto
        if email or telefono:
            security.log_security_event(
                "contatto_salvato", 
                session_id, 
                {"azienda": azienda, "nome": nome}, 
                "info"
            )
        
        return {
            "success": True,
            "message": "Dati del lead aggiornati con successo",
            "session_id": session_id
        }
    except Exception as e:
        log.error(f"❌ Errore nel salvataggio dei dati del lead: {str(e)}")
        return {"success": False, "error": str(e)}

def create_lead_from_conversation(session_id, cat=None):
    """
    Crea un nuovo lead nel database utilizzando i dati raccolti nella conversazione.
    
    Args:
        session_id: ID di sessione della conversazione
        cat: Istanza di Cheshire Cat
        
    Returns:
        Dict: Risultato dell'operazione
    """
    try:
        # Se non è specificato l'ID di sessione, utilizza quello corrente
        if not session_id and cat:
            session_id = cat.working_memory.get("conversation_id", "default")
        
        if not session_id:
            return {"success": False, "error": "ID sessione non specificato"}
        
        # Verifica che ci siano abbastanza dati nella conversazione
        result = finalize_lead_from_conversation(session_id)
        
        if not result["success"]:
            log.warning(f"⚠️ Impossibile creare lead: {result['error']}")
            return result
        
        lead_id = result["lead_id"]
        
        log.info(f"✅ Lead creato con successo: ID {lead_id}")
        
        return {
            "success": True,
            "lead_id": lead_id,
            "message": "Lead creato con successo"
        }
    except Exception as e:
        log.error(f"❌ Errore nella creazione del lead: {str(e)}")
        return {"success": False, "error": str(e)}

def evaluate_conversation_completion(session_id):
    """
    Valuta quanto è completa la conversazione e quali dati mancano.
    
    Args:
        session_id: ID di sessione della conversazione
        
    Returns:
        Dict: Risultato dell'analisi
    """
    try:
        # Recupera la conversazione
        conversation = get_conversation(session_id)
        
        if not conversation:
            return {
                "complete": False,
                "missing_fields": ["conversazione"],
                "completion_percentage": 0,
                "message": "Conversazione non trovata"
            }
        
        # Recupera i dati del lead
        lead_data = conversation["data"].get("lead_data", {})
        
        # Carica i requisiti del form da un file Markdown
        form_requirements = load_prompt_file("09_prompt_form_requirements.md")
        
        # Analizza il testo per estrarre i campi obbligatori
        # (Questo è un approccio semplificato - potresti voler analizzare il file in modo più robusto)
        required_fields = {
            "azienda_data": ["nome_azienda"],
            "contatto_data": ["email", "telefono"],  # Basta uno dei due
            "investimenti_data": ["budget"]
        }
        
        # Verifica quali campi sono presenti
        missing_fields = []
        
        # Controlla azienda_data
        azienda_data = lead_data.get("azienda_data", {})
        for field in required_fields["azienda_data"]:
            if field not in azienda_data or not azienda_data[field]:
                missing_fields.append(f"azienda.{field}")
        
        # Controlla contatto_data (email o telefono sono sufficienti)
        contatto_data = lead_data.get("contatto_data", {})
        if not (contatto_data.get("email") or contatto_data.get("telefono")):
            missing_fields.append("contatto.email/telefono")
        
        # Controlla investimenti_data
        investimenti_data = lead_data.get("investimenti_data", {})
        for field in required_fields["investimenti_data"]:
            if field not in investimenti_data or not investimenti_data[field]:
                missing_fields.append(f"investimenti.{field}")
        
        # Calcola la percentuale di completamento
        total_fields = len(required_fields["azienda_data"]) + 1 + len(required_fields["investimenti_data"])
        filled_fields = total_fields - len(missing_fields)
        completion_percentage = int((filled_fields / total_fields) * 100)
        
        # Prepara la risposta
        return {
            "complete": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "completion_percentage": completion_percentage,
            "azienda_data": azienda_data,
            "contatto_data": contatto_data,
            "investimenti_data": investimenti_data
        }
    except Exception as e:
        log.error(f"❌ Errore nella valutazione del completamento: {str(e)}")
        return {
            "complete": False,
            "missing_fields": ["errore"],
            "completion_percentage": 0,
            "message": f"Errore: {str(e)}"
        }

def get_conversation_phase(session_id):
    """
    Determina la fase corrente della conversazione.
    
    Args:
        session_id: ID di sessione della conversazione
        
    Returns:
        str: Fase della conversazione (accoglienza, approfondimento, qualificazione, formalizzazione)
    """
    try:
        # Recupera la conversazione
        conversation = get_conversation(session_id)
        
        if not conversation:
            # Se non c'è conversazione, siamo in fase di accoglienza
            return "accoglienza"
        
        # Valuta il completamento
        evaluation = evaluate_conversation_completion(session_id)
        completion_percentage = evaluation.get("completion_percentage", 0)
        
        # Determina la fase in base alla percentuale di completamento
        if completion_percentage < 25:
            return "accoglienza"
        elif completion_percentage < 50:
            return "approfondimento"
        elif completion_percentage < 75:
            return "qualificazione"
        else:
            return "formalizzazione"
    except Exception as e:
        log.error(f"❌ Errore nella determinazione della fase: {str(e)}")
        return "accoglienza"  # Default in caso di errore