"""Plugin GSE Stats per Cheshire Cat."""
import json
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from cat.mad_hatter.decorators import plugin, hook
from cat.log import log

from . import DATA_FILE_PATH
from .gse_stats_operations import initialize, get_gse_stats_data, update_gse_stats_data

# Variabili globali per la configurazione
DATA_FILE_PATH = "data/gse_stats.json"
GSE_STATS = {}
LAST_UPDATE = None

@plugin
class Transizione5StatsPlugin:
    def __init__(self, cat):
        global GSE_STATS, LAST_UPDATE, DATA_FILE_PATH
        
        self.cat = cat
        
        # Carica impostazioni
        settings = cat.mad_hatter.get_plugin().load_settings()
        
        # URL del portale GSE
        gse_url = settings.get("gse_url", "https://www.gse.it/servizi-per-te/attuazione-misure-pnrr/transizione-5-0")
        
        # URL del contatore
        contatore_url = "https://gseorg1.my.salesforce-sites.com/transizione5contatori"
        
        # Carica i dati esistenti
        self.load_stats_from_file()
        
        # Inizializza le operazioni
        plugin_data = {
            "stats": GSE_STATS,
            "last_successful_fetch_time": LAST_UPDATE,
            "data_file_path": DATA_FILE_PATH,
            "gse_url": gse_url,
            "contatore_url": contatore_url
        }
        
        initialize(plugin_data)
        log.info("Plugin GSE Stats inizializzato e operazioni configurate")
    
    def load_stats_from_file(self):
        """Carica i dati da file all'avvio"""
        global GSE_STATS, LAST_UPDATE
        
        try:
            if not os.path.exists(DATA_FILE_PATH):
                log.info(f"File dati GSE non trovato: {DATA_FILE_PATH}")
                return False
                    
            with open(DATA_FILE_PATH, "r") as f:
                loaded_data = json.load(f)
                    
                # Rimuovi il timestamp dal dizionario
                timestamp_str = loaded_data.pop("timestamp", None)
                    
                # Aggiorna i dati
                GSE_STATS = loaded_data
                    
                # Se c'è un timestamp, aggiorna LAST_UPDATE
                if timestamp_str:
                    try:
                        LAST_UPDATE = datetime.fromisoformat(timestamp_str)
                        log.info(f"📋 Dati GSE caricati da file (ultimo aggiornamento: {LAST_UPDATE})")
                    except:
                        log.warning("⚠️ Formato timestamp non valido nel file dati")
                    
                return True
        except FileNotFoundError:
            log.info(f"ℹ️ File dati GSE non trovato: {DATA_FILE_PATH}")
        except json.JSONDecodeError:
            log.error(f"❌ Errore di decodifica JSON dal file: {DATA_FILE_PATH}")
        except Exception as e:
            log.error(f"❌ Errore nel caricamento dei dati GSE: {str(e)}")
            import traceback
            log.error(traceback.format_exc())
        
        return False


def get_plugin_instance(cat):
    """Ottiene l'istanza corretta del plugin in modo sicuro"""
    # Cicla attraverso tutti i plugin
    for plugin_id, plugin_obj in cat.mad_hatter.plugins.items():
        # Identifica il nostro plugin
        if plugin_id == "transizione5_gse_stats":
            return plugin_obj
    return None


@hook
def after_cat_bootstrap(cat):
    """Hook che viene eseguito dopo l'avvio del Cat"""
    log.info("🚀 Hook after_cat_bootstrap chiamato per GSE Stats")
    
    try:
        # Ottieni il plugin
        plugin = get_plugin_instance(cat)
        
        if not plugin:
            log.error("❌ Plugin GSE Stats non trovato")
            return
        
        log.info("✅ Plugin GSE Stats trovato")
        
        # Crea una funzione per l'aggiornamento periodico
        def update_routine():
            log.info("🔄 Esecuzione job di aggiornamento GSE Stats")
            try:
                # Utilizziamo requests in modo sincrono (più semplice in un job pianificato)
                import requests
                from .gse_stats_operations import update_gse_stats_sync
                
                result = update_gse_stats_sync()
                if result and result.get("status") == "success":
                    log.info("✅ Aggiornamento dati GSE completato con successo")
                else:
                    log.error(f"❌ Aggiornamento dati GSE fallito: {result}")
            except Exception as e:
                log.error(f"❌ Errore durante l'aggiornamento dei dati GSE: {e}")
                import traceback
                log.error(traceback.format_exc())
        
        # Pianifica un job di aggiornamento periodico utilizzando il White Rabbit
        settings = cat.mad_hatter.get_plugin().load_settings()
        update_interval = settings.get("update_interval", 3.0)
        seconds = int(update_interval * 60 * 60)  # Per test 10, poi cambiare a: int(update_interval * 60 * 60)
        cat.white_rabbit.schedule_interval_job(
            update_routine,
            seconds=seconds,
            job_id="gse_stats_update"
        )
        
        log.info(f"📅 Job di aggiornamento GSE pianificato ogni {seconds} secondi")
        
        # Forza un aggiornamento immediato all'avvio
        update_routine()
        
    except Exception as e:
        log.error(f"❌ Errore nell'hook after_cat_bootstrap: {str(e)}")
        import traceback
        log.error(traceback.format_exc())