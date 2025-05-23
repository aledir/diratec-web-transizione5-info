"""Funzionalità per la sicurezza e la validazione dei messaggi."""
from cat.log import log
import re

def is_off_topic(text):
    """
    Verifica se un messaggio dell'utente è fuori tema (non correlato alla Transizione 5.0)
    
    Args:
        text: Il testo del messaggio
        
    Returns:
        bool: True se il messaggio è probabilmente fuori tema, False altrimenti
    """
    # Lista di parole chiave pertinenti alla Transizione 5.0
    relevant_keywords = [
        "transizione", "t5.0", "t5", "5.0", "transizione 5.0", "transizione5.0",
        "credito", "imposta", "credito d'imposta", "agevolazione", "agevolazioni",
        "fiscale", "bando", "incentivo", "incentivi", "investimento", "investimenti",
        "certificazione", "certificazioni", "sostenibilità", "sostenibile", 
        "energia", "energetico", "fotovoltaico", "pannelli", "solare",
        "digitale", "digitalizzazione", "automazione", "robot", "robotica",
        "risparmio", "energetico", "mimit", "ministero", "GSE", "Gestore",
        "PNRR", "decreto", "attuativo", "legge", "bilancio", "2025",
        "documentazione", "scadenza", "procedura", "requisiti", "ammissibilità",
        "spese", "ammissibili", "rendicontazione", "progetto", "budget"
    ]
    
    # Lista di argomenti non pertinenti o potenziali tentativi di abuso
    irrelevant_topics = [
        r"\bporno", r"\bsex", r"\bcasino", r"\bgioco d'azzardo", r"\bbet", r"\bscommesse",
        r"\bhacker", r"\bhacking", r"\binsulta", r"\boffendi", r"\bstupido",
        r"\brazzismo", r"\bodio", r"\bdiscriminazione", r"\bpolitica",
        r"\belezion", r"\bgoverno", r"\bpartit", r"\bscrivimi una poesia",
        r"\bracconta una storia", r"\bfai finta", r"\bpretendi", r"\binterpreta",
        r"\bchat gpt", r"\bopenai", r"\bai model", r"\ballucina", r"\bcercami",
        r"\btrovami", r"\bcercatore", r"\bmotore di ricerca", r"\bricetta",
        r"\bviaggio", r"\bhotel", r"\bprenotazione", r"\bmeteo", r"\btempo",
        r"\bgioco", r"\bmusica", r"\bfilm", r"\bserie tv", r"\bsport",
        r"\bcalcio", r"\bcryptotruffa", r"\bspeculazione", r"\binvestimento speculativo"
    ]
    
    # Controlla se il messaggio contiene almeno una parola chiave rilevante
    has_relevant_keyword = any(keyword.lower() in text.lower() for keyword in relevant_keywords)
    
    # Controlla se il messaggio contiene un argomento non pertinente
    has_irrelevant_topic = any(re.search(pattern, text.lower()) for pattern in irrelevant_topics)
    
    # Se il testo è molto breve (meno di 4 parole), consideriamolo potenzialmente valido
    # per permettere domande brevi come "Cos'è la Transizione 5.0?"
    if len(text.split()) < 4:
        return False
    
    # Se contiene un argomento non pertinente, consideriamolo fuori tema
    if has_irrelevant_topic:
        log.warning(f"⚠️ Rilevato potenziale messaggio fuori tema (argomento non pertinente)")
        return True
    
    # Se non contiene parole chiave rilevanti ed è più lungo di un semplice saluto,
    # consideriamolo probabilmente fuori tema
    if not has_relevant_keyword and len(text.split()) > 7:
        log.warning(f"⚠️ Rilevato potenziale messaggio fuori tema (mancano parole chiave rilevanti)")
        return True
    
    return False

def generate_stay_on_topic_response():
    """
    Genera una risposta gentile per reindirizzare l'utente sull'argomento
    
    Returns:
        str: Messaggio di risposta
    """
    return """Mi dispiace, ma posso fornirti assistenza solo su argomenti relativi alla Transizione 5.0.

Posso aiutarti con:
- Informazioni sulle agevolazioni fiscali della Transizione 5.0
- Requisiti e procedure per accedere ai crediti d'imposta
- Documentazione necessaria per le certificazioni
- Chiarimenti sugli investimenti ammissibili
- Modalità di calcolo delle aliquote del credito
- Scadenze e tempistiche per le domande

Se hai domande su questi argomenti, sarò felice di aiutarti!"""

def filter_offensive_content(text):
    """
    Filtra contenuti potenzialmente offensivi o inappropriati
    
    Args:
        text: Il testo da filtrare
        
    Returns:
        str: Il testo filtrato se necessario, altrimenti il testo originale
    """
    # Parole o frasi da censurare
    offensive_patterns = [
        r"\bstronz[oi]\b", r"\bcazz[oi]\b", r"\bmerda\b", r"\bvaffanculo\b", 
        r"\bfanculo\b", r"\bfiglio di\b", r"\bputtana\b", r"\bidiota\b",
        r"\bdeficiente\b", r"\bscemo\b", r"\bcretino\b"
    ]
    
    # Verifica se il testo contiene contenuti offensivi
    contains_offensive = any(re.search(pattern, text.lower()) for pattern in offensive_patterns)
    
    if contains_offensive:
        log.warning("⚠️ Rilevato potenziale contenuto offensivo nel messaggio")
        # Sostituisci il testo con un messaggio generico
        return "Mi dispiace, ma non posso elaborare messaggi con linguaggio inappropriato. Come posso aiutarti con la Transizione 5.0?"
    
    return text  # Restituisci il testo originale se non contiene contenuti offensivi