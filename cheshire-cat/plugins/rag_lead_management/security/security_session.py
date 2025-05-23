"""
Gestione della sicurezza delle sessioni per il plugin Lead Management.
"""
import secrets
import json
from datetime import datetime, timedelta
from cat.log import log
import threading

# Importa config in modo condizionale per evitare dipendenze circolari
try:
    from .security_config import SESSION_TIMEOUT_MINUTES
except ImportError:
    # Valore di default se security_config.py non è disponibile
    SESSION_TIMEOUT_MINUTES = 30

# Lock per thread-safety
_session_lock = threading.Lock()

class SessionManager:
    """Gestisce la sicurezza delle sessioni."""
    
    def __init__(self):
        """Inizializza il gestore di sessioni."""
        # Configurazione timeout
        self.session_timeout = SESSION_TIMEOUT_MINUTES
        
        # Cache per i token di sessione
        # Formato: {session_id: {"token": token, "last_access": timestamp}}
        self.session_tokens = {}
    
    def generate_session_token(self):
        """
        Genera un token di sessione sicuro
        
        Returns:
            str: Token di sessione
        """
        return secrets.token_hex(32)
    
    def validate_session_token(self, session_id, token):
        """
        Verifica che il token di sessione sia valido
        
        Args:
            session_id: ID della sessione
            token: Token da verificare
            
        Returns:
            bool: True se il token è valido, False altrimenti
        """
        try:
            # Verifica cache locale prima
            with _session_lock:
                if session_id in self.session_tokens:
                    stored_token = self.session_tokens[session_id]["token"]
                    if stored_token == token:
                        # Aggiorna il timestamp di accesso
                        self.session_tokens[session_id]["last_access"] = datetime.now()
                        return True
            
            # Se non trovato in cache, verifica nel database
            # Importa localmente per evitare dipendenze circolari
            from ..database_operations import connect_db
            
            conn = connect_db()
            if not conn:
                return False
                
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT data->>'session_token' FROM conversazioni
                    WHERE session_id = %s AND fine_conversazione IS NULL
                    """,
                    (session_id,)
                )
                
                result = cursor.fetchone()
                if not result or not result[0]:
                    return False
                    
                # Verifica il token
                stored_token = result[0]
                
                # Aggiorna la cache
                with _session_lock:
                    self.session_tokens[session_id] = {
                        "token": stored_token,
                        "last_access": datetime.now()
                    }
                
                return stored_token == token
        except Exception as e:
            log.error(f"❌ Errore nella validazione del token di sessione: {str(e)}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def rotate_session_token(self, session_id):
        """
        Genera un nuovo token per una sessione esistente
        
        Args:
            session_id: ID della sessione
            
        Returns:
            str: Nuovo token di sessione o None in caso di errore
        """
        try:
            # Importa localmente per evitare dipendenze circolari
            from ..database_operations import connect_db, get_conversation
            
            # Genera nuovo token
            new_token = self.generate_session_token()
            
            # Recupera la conversazione
            conversation = get_conversation(session_id)
            if not conversation:
                return None
                
            # Aggiorna il token nella conversazione
            conversation_data = conversation["data"]
            conversation_data["session_token"] = new_token
            
            # Salva la conversazione aggiornata
            conn = connect_db()
            if not conn:
                return None
                
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE conversazioni
                    SET data = %s
                    WHERE session_id = %s AND fine_conversazione IS NULL
                    """,
                    (json.dumps(conversation_data), session_id)
                )
                
                conn.commit()
            
            # Aggiorna la cache
            with _session_lock:
                self.session_tokens[session_id] = {
                    "token": new_token,
                    "last_access": datetime.now()
                }
                
            return new_token
        except Exception as e:
            log.error(f"❌ Errore nella rotazione del token di sessione: {str(e)}")
            return None
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def check_session_expired(self, session_id):
        """
        Verifica se una sessione è scaduta per inattività
        
        Args:
            session_id: ID della sessione
            
        Returns:
            bool: True se scaduta, False altrimenti
        """
        try:
            # Verifica nella cache locale prima
            with _session_lock:
                if session_id in self.session_tokens:
                    last_access = self.session_tokens[session_id]["last_access"]
                    session_age = datetime.now() - last_access
                    
                    # Se non è scaduta, aggiorna il timestamp e restituisci False
                    if session_age <= timedelta(minutes=self.session_timeout):
                        self.session_tokens[session_id]["last_access"] = datetime.now()
                        return False
                    
                    # Se è scaduta, rimuovi dalla cache
                    del self.session_tokens[session_id]
            
            # Se non trovata in cache o scaduta, verifica nel database
            # Importa localmente per evitare dipendenze circolari
            from ..database_operations import connect_db
            
            conn = connect_db()
            if not conn:
                return True  # In caso di dubbio, considera la sessione scaduta
                
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT inizio_conversazione FROM conversazioni
                    WHERE session_id = %s AND fine_conversazione IS NULL
                    """,
                    (session_id,)
                )
                
                result = cursor.fetchone()
                if not result:
                    return True
                    
                session_start = result[0]
                session_age = datetime.now() - session_start
                
                # Verifica timeout
                if session_age > timedelta(minutes=self.session_timeout):
                    # Termina la sessione
                    cursor.execute(
                        """
                        UPDATE conversazioni
                        SET fine_conversazione = NOW()
                        WHERE session_id = %s AND fine_conversazione IS NULL
                        """,
                        (session_id,)
                    )
                    conn.commit()
                    return True
                    
                # Se la sessione è attiva, aggiorna la cache
                with _session_lock:
                    # Recupera il token (se presente)
                    cursor.execute(
                        """
                        SELECT data->>'session_token' FROM conversazioni
                        WHERE session_id = %s AND fine_conversazione IS NULL
                        """,
                        (session_id,)
                    )
                    
                    token_result = cursor.fetchone()
                    token = token_result[0] if token_result and token_result[0] else self.generate_session_token()
                    
                    # Aggiorna la cache
                    self.session_tokens[session_id] = {
                        "token": token,
                        "last_access": datetime.now()
                    }
                
                return False
        except Exception as e:
            log.error(f"❌ Errore nella verifica della scadenza della sessione: {str(e)}")
            return True  # In caso di errore, considera la sessione scaduta
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def create_session(self, session_id, data=None):
        """
        Crea una nuova sessione
        
        Args:
            session_id: ID della sessione
            data: Dati iniziali della sessione (opzionale)
            
        Returns:
            str: Token di sessione o None in caso di errore
        """
        try:
            # Importa localmente per evitare dipendenze circolari
            from ..database_operations import connect_db, create_conversation
            
            # Genera token
            token = self.generate_session_token()
            
            # Prepara i dati della sessione
            session_data = data or {}
            session_data["session_token"] = token
            session_data["created_at"] = datetime.now().isoformat()
            
            # Crea la conversazione nel database
            success = create_conversation(session_id, session_data)
            
            if not success:
                return None
            
            # Aggiorna la cache
            with _session_lock:
                self.session_tokens[session_id] = {
                    "token": token,
                    "last_access": datetime.now()
                }
            
            return token
        except Exception as e:
            log.error(f"❌ Errore nella creazione della sessione: {str(e)}")
            return None
    
    def invalidate_session(self, session_id):
        """
        Invalida una sessione
        
        Args:
            session_id: ID della sessione
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        try:
            # Importa localmente per evitare dipendenze circolari
            from ..database_operations import connect_db
            
            # Rimuovi dalla cache
            with _session_lock:
                if session_id in self.session_tokens:
                    del self.session_tokens[session_id]
            
            # Termina la sessione nel database
            conn = connect_db()
            if not conn:
                return False
                
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE conversazioni
                    SET fine_conversazione = NOW()
                    WHERE session_id = %s AND fine_conversazione IS NULL
                    """,
                    (session_id,)
                )
                
                if cursor.rowcount == 0:
                    # Nessuna riga aggiornata
                    return False
                
                conn.commit()
                return True
        except Exception as e:
            log.error(f"❌ Errore nell'invalidazione della sessione: {str(e)}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def clean_expired_sessions(self):
        """
        Pulisce le sessioni scadute sia nella cache che nel database
        
        Returns:
            int: Numero di sessioni pulite
        """
        try:
            # Importa localmente per evitare dipendenze circolari
            from ..database_operations import connect_db, verify_tables_exist
            
            # Pulisci la cache locale
            expired_sessions = []
            current_time = datetime.now()
            
            with _session_lock:
                for session_id, session_data in list(self.session_tokens.items()):
                    last_access = session_data["last_access"]
                    if current_time - last_access > timedelta(minutes=self.session_timeout):
                        expired_sessions.append(session_id)
                        del self.session_tokens[session_id]
            
            # Verifica se le tabelle esistono prima di tentare di pulire il database
            tables_exist = verify_tables_exist()
            
            if not tables_exist:
                log.warning("⚠️ Tabelle del database non trovate, impossibile pulire le sessioni scadute")
                return len(expired_sessions)
            
            # Pulisci il database
            conn = connect_db()
            if not conn:
                return len(expired_sessions)
                
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE conversazioni
                        SET fine_conversazione = NOW()
                        WHERE fine_conversazione IS NULL
                        AND inizio_conversazione < %s
                        """,
                        (current_time - timedelta(minutes=self.session_timeout),)
                    )
                    
                    db_expired = cursor.rowcount
                    conn.commit()
                    
                return len(expired_sessions) + db_expired
            except Exception as e:
                log.error(f"❌ Errore nell'aggiornamento delle sessioni nel database: {str(e)}")
                if conn:
                    conn.rollback()
                return len(expired_sessions)
            finally:
                if conn:
                    conn.close()
        except Exception as e:
            log.error(f"❌ Errore nella pulizia delle sessioni scadute: {str(e)}")
            return 0

# Istanza singleton del gestore di sessioni
session_manager = SessionManager()