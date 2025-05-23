"""
Configurazione della sicurezza per il plugin Lead Management.
"""

# Parametri generali
MAX_MESSAGE_LENGTH = 2000  # Lunghezza massima dei messaggi
SESSION_TIMEOUT_MINUTES = 30  # Timeout sessione in minuti
DEBUG_MODE = False  # Modalità debug (attivare solo in sviluppo)

# Rate limiting
RATE_LIMIT_INTERVAL_SECONDS = 60  # Periodo per il rate limit
RATE_LIMIT_MAX_REQUESTS = 10  # Numero massimo di richieste nel periodo
IP_RATE_LIMIT_REQUESTS = 60  # Numero massimo di richieste per IP al minuto

# Brute force protection
BRUTE_FORCE_MAX_ATTEMPTS = 5  # Numero massimo di tentativi falliti
BRUTE_FORCE_WINDOW_MINUTES = 10  # Finestra temporale per il conteggio tentativi
BRUTE_FORCE_BLOCK_MINUTES = 30  # Durata del blocco dopo troppi tentativi

# Email security
DISPOSABLE_EMAIL_DOMAINS = [
    "guerrillamail.com", "mailinator.com", "tempmail.com", 
    "10minutemail.com", "yopmail.com", "maildrop.cc",
    "temp-mail.org", "fakeinbox.com", "trashmail.com"
]

# Regex patterns
SUSPICIOUS_PATTERNS = [
    r"(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER).+(FROM|TABLE)",  # Possibili iniezioni SQL
    r"<script>|<\/script>|javascript:",  # Possibili XSS
    r"\bhacker\b|\bhack\b|\bvulnerabil",  # Discussioni su hacking
    r"cat\.working_memory|skip_llm_generation",  # Riferimenti a variabili interne
    r"token|api_key|password|credential",  # Tentativi di phishing
    r"/%[0-9A-F]{2}|\\x[0-9A-F]{2}",  # URL o Unicode encoding
]

# Argomenti fuori tema
FORBIDDEN_TOPICS = [
    r"\bporno", r"\bsex", r"\bcasino", r"\bgioco d'azzardo", 
    r"\bbet", r"\bscommesse", r"\bhacker", r"\bhacking",
    r"\brazzismo", r"\bodio", r"\bdiscriminazione", r"\bpolitica",
    r"\bchat gpt", r"\bopenai", r"\ballucina", r"\bllm\b",
    r"\btraduzione\b", r"\btraduci\b", r"\bracconta una storia",
    r"\bpoesia\b", r"\bcanzoni\b", r"\baiuto compiti"
]

# Parole chiave Transizione 5.0
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

# Secure headers
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'",
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}

# Log security
SENSITIVE_FIELDS = [
    'password', 'token', 'secret', 'key', 'email', 
    'telefono', 'cellulare', 'carta', 'credit', 'cvv'
]