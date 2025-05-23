"""Operazioni per la raccolta di analytics."""
from cat.log import log
from .database_operations import connect_db
import json

def log_analytics_event(evento, session_id=None, lead_id=None, dati=None):
    """Registra un evento analytics nel database"""
    try:
        conn = connect_db()
        if not conn:
            return False

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO analytics (evento, session_id, lead_id, dati)
                VALUES (%s, %s, %s, %s)
                """,
                (evento, session_id, lead_id, json.dumps(dati or {}))
            )

            conn.commit()
            return True
    except Exception as e:
        log.error(f"❌ Errore nella registrazione dell'evento analytics: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()