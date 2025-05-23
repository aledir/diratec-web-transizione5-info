"""Operazioni per la gestione del database PostgreSQL."""
import json
import uuid
import pg8000
import os
from datetime import datetime
from cat.log import log
from typing import Dict, Any, List, Optional

# Variabili globali - Leggi variabili d'ambiente senza fallback
try:
    DB_CONFIG = {
        "host": os.environ["POSTGRES_HOST"],
        "port": os.environ["POSTGRES_PORT"],
        "database": os.environ["POSTGRES_DB"],
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"]
    }
    # Log configurazione senza esporre password
    log_config = {**DB_CONFIG}
    log_config["password"] = "********"
    log.info(f"✅ Configurazione database caricata dalle variabili d'ambiente: {log_config['host']}:{log_config['port']}/{log_config['database']}")
except KeyError as e:
    log.error(f"❌ Configurazione database incompleta. Variabile mancante: {e}")
    raise

def initialize(config):
    """Inizializza la configurazione del database"""
    global DB_CONFIG
    # Verifica che tutte le chiavi necessarie siano presenti
    required_keys = ["host", "port", "database", "user", "password"]
    missing_keys = [key for key in required_keys if key not in config or not config[key]]
    
    if missing_keys:
        error_msg = f"❌ Configurazione database incompleta. Campi mancanti: {', '.join(missing_keys)}"
        log.error(error_msg)
        raise ValueError(error_msg)
        
    DB_CONFIG = config
    # Non logare la password per sicurezza
    log_config = {**DB_CONFIG}
    log_config["password"] = "********"
    log.info(f"✅ Configurazione database inizializzata: {log_config['host']}:{log_config['port']}/{log_config['database']} (user: {log_config['user']})")

def connect_db():
    """Crea una connessione al database usando pg8000"""
    try:
        conn = pg8000.connect(
            host=DB_CONFIG["host"],
            port=int(DB_CONFIG["port"]),
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        return conn
    except Exception as e:
        log.error(f"❌ Errore di connessione al database: {str(e)}")
        return None

def verify_tables_exist():
    """Verifica che le tabelle necessarie esistano nel database"""
    try:
        conn = connect_db()
        if not conn:
            log.error("❌ Impossibile connettersi al database per verificare le tabelle")
            return False

        with conn.cursor() as cursor:
            # Verifica l'esistenza delle tabelle principali
            tables_to_check = ["leads", "conversazioni", "analytics", "audit_log"]
            missing_tables = []
            
            for table in tables_to_check:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = %s
                    );
                """, (table,))
                
                if not cursor.fetchone()[0]:
                    missing_tables.append(table)
            
            if missing_tables:
                log.error(f"❌ Tabelle mancanti nel database: {', '.join(missing_tables)}")
                return False
            else:
                log.info("✅ Tutte le tabelle necessarie esistono nel database")
                return True
    except Exception as e:
        log.error(f"❌ Errore nella verifica delle tabelle: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def create_lead(azienda_data, investimenti_data, contatto_data, session_id, score, stato):
    """Crea un nuovo lead nel database"""
    try:
        conn = connect_db()
        if not conn:
            return None

        with conn.cursor() as cursor:
            # Inserisci il lead
            cursor.execute(
                """
                INSERT INTO leads (azienda_data, investimenti_data, contatto_data, score, stato)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    json.dumps(azienda_data),
                    json.dumps(investimenti_data),
                    json.dumps(contatto_data),
                    score,
                    stato
                )
            )

            lead_id = cursor.fetchone()[0]

            # Aggiorna la conversazione
            if session_id:
                cursor.execute(
                    """
                    UPDATE conversazioni
                    SET lead_id = %s, completato_form = TRUE, fine_conversazione = NOW()
                    WHERE session_id = %s AND fine_conversazione IS NULL
                    """,
                    (lead_id, session_id)
                )

            conn.commit()
            log.info(f"✅ Lead creato con successo: ID {lead_id}")
            return lead_id
    except Exception as e:
        log.error(f"❌ Errore nella creazione del lead: {str(e)}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def update_lead(lead_id, azienda_data=None, investimenti_data=None, contatto_data=None, stato=None, score=None):
    """Aggiorna un lead esistente"""
    try:
        conn = connect_db()
        if not conn:
            return False

        with conn.cursor() as cursor:
            # Recupera il lead attuale
            cursor.execute(
                "SELECT azienda_data, investimenti_data, contatto_data, score FROM leads WHERE id = %s",
                (lead_id,)
            )

            result = cursor.fetchone()
            if not result:
                log.warning(f"⚠️ Lead non trovato: {lead_id}")
                return False

            current_azienda_data = json.loads(result[0]) if isinstance(result[0], str) else result[0]
            current_investimenti_data = json.loads(result[1]) if isinstance(result[1], str) else result[1]
            current_contatto_data = json.loads(result[2]) if isinstance(result[2], str) else result[2]
            current_score = result[3]

            # Aggiorna i dati
            if azienda_data:
                current_azienda_data.update(azienda_data)

            if investimenti_data:
                current_investimenti_data.update(investimenti_data)

            if contatto_data:
                current_contatto_data.update(contatto_data)

            # Se non viene fornito lo score, non modificarlo
            final_score = score if score is not None else current_score
            
            # Se non viene fornito lo stato, mantieni quello attuale
            update_fields = []
            update_values = []
            
            update_fields.append("azienda_data = %s")
            update_values.append(json.dumps(current_azienda_data))
            
            update_fields.append("investimenti_data = %s")
            update_values.append(json.dumps(current_investimenti_data))
            
            update_fields.append("contatto_data = %s")
            update_values.append(json.dumps(current_contatto_data))
            
            update_fields.append("score = %s")
            update_values.append(final_score)
            
            if stato:
                update_fields.append("stato = %s")
                update_values.append(stato)
            
            # Costruisci la query
            query = f"""
                UPDATE leads
                SET {", ".join(update_fields)}
                WHERE id = %s
            """
            update_values.append(lead_id)

            # Esegui l'aggiornamento
            cursor.execute(query, update_values)

            conn.commit()
            log.info(f"✅ Lead aggiornato con successo: ID {lead_id}")
            return True
    except Exception as e:
        log.error(f"❌ Errore nell'aggiornamento del lead: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def create_conversation(session_id, data):
    """Crea o aggiorna una conversazione nel database"""
    try:
        # Verifica prima che le tabelle necessarie esistano
        if not verify_tables_exist():
            log.warning("⚠️ Impossibile creare conversazione: tabelle necessarie non esistenti")
            return False
            
        conn = connect_db()
        if not conn:
            return False

        with conn.cursor() as cursor:
            # Verifiche se esiste già una conversazione attiva
            cursor.execute(
                """
                SELECT id FROM conversazioni
                WHERE session_id = %s AND fine_conversazione IS NULL
                """,
                (session_id,)
            )

            existing = cursor.fetchone()

            if existing:
                # Aggiorna la conversazione esistente
                cursor.execute(
                    """
                    UPDATE conversazioni
                    SET data = %s
                    WHERE id = %s
                    """,
                    (json.dumps(data), existing[0])
                )
                log.info(f"✅ Conversazione aggiornata: ID {existing[0]}")
            else:
                # Crea una nuova conversazione
                cursor.execute(
                    """
                    INSERT INTO conversazioni (session_id, data)
                    VALUES (%s, %s)
                    """,
                    (session_id, json.dumps(data))
                )
                log.info(f"✅ Nuova conversazione creata: session_id {session_id}")

            conn.commit()
            return True
    except Exception as e:
        log.error(f"❌ Errore nella gestione della conversazione: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_conversation(session_id):
    """Recupera una conversazione attiva dal database"""
    try:
        # Verifica prima che le tabelle necessarie esistano
        if not verify_tables_exist():
            log.warning("⚠️ Impossibile recuperare conversazione: tabelle necessarie non esistenti")
            return None
            
        conn = connect_db()
        if not conn:
            return None

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, data, lead_id FROM conversazioni
                WHERE session_id = %s AND fine_conversazione IS NULL
                """,
                (session_id,)
            )

            result = cursor.fetchone()
            if not result:
                return None

            return {
                "id": result[0],
                "data": json.loads(result[1]) if isinstance(result[1], str) else result[1],
                "lead_id": result[2]
            }
    except Exception as e:
        log.error(f"❌ Errore nel recupero della conversazione: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def log_analytics_event(evento, session_id=None, lead_id=None, dati=None):
    """Registra un evento analytics nel database"""
    try:
        # Verifica prima che le tabelle necessarie esistano
        if not verify_tables_exist():
            log.warning("⚠️ Impossibile registrare evento analytics: tabelle necessarie non esistenti")
            return False
            
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

def get_leads_from_db():
    """Recupera l'elenco dei lead dal database"""
    try:
        # Verifica prima che le tabelle necessarie esistano
        if not verify_tables_exist():
            log.warning("⚠️ Impossibile recuperare lead: tabelle necessarie non esistenti")
            return {"error": "Tabelle necessarie non esistenti", "status": 500}
            
        conn = connect_db()
        if not conn:
            return {"error": "Errore di connessione al database", "status": 500}

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, azienda_data->>'nome_azienda' as azienda,
                       contatto_data->>'email' as email,
                       score, stato, data_creazione
                FROM leads
                ORDER BY data_creazione DESC
                LIMIT 100
                """
            )

            results = cursor.fetchall()

            leads = []
            for row in results:
                leads.append({
                    "id": row[0],
                    "azienda": row[1],
                    "email": row[2],
                    "score": row[3],
                    "stato": row[4],
                    "data_creazione": row[5].isoformat() if row[5] else None
                })

            return {"leads": leads}
    except Exception as e:
        log.error(f"❌ Errore nel recupero dei lead: {str(e)}")
        return {"error": f"Errore nel recupero dei lead: {str(e)}", "status": 500}
    finally:
        if conn:
            conn.close()

def get_lead_details_from_db(lead_id):
    """Recupera i dettagli di un lead specifico"""
    try:
        # Verifica prima che le tabelle necessarie esistano
        if not verify_tables_exist():
            log.warning("⚠️ Impossibile recuperare dettagli lead: tabelle necessarie non esistenti")
            return None
            
        conn = connect_db()
        if not conn:
            return None

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, azienda_data, investimenti_data, contatto_data,
                       fonte, data_creazione, score, stato, assegnato_a, note
                FROM leads
                WHERE id = %s
                """,
                (lead_id,)
            )

            result = cursor.fetchone()
            if not result:
                return None

            return {
                "id": result[0],
                "azienda_data": json.loads(result[1]) if isinstance(result[1], str) else result[1],
                "investimenti_data": json.loads(result[2]) if isinstance(result[2], str) else result[2],
                "contatto_data": json.loads(result[3]) if isinstance(result[3], str) else result[3],
                "fonte": result[4],
                "data_creazione": result[5].isoformat() if result[5] else None,
                "score": result[6],
                "stato": result[7],
                "assegnato_a": result[8],
                "note": result[9]
            }
    except Exception as e:
        log.error(f"❌ Errore nel recupero dei dettagli del lead: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def update_lead_status_in_db(lead_id, stato):
    """Aggiorna lo stato di un lead nel database"""
    try:
        # Verifica prima che le tabelle necessarie esistano
        if not verify_tables_exist():
            log.warning("⚠️ Impossibile aggiornare stato lead: tabelle necessarie non esistenti")
            return False
            
        conn = connect_db()
        if not conn:
            return False

        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE leads
                SET stato = %s
                WHERE id = %s
                """,
                (stato, lead_id)
            )

            if cursor.rowcount == 0:
                log.warning(f"⚠️ Nessun lead aggiornato con ID: {lead_id}")
                return False

            conn.commit()
            log.info(f"✅ Stato del lead aggiornato: ID {lead_id} -> {stato}")
            return True
    except Exception as e:
        log.error(f"❌ Errore nell'aggiornamento dello stato del lead: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def finalize_lead_from_conversation(session_id):
    """Finalizza la creazione di un lead dalla conversazione corrente"""
    try:
        # Verifica prima che le tabelle necessarie esistano
        if not verify_tables_exist():
            log.warning("⚠️ Impossibile finalizzare lead dalla conversazione: tabelle necessarie non esistenti")
            return {"success": False, "error": "Tabelle necessarie non esistenti"}
            
        conn = connect_db()
        if not conn:
            return {"success": False, "error": "Errore di connessione al database"}

        with conn.cursor() as cursor:
            # Recupera la conversazione attiva
            cursor.execute(
                """
                SELECT data FROM conversazioni
                WHERE session_id = %s AND fine_conversazione IS NULL
                """,
                (session_id,)
            )

            result = cursor.fetchone()
            if not result:
                return {"success": False, "error": "Conversazione non trovata"}

            # Estrai i dati della conversazione
            conversation_data = json.loads(result[0]) if isinstance(result[0], str) else result[0]

            # Verifica che i dati del lead esistano
            if "lead_data" not in conversation_data:
                return {"success": False, "error": "Dati del lead non trovati nella conversazione"}

            lead_data = conversation_data["lead_data"]

            # Verifica che ci siano i dati minimi necessari
            azienda_data = lead_data.get("azienda_data", {})
            investimenti_data = lead_data.get("investimenti_data", {})
            contatto_data = lead_data.get("contatto_data", {})

            # Verifica che ci sia almeno un dato di contatto
            if not contatto_data.get("email") and not contatto_data.get("telefono"):
                return {"success": False, "error": "È necessario fornire almeno un contatto email o telefono"}

            # Calcola lo score e determina lo stato
            from .scoring_operations import calculate_lead_score, get_lead_status
            score = calculate_lead_score(azienda_data, investimenti_data)
            stato = get_lead_status(score)

            # Crea il lead
            lead_id = create_lead(
                azienda_data=azienda_data,
                investimenti_data=investimenti_data,
                contatto_data=contatto_data,
                session_id=session_id,
                score=score,
                stato=stato
            )

            if not lead_id:
                return {"success": False, "error": "Errore nella creazione del lead"}

            # Registra l'evento analytics
            log_analytics_event(
                evento="creazione_lead",
                session_id=session_id,
                lead_id=lead_id,
                dati={"lead_data": lead_data}
            )

            return {
                "success": True,
                "lead_id": lead_id,
                "message": "Lead creato con successo"
            }
    except Exception as e:
        log.error(f"❌ Errore nella finalizzazione del lead: {str(e)}")
        if conn:
            conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        if conn:
            conn.close()


def update_conversation(session_id, new_data):
    """
    Aggiorna una conversazione esistente senza sovrascriverla completamente.
    """
    try:
        conn = connect_db()
        if not conn:
            return False

        with conn.cursor() as cursor:
            # Recupera prima la conversazione esistente
            cursor.execute(
                """
                SELECT id, data FROM conversazioni
                WHERE session_id = %s AND fine_conversazione IS NULL
                """,
                (session_id,)
            )

            existing = cursor.fetchone()
            if not existing:
                log.warning(f"⚠️ Impossibile aggiornare: Conversazione non trovata per session_id={session_id}")
                return False
                
            conversation_id = existing[0]
            existing_data = json.loads(existing[1]) if isinstance(existing[1], str) else existing[1]
            
            # Log per debug
            log.info(f"📌 Update conversation - Dati esistenti: {existing_data}")
            log.info(f"📌 Update conversation - Nuovi dati: {new_data}")
            
            # Verifica se la chiave "messaggi" esiste in entrambi i dizionari
            # Se presente nei nuovi dati, sostituisci completamente
            if "messaggi" in new_data:
                existing_data["messaggi"] = new_data["messaggi"]
                log.info(f"📝 Aggiornati messaggi nella conversazione - Nuova lunghezza: {len(new_data['messaggi'])}")
            
            # Aggiorna lead_data se presente
            if "lead_data" in new_data:
                if "lead_data" not in existing_data:
                    existing_data["lead_data"] = {}
                    
                for key, value in new_data["lead_data"].items():
                    if isinstance(value, dict):
                        if key not in existing_data["lead_data"]:
                            existing_data["lead_data"][key] = {}
                        existing_data["lead_data"][key].update(value)
                    else:
                        existing_data["lead_data"][key] = value

            # Aggiorna la conversazione con i dati modificati
            cursor.execute(
                """
                UPDATE conversazioni
                SET data = %s
                WHERE id = %s
                """,
                (json.dumps(existing_data), conversation_id)
            )
            
            conn.commit()
            log.info(f"✅ Conversazione aggiornata con successo: ID {conversation_id}")
            return True
    except Exception as e:
        log.error(f"❌ Errore nell'aggiornamento della conversazione: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()