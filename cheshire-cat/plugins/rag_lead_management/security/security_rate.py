"""
Funzionalità di rate limiting e protezione da DoS.
"""
from datetime import datetime, timedelta
from cat.log import log
import threading

# Importa config in modo condizionale per evitare dipendenze circolari
try:
    from .security_config import (RATE_LIMIT_INTERVAL_SECONDS, RATE_LIMIT_MAX_REQUESTS,
                                IP_RATE_LIMIT_REQUESTS, BRUTE_FORCE_MAX_ATTEMPTS, 
                                BRUTE_FORCE_WINDOW_MINUTES, BRUTE_FORCE_BLOCK_MINUTES)
except ImportError:
    # Valori di default se security_config.py non è disponibile
    RATE_LIMIT_INTERVAL_SECONDS = 60  # Periodo in secondi
    RATE_LIMIT_MAX_REQUESTS = 10  # Richieste max nel periodo
    IP_RATE_LIMIT_REQUESTS = 60  # Richieste max per IP al minuto
    BRUTE_FORCE_MAX_ATTEMPTS = 5  # Tentativi falliti max
    BRUTE_FORCE_WINDOW_MINUTES = 10  # Finestra temporale per tentativi
    BRUTE_FORCE_BLOCK_MINUTES = 30  # Durata del blocco

# Cache globali
_request_cache = {}
_ip_request_counter = {}
_failed_attempts = {}
_blocked_ips = {}

# Lock per thread-safety
_cache_lock = threading.Lock()

class RateLimiter:
    """Gestisce tutte le funzionalità di rate limiting e protezione DoS."""
    
    def __init__(self):
        """Inizializza il rate limiter."""
        # Configurazioni
        self.rate_limit_interval = RATE_LIMIT_INTERVAL_SECONDS
        self.rate_limit_max = RATE_LIMIT_MAX_REQUESTS
        self.ip_rate_limit_max = IP_RATE_LIMIT_REQUESTS
        self.brute_force_max_attempts = BRUTE_FORCE_MAX_ATTEMPTS
        self.brute_force_window = BRUTE_FORCE_WINDOW_MINUTES
        self.brute_force_block_duration = BRUTE_FORCE_BLOCK_MINUTES
    
    def check_rate_limit(self, session_id):
        """
        Verifica se una sessione ha superato il limite di richieste.
        
        Args:
            session_id: ID della sessione
            
        Returns:
            bool: True se il limite è stato superato, False altrimenti
        """
        global _request_cache, _cache_lock
        current_time = datetime.now()
        
        with _cache_lock:
            # Se la sessione non è nel cache, inizializzala
            if session_id not in _request_cache:
                _request_cache[session_id] = []
                
            # Recupera le richieste recenti
            requests = _request_cache[session_id]
            
            # Rimuove richieste più vecchie del periodo configurato
            requests = [r for r in requests if r > current_time - timedelta(seconds=self.rate_limit_interval)]
            
            # Verifica se è stato superato il limite
            if len(requests) >= self.rate_limit_max:
                log.warning(f"⚠️ Rate limit superato per session_id: {session_id}")
                return True
                
            # Aggiorna la cache con la nuova richiesta
            requests.append(current_time)
            _request_cache[session_id] = requests
            
        return False
    
    def check_brute_force(self, ip_address, is_failed_attempt=False):
        """
        Verifica se un IP sta tentando un attacco di forza bruta
        
        Args:
            ip_address: Indirizzo IP da verificare
            is_failed_attempt: True se questo è un tentativo fallito
            
        Returns:
            bool: True se l'IP è bloccato, False altrimenti
        """
        global _failed_attempts, _blocked_ips, _cache_lock
        current_time = datetime.now()
        
        with _cache_lock:
            # Controlla se l'IP è già bloccato
            if ip_address in _blocked_ips:
                block_until = _blocked_ips[ip_address]
                if current_time < block_until:
                    # Calcola il tempo rimanente di blocco
                    remaining = (block_until - current_time).total_seconds()
                    log.warning(f"⚠️ IP {ip_address} bloccato per altri {int(remaining)} secondi")
                    return True
                else:
                    # Sblocca l'IP se il periodo di blocco è terminato
                    del _blocked_ips[ip_address]
            
            # Se è un tentativo fallito, aggiorna il conteggio
            if is_failed_attempt:
                if ip_address not in _failed_attempts:
                    _failed_attempts[ip_address] = []
                
                # Aggiungi il timestamp del tentativo fallito
                _failed_attempts[ip_address].append(current_time)
                
                # Rimuovi i tentativi più vecchi
                _failed_attempts[ip_address] = [
                    t for t in _failed_attempts[ip_address] 
                    if t > current_time - timedelta(minutes=self.brute_force_window)
                ]
                
                # Se ci sono troppi tentativi falliti, blocca l'IP
                if len(_failed_attempts[ip_address]) >= self.brute_force_max_attempts:
                    block_until = current_time + timedelta(minutes=self.brute_force_block_duration)
                    _blocked_ips[ip_address] = block_until
                    log.warning(f"🚨 IP {ip_address} bloccato per {self.brute_force_block_duration} minuti dopo ripetuti tentativi falliti")
                    
                    # Registra l'evento di sicurezza
                    try:
                        from .security_audit import audit_logger
                        audit_logger.log_security_event(
                            "ip_blocked",
                            f"ip-{ip_address}", 
                            {"ip": ip_address, "block_until": block_until.isoformat()},
                            "error"
                        )
                    except (ImportError, AttributeError):
                        # Se security_audit.py non è disponibile, logga solo l'evento
                        log.error(f"🚨 IP {ip_address} bloccato fino a {block_until.isoformat()}")
                    
                    return True
            
        return False
    
    def check_dos_protection(self, ip_address):
        """
        Verifica se un IP sta facendo troppe richieste (possibile DoS)
        
        Args:
            ip_address: Indirizzo IP da verificare
            
        Returns:
            bool: True se l'IP è bloccato, False altrimenti
        """
        global _ip_request_counter, _cache_lock
        current_time = datetime.now()
        
        with _cache_lock:
            # Se l'IP non è ancora nel contatore, inizializzalo
            if ip_address not in _ip_request_counter:
                _ip_request_counter[ip_address] = []
            
            # Aggiungi il timestamp della richiesta
            _ip_request_counter[ip_address].append(current_time)
            
            # Rimuovi le richieste più vecchie di 1 minuto
            _ip_request_counter[ip_address] = [
                t for t in _ip_request_counter[ip_address] 
                if t > current_time - timedelta(minutes=1)
            ]
            
            # Se ci sono troppe richieste in 1 minuto, blocca temporaneamente
            if len(_ip_request_counter[ip_address]) > self.ip_rate_limit_max:
                log.warning(f"🚨 Possibile attacco DoS da IP {ip_address}: {len(_ip_request_counter[ip_address])} richieste nell'ultimo minuto")
                
                # Registra l'evento di sicurezza
                try:
                    from .security_audit import audit_logger
                    audit_logger.log_security_event(
                        "dos_protection",
                        f"ip-{ip_address}", 
                        {"ip": ip_address, "request_count": len(_ip_request_counter[ip_address])},
                        "error"
                    )
                except (ImportError, AttributeError):
                    # Se security_audit.py non è disponibile, logga solo l'evento
                    log.error(f"🚨 Possibile DoS da {ip_address}: {len(_ip_request_counter[ip_address])} richieste/min")
                
                return True
            
        return False
    
    def clear_cache(self, older_than_minutes=60):
        """
        Pulisce la cache di richieste e tentativi più vecchi di un certo periodo
        
        Args:
            older_than_minutes: Minuti oltre i quali i dati vengono rimossi
            
        Returns:
            int: Numero di elementi rimossi dalla cache
        """
        global _request_cache, _ip_request_counter, _failed_attempts, _cache_lock
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=older_than_minutes)
        removed = 0
        
        with _cache_lock:
            # Pulisci _request_cache
            for session_id in list(_request_cache.keys()):
                # Filtra richieste recenti
                old_len = len(_request_cache[session_id])
                _request_cache[session_id] = [
                    r for r in _request_cache[session_id] if r > cutoff_time
                ]
                new_len = len(_request_cache[session_id])
                removed += (old_len - new_len)
                
                # Se non ci sono richieste recenti, rimuovi la sessione
                if not _request_cache[session_id]:
                    del _request_cache[session_id]
            
            # Pulisci _ip_request_counter
            for ip in list(_ip_request_counter.keys()):
                old_len = len(_ip_request_counter[ip])
                _ip_request_counter[ip] = [
                    r for r in _ip_request_counter[ip] if r > cutoff_time
                ]
                new_len = len(_ip_request_counter[ip])
                removed += (old_len - new_len)
                
                if not _ip_request_counter[ip]:
                    del _ip_request_counter[ip]
            
            # Pulisci _failed_attempts
            for ip in list(_failed_attempts.keys()):
                old_len = len(_failed_attempts[ip])
                _failed_attempts[ip] = [
                    r for r in _failed_attempts[ip] if r > cutoff_time
                ]
                new_len = len(_failed_attempts[ip])
                removed += (old_len - new_len)
                
                if not _failed_attempts[ip]:
                    del _failed_attempts[ip]
            
            # Pulisci _blocked_ips scaduti
            for ip in list(_blocked_ips.keys()):
                if _blocked_ips[ip] < current_time:
                    del _blocked_ips[ip]
                    removed += 1
                    
        return removed

# Istanza singleton
rate_limiter = RateLimiter()