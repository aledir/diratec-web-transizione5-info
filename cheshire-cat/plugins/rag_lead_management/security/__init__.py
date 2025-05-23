"""
Pacchetto di sicurezza per il plugin Lead Management.
Fornisce funzionalità avanzate di protezione e monitoraggio.
"""
from .security_core import SecurityManager, check_message_security
from .security_rate import RateLimiter
from .security_session import SessionManager
from .security_audit import AuditLogger
from .security_scan import check_dependencies

# Crea le istanze singleton
security = SecurityManager()
rate_limiter = RateLimiter()
session_manager = SessionManager()
audit_logger = AuditLogger()

# Esporta le funzioni principali
__all__ = ['security', 'rate_limiter', 'session_manager', 'audit_logger', 
           'check_message_security', 'check_dependencies']