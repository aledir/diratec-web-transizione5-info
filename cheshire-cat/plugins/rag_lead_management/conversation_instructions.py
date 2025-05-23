"""Istruzioni conversazionali per guidare il comportamento di Cheshire Cat."""
from cat.log import log
from .form_operations import get_conversation_phase, evaluate_conversation_completion
from .utils import load_prompt_file

def get_phase_prompt(session_id):
    """
    Genera il prompt per guidare il comportamento del modello linguistico
    in base alla fase corrente della conversazione.
    
    Args:
        session_id: ID sessione della conversazione
        
    Returns:
        str: Prompt con istruzioni specifiche per la fase
    """
    # Determina la fase corrente
    phase = get_conversation_phase(session_id)
    log.info(f"🔄 Fase conversazionale attuale: {phase}")
    
    # Ottieni lo stato di completamento
    evaluation = evaluate_conversation_completion(session_id)
    
    # Prepara i dati per il template
    azienda_data = evaluation.get("azienda_data", {})
    investimenti_data = evaluation.get("investimenti_data", {})
    contatto_data = evaluation.get("contatto_data", {})
    
    # Formatta i dati raccolti in modo leggibile
    collected_data = []
    missing_data = evaluation.get("missing_fields", [])
    
    if azienda_data.get("nome_azienda"):
        collected_data.append(f"Nome azienda: {azienda_data['nome_azienda']}")
    
    if azienda_data.get("dimensione"):
        collected_data.append(f"Dimensione: {azienda_data['dimensione']}")
        
    if azienda_data.get("settore"):
        collected_data.append(f"Settore: {azienda_data['settore']}")
        
    if azienda_data.get("regione"):
        collected_data.append(f"Regione: {azienda_data['regione']}")
    
    if investimenti_data.get("tipo_investimento"):
        collected_data.append(f"Tipo investimento: {investimenti_data['tipo_investimento']}")
        
    if investimenti_data.get("budget"):
        collected_data.append(f"Budget: {investimenti_data['budget']}")
        
    if investimenti_data.get("tempistiche"):
        collected_data.append(f"Tempistiche: {investimenti_data['tempistiche']}")
    
    if contatto_data.get("nome"):
        name_parts = [contatto_data.get("nome", "")]
        if contatto_data.get("cognome"):
            name_parts.append(contatto_data.get("cognome", ""))
        collected_data.append(f"Nome: {' '.join(name_parts)}")
        
    if contatto_data.get("ruolo"):
        collected_data.append(f"Ruolo: {contatto_data['ruolo']}")
        
    if contatto_data.get("email"):
        collected_data.append(f"Email: {contatto_data['email']}")
        
    if contatto_data.get("telefono"):
        collected_data.append(f"Telefono: {contatto_data['telefono']}")
    
    # Carica il contenuto delle fasi dal file
    phases_content = load_prompt_file("04_prompt_conversation_phases.md")
    
    # Estrai la sezione della fase corrente dal contenuto
    phase_markers = {
        "accoglienza": "## FASE 1: ACCOGLIENZA",
        "approfondimento": "## FASE 2: APPROFONDIMENTO",
        "qualificazione": "## FASE 3: QUALIFICAZIONE",
        "formalizzazione": "## FASE 4: FORMALIZZAZIONE"
    }
    
    # Trova la fase corrente nel contenuto
    phase_marker = phase_markers.get(phase)
    if not phase_marker:
        raise ValueError(f"Fase non riconosciuta: {phase}")
    
    if phase_marker not in phases_content:
        raise ValueError(f"Marker di fase '{phase_marker}' non trovato nel file prompt")
    
    # Estrai il contenuto della fase
    start_index = phases_content.find(phase_marker)
    
    # Trova il prossimo marker o la fine del file
    next_markers = [m for m in phase_markers.values() if m > phase_marker]
    end_index = len(phases_content)
    
    for marker in next_markers:
        marker_index = phases_content.find(marker)
        if marker_index > start_index and marker_index < end_index:
            end_index = marker_index
    
    # Estrai il contenuto della fase
    phase_content = phases_content[start_index:end_index].strip()
    
    # Prepara le stringhe per i dati raccolti e mancanti
    collected_str = "Nessun dato raccolto finora."
    if collected_data:
        collected_str = "\n- " + "\n- ".join(collected_data)
    
    missing_str = "Tutti i dati essenziali sono stati raccolti."
    if missing_data:
        missing_str = "\n- " + "\n- ".join(missing_data)
    
    # Costruisci il prompt finale
    formatted_prompt = f"""
{phase_content}

Dati già raccolti: {collected_str}
Dati mancanti: {missing_str}
"""
    
    log.info(f"✅ Generato prompt per la fase '{phase}'")
    return formatted_prompt

def get_next_question(session_id):
    """
    Suggerisce la prossima domanda da porre in base ai dati mancanti.
    
    Args:
        session_id: ID sessione della conversazione
        
    Returns:
        str: Domanda suggerita o None se non ci sono domande da suggerire
    """
    try:
        # Ottieni lo stato di completamento
        evaluation = evaluate_conversation_completion(session_id)
        missing_fields = evaluation.get("missing_fields", [])
        
        if not missing_fields:
            return None
        
        # Mappatura dei campi mancanti alle domande
        questions = {
            "azienda.nome_azienda": "Qual è il nome della tua azienda?",
            "contatto.email/telefono": "Qual è la tua email o numero di telefono per poterti ricontattare?",
            "investimenti.budget": "Hai già un'idea del budget che vorresti investire per questo progetto?"
        }
        
        # Verifica se ci sono campi mancanti per cui abbiamo domande
        for field in missing_fields:
            if field in questions:
                return questions[field]
        
        # Se non abbiamo domande specifiche, suggeriscine una generica
        if "azienda." in missing_fields[0]:
            return "Mi potresti dire qualcosa in più sulla tua azienda?"
        elif "investimenti." in missing_fields[0]:
            return "Puoi dirmi di più riguardo all'investimento che state considerando?"
        elif "contatto." in missing_fields[0]:
            return "Come possiamo contattarti per fornirti ulteriori informazioni?"
        
        return None
    
    except Exception as e:
        log.error(f"❌ Errore nella generazione della prossima domanda: {str(e)}")
        return None