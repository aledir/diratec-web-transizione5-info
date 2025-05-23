"""Tool functions per il plugin Lead Management."""
from cat.mad_hatter.decorators import tool
from cat.log import log

from .form_operations import save_lead_data as save_lead_data_function
from .form_operations import create_lead_from_conversation

@tool
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
    return save_lead_data_function(
        azienda, dimensione, settore, regione,
        investimento, budget, tempistiche,
        nome, cognome, ruolo,
        email, telefono, session_id, cat
    )

@tool
def create_lead(session_id=None, cat=None):
    """
    Crea un nuovo lead nel database utilizzando i dati raccolti nella conversazione.

    Args:
        session_id: ID di sessione della conversazione
        cat: Istanza di Cheshire Cat

    Returns:
        Dict: Risultato dell'operazione
    """
    return create_lead_from_conversation(session_id, cat)