"""Endpoint API per CAG Lead Management."""
from cat.mad_hatter.decorators import endpoint
from cat.log import log

# Importa le operazioni necessarie
from .database_operations import get_leads_from_db, get_lead_details_from_db, update_lead_status_in_db
from .form_operations import evaluate_conversation_completion

@endpoint("/api/cag/leads")
def get_leads():
    """Endpoint per ottenere l'elenco dei lead"""
    try:
        log.info("🔄 Endpoint /api/cag/leads chiamato")
        return get_leads_from_db()
    except Exception as e:
        log.error(f"❌ Errore nel recupero dei lead: {str(e)}")
        return {"error": f"Errore nel recupero dei lead: {str(e)}", "status": 500}

@endpoint("/api/cag/lead/{lead_id}")
def get_lead_details(lead_id=None):
    """Endpoint per ottenere i dettagli di un lead specifico"""
    try:
        log.info(f"🔄 Endpoint /api/cag/lead/{lead_id} chiamato")
        result = get_lead_details_from_db(lead_id)
        if not result:
            return {"error": f"Lead non trovato: {lead_id}", "status": 404}
        return result
    except Exception as e:
        log.error(f"❌ Errore nel recupero dei dettagli del lead: {str(e)}")
        return {"error": f"Errore nel recupero dei dettagli del lead: {str(e)}", "status": 500}

@endpoint("/api/cag/lead/update/{lead_id}")
async def update_lead_status(request, lead_id=None):
    """Endpoint per aggiornare lo stato di un lead"""
    try:
        log.info(f"🔄 Endpoint /api/cag/lead/update/{lead_id} chiamato")
        data = await request.json()
        if "stato" not in data:
            return {"error": "Campo obbligatorio mancante: stato", "status": 400}
        
        success = update_lead_status_in_db(lead_id, data["stato"])
        if not success:
            return {"error": f"Lead non trovato: {lead_id}", "status": 404}
        
        return {"success": True, "id": lead_id}
    except Exception as e:
        log.error(f"❌ Errore nell'aggiornamento del lead: {str(e)}")
        return {"error": f"Errore nell'aggiornamento del lead: {str(e)}", "status": 500}

@endpoint("/api/cag/conversation/{session_id}/status")
def get_conversation_status(session_id=None):
    """Endpoint per verificare lo stato di completamento della conversazione"""
    try:
        log.info(f"🔄 Endpoint /api/cag/conversation/{session_id}/status chiamato")
        
        result = evaluate_conversation_completion(session_id)
        if not result:
            return {"error": "Conversazione non trovata", "status": 404}
        
        return {
            "success": True,
            "complete": result.get("complete", False),
            "completion_percentage": result.get("completion_percentage", 0),
            "missing_fields": result.get("missing_fields", [])
        }
    except Exception as e:
        log.error(f"❌ Errore nel recupero dello stato della conversazione: {str(e)}")
        return {"error": str(e), "status": 500}