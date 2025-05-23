"""
Funzionalità di sicurezza di base per il plugin Lead Management.
"""
import re
import json
from datetime import datetime
from cat.log import log
from typing import Dict, Any, List, Optional

# Per evitare dipendenze circolari, importiamo in modo condizionale
# Le configurazioni base vengono definite qui come fallback se security_config.py non esiste
try:
    from .security_config import (MAX_MESSAGE_LENGTH, SUSPICIOUS_PATTERNS,
                                 DISPOSABLE_EMAIL_DOMAINS, FORBIDDEN_TOPICS,
                                 CORE_T5_KEYWORDS, RELEVANT_T5_KEYWORDS,
                                 SENSITIVE_FIELDS)
except ImportError:
    # Valori di default se security_config.py non è disponibile
    MAX_MESSAGE_LENGTH = 2000
    SUSPICIOUS_PATTERNS = [
        r"(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER).+(FROM|TABLE)",  # Possibili iniezioni SQL
        r"<script>|<\/script>|javascript:",  # Possibili XSS
        r"\bhacker\b|\bhack\b|\bvulnerabil",  # Discussioni su hacking
        r"cat\.working_memory|skip_llm_generation",  # Riferimenti a variabili interne
        r"token|api_key|password|credential",  # Tentativi di phishing
        r"/%[0-9A-F]{2}|\\x[0-9A-F]{2}",  # URL o Unicode encoding
    ]
    DISPOSABLE_EMAIL_DOMAINS = [
        "guerrillamail.com", "mailinator.com", "tempmail.com", 
        "10minutemail.com", "yopmail.com", "maildrop.cc",
        "temp-mail.org", "fakeinbox.com", "trashmail.com"
    ]
    FORBIDDEN_TOPICS = [
        r"\bporno", r"\bsex", r"\bcasino", r"\bgioco d'azzardo", 
        r"\bbet", r"\bscommesse", r"\bhacker", r"\bhacking",
        r"\brazzismo", r"\bodio", r"\bdiscriminazione", r"\bpolitica",
        r"\bchat gpt", r"\bopenai", r"\ballucina", r"\bllm\b",
        r"\btraduzione\b", r"\btraduci\b", r"\bracconta una storia",
        r"\bpoesia\b", r"\bcanzoni\b", r"\baiuto compiti"
    ]
    CORE_T5_KEYWORDS = [
        "transizione 5.0", "transizione5.0", "t5.0", "t5", "t 5.0",
        "credito d'imposta", "decreto attuativo", "certificazione"
    ]
    RELEVANT_T5_KEYWORDS = [
        "transizione", "5.0", "credito", "imposta", "agevolazione", "agevolazioni",
        "fiscale", "bando", "incentivo", "incentivi", "investimento", "investimenti",
        "certificazione", "certificazioni", "sostenibilità", "sostenibile", 
        "energia", "energetico", "fotovoltaico", "pannelli", "solare",
        "digitale", "digitalizzazione", "automazione", "robot", "robotica",
        "risparmio", "energetico", "mimit", "ministero", "GSE", "Gestore",
        "PNRR", "decreto", "attuativo", "legge", "bilancio", "2025",
        "documentazione", "scadenza", "procedura", "requisiti", "ammissibilità",
        "spese", "ammissibili", "rendicontazione", "progetto", "budget"
    ]
    SENSITIVE_FIELDS = [
        'password', 'token', 'secret', 'key', 'email', 
        'telefono', 'cellulare', 'carta', 'credit', 'cvv'
    ]

class SecurityManager:
    """Gestisce le operazioni di sicurezza di base."""
    
    def __init__(self):
        """Inizializza il gestore di sicurezza."""
        # Configurazione
        self.max_message_length = MAX_MESSAGE_LENGTH
        self.suspicious_patterns = SUSPICIOUS_PATTERNS
        self.disposable_email_domains = DISPOSABLE_EMAIL_DOMAINS
        self.forbidden_topics = FORBIDDEN_TOPICS
        self.core_t5_keywords = CORE_T5_KEYWORDS
        self.relevant_t5_keywords = RELEVANT_T5_KEYWORDS
        self.sensitive_fields = SENSITIVE_FIELDS
    
    def sanitize_input(self, text):
        """
        Sanitizza gli input per prevenire iniezioni
        
        Args:
            text: Testo da sanitizzare
            
        Returns:
            str: Testo sanitizzato
        """
        if not text:
            return ""
            
        # Limita la lunghezza
        if len(text) > self.max_message_length:
            text = text[:self.max_message_length]
            
        # Rimuove caratteri potenzialmente pericolosi
        # Mantiene lettere, numeri, punteggiatura comune e spazi
        sanitized = re.sub(r'[^\w\s.,;:?!()\-\'\"€]', '', text)
        
        return sanitized
    
    def is_suspicious_activity(self, text):
        """
        Verifica se un messaggio contiene pattern sospetti
        
        Args:
            text: Testo da analizzare
            
        Returns:
            bool: True se sospetto, False altrimenti
        """
        if not text:
            return False
            
        # Controlla tutti i pattern sospetti
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
                
        return False
    
    def validate_email(self, email):
        """
        Verifica che l'email sia valida e non usa domini temporanei
        
        Args:
            email: Indirizzo email da verificare
            
        Returns:
            bool: True se valida, False altrimenti
        """
        if not email:
            return False
            
        # Verifica formato base
        if not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            return False
            
        # Controlla se usa un dominio usa e getta
        domain = email.split('@')[-1].lower()
        if domain in self.disposable_email_domains:
            return False
            
        return True
    
    def is_off_topic(self, text):
        """
        Verifica avanzata se un messaggio è fuori tema
        
        Args:
            text: Testo da analizzare
            
        Returns:
            bool: True se fuori tema, False altrimenti
        """
        if not text:
            return False
            
        # Normalizza il testo per i confronti
        text_lower = text.lower()
        
        # Se contiene almeno una parola chiave centrale, è probabilmente in tema
        if any(keyword.lower() in text_lower for keyword in self.core_t5_keywords):
            return False
        
        # Se contiene un argomento proibito, è fuori tema
        if any(re.search(pattern, text_lower) for pattern in self.forbidden_topics):
            return True
        
        # Se il testo è molto breve (meno di 4 parole), consideriamolo potenzialmente valido
        if len(text.split()) < 4:
            return False
        
        # Conta quante parole chiave rilevanti sono presenti
        relevance_count = sum(1 for keyword in self.relevant_t5_keywords if keyword.lower() in text_lower)
        
        # Se il messaggio è lungo ma non contiene parole chiave rilevanti, è probabilmente fuori tema
        if len(text.split()) > 10 and relevance_count == 0:
            return True
        
        # Se il messaggio è di lunghezza media ma ha poche parole chiave, potrebbe essere fuori tema
        if len(text.split()) > 20 and relevance_count < 2:
            return True
        
        return False
    
    def generate_stay_on_topic_response(self):
        """
        Genera una risposta per reindirizzare l'utente sull'argomento
        
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
    
    def mask_sensitive_data(self, data, fields_to_mask=None):
        """
        Maschera dati sensibili nei log per prevenire data leakage
        
        Args:
            data: Dati da mascherare (dict o str)
            fields_to_mask: Lista di campi da mascherare
            
        Returns:
            I dati con informazioni sensibili mascherate
        """
        if fields_to_mask is None:
            fields_to_mask = self.sensitive_fields
        
        if isinstance(data, dict):
            masked_data = data.copy()
            for key, value in masked_data.items():
                if isinstance(value, dict):
                    masked_data[key] = self.mask_sensitive_data(value, fields_to_mask)
                elif isinstance(value, str):
                    for field in fields_to_mask:
                        if field.lower() in key.lower():
                            if len(value) > 4:
                                masked_data[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
                            else:
                                masked_data[key] = '****'
            return masked_data
        elif isinstance(data, str):
            # Maschera email e numeri di telefono in stringhe
            masked = data
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'(?:\+\d{1,3})?(?:\d[ .-]?){8,12}'
            
            # Maschera email
            masked = re.sub(email_pattern, lambda m: m.group(0)[:3] + '***@***' + m.group(0).split('@')[-1][-3:], masked)
            
            # Maschera telefono
            masked = re.sub(phone_pattern, lambda m: m.group(0)[:3] + '****' + m.group(0)[-2:], masked)
            
            return masked
        else:
            return data
    
    def log_security_event(self, evento, session_id, dati=None, severity="warning"):
        """
        Registra un evento di sicurezza
        
        Args:
            evento: Tipo di evento
            session_id: ID della sessione
            dati: Dati aggiuntivi
            severity: Livello di gravità (info, warning, error)
        """
        try:
            # Importa localmente per evitare dipendenze circolari
            from ..analytics_operations import log_analytics_event
            
            # Prepara i dati dell'evento
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "severity": severity
            }
            
            # Aggiungi dati aggiuntivi se presenti
            if dati:
                # Maschera dati sensibili
                masked_dati = self.mask_sensitive_data(dati)
                event_data.update(masked_dati)
            
            # Logga l'evento
            if severity == "warning":
                log.warning(f"⚠️ {evento}: session_id={session_id}")
            elif severity == "error":
                log.error(f"🚨 {evento}: session_id={session_id}")
            else:
                log.info(f"ℹ️ {evento}: session_id={session_id}")
            
            # Registra nel database
            log_analytics_event(
                evento=f"security_{evento}",
                session_id=session_id,
                dati=event_data
            )
        except Exception as e:
            log.error(f"❌ Errore nella registrazione dell'evento di sicurezza: {str(e)}")

# Istanza singleton globale
security = SecurityManager()

def check_message_security(message, session_id=None):
    """
    Funzione completa per verificare la sicurezza di un messaggio.
    Restituisce un dict con i risultati delle varie verifiche.
    
    Args:
        message: Messaggio da verificare
        session_id: ID della sessione
        
    Returns:
        dict: Risultati delle verifiche di sicurezza
    """
    result = {
        "original_message": message,
        "sanitized_message": security.sanitize_input(message),
        "is_off_topic": security.is_off_topic(message),
        "is_suspicious": security.is_suspicious_activity(message),
        "rate_limited": False,
        "session_expired": False,
        "should_block": False,
        "response": None
    }
    
    # Verifica rate limit solo se c'è un session_id
    # Questi check vengono fatti dinamicamente per evitare dipendenze circolari
    if session_id:
        try:
            # Verifica rate limit
            from .security_rate import rate_limiter
            result["rate_limited"] = rate_limiter.check_rate_limit(session_id)
        except (ImportError, AttributeError):
            # Se security_rate.py non è disponibile, mantieni il valore False
            pass
            
        try:
            # Verifica scadenza sessione
            from .security_session import session_manager
            result["session_expired"] = session_manager.check_session_expired(session_id)
        except (ImportError, AttributeError):
            # Se security_session.py non è disponibile, mantieni il valore False
            pass
    
    # Determina se bloccare il messaggio
    if result["rate_limited"]:
        result["should_block"] = True
        result["response"] = "Mi dispiace, hai effettuato troppe richieste in breve tempo. Per garantire un servizio ottimale a tutti gli utenti, ti chiedo di attendere qualche minuto prima di inviare nuovi messaggi."
    elif result["session_expired"]:
        result["should_block"] = True
        result["response"] = "La tua sessione è scaduta per inattività. Iniziamo una nuova conversazione sulla Transizione 5.0. Come posso aiutarti oggi?"
    elif result["is_off_topic"]:
        result["should_block"] = True
        result["response"] = security.generate_stay_on_topic_response()
    
    # Logga eventi di sicurezza se necessario
    if session_id:
        if result["is_suspicious"]:
            security.log_security_event(
                "suspicious_activity", 
                session_id, 
                {"message": message[:100]}, 
                "warning"
            )
        if result["is_off_topic"]:
            security.log_security_event(
                "off_topic", 
                session_id, 
                {"message": message[:100]}, 
                "info"
            )
        if result["rate_limited"]:
            security.log_security_event(
                "rate_limit", 
                session_id, 
                {"message": message[:100]}, 
                "warning"
            )
    
    return result