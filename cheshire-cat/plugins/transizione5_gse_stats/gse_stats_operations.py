"""Operazioni per il plugin GSE Stats."""
import json
import os
from cat.log import log
from datetime import datetime
import aiohttp
import requests
import re
from bs4 import BeautifulSoup

from . import DATA_FILE_PATH

# Variabili globali per i dati
_stats = {}
_last_successful_fetch_time = None
_contatore_url = "https://gseorg1.my.salesforce-sites.com/transizione5contatori"

def initialize(plugin_data):
    """Inizializza le variabili globali con i dati del plugin"""
    global _stats, _last_successful_fetch_time, _contatore_url
    
    _stats = plugin_data["stats"]
    _last_successful_fetch_time = plugin_data["last_successful_fetch_time"]
    
    # Assicuriamoci che l'URL del contatore sia sempre disponibile
    if "contatore_url" in plugin_data and plugin_data["contatore_url"]:
        _contatore_url = plugin_data["contatore_url"]
    
    log.info(f"GSE Stats Operations inizializzato: stats={bool(_stats)}, contatore_url={_contatore_url}, data_file_path={DATA_FILE_PATH}")

def get_gse_stats_data():
    """Restituisce i dati delle statistiche GSE"""
    global _stats, _last_successful_fetch_time
    
    log.info(f"get_gse_stats_data: stats={_stats}, last_update={_last_successful_fetch_time}")
    
    if not _stats:
        return {
            "error": "Dati non ancora disponibili",
            "status": 404
        }
    
    return {
        **_stats,
        "last_successful_update": _last_successful_fetch_time.isoformat() if _last_successful_fetch_time else None
    }

async def update_gse_stats_data():
    """Forza l'aggiornamento manuale dei dati GSE (versione asincrona)"""
    global _stats, _last_successful_fetch_time, _data_file_path, _contatore_url
    
    log.info(f"update_gse_stats_data: url={_contatore_url}")
    
    if not _contatore_url:
        return {
            "status": "error",
            "message": "URL Contatore non configurato",
            "status": 500
        }
    
    # Aggiorna i dati GSE
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(_contatore_url) as response:
                if response.status != 200:
                    log.error(f"Risposta non valida dal contatore: {response.status}")
                    return {
                        "status": "error",
                        "message": f"Risposta non valida dal contatore: {response.status}"
                    }

                html = await response.text()
                log.info(f"HTML contatore ricevuto: {len(html)} caratteri")

                # Usiamo BeautifulSoup per estrarre i dati dal contatore
                result = _extract_data_from_html(html)
                
                if "error" in result:
                    return result
                
                # Aggiorna i dati e il timestamp
                _stats = result["data"]
                _last_successful_fetch_time = datetime.now()
                
                # Salva i dati su file
                save_success = _save_to_file()
                
                return {
                    "status": "success",
                    "message": "Dati GSE aggiornati con successo",
                    "data": _stats,
                    "saved_to_file": save_success
                }
    
    except Exception as e:
        log.error(f"Errore nell'aggiornamento dei dati GSE: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Errore nell'aggiornamento dei dati GSE: {str(e)}"
        }

def update_gse_stats_sync():
    """Forza l'aggiornamento manuale dei dati GSE (versione sincrona)"""
    global _stats, _last_successful_fetch_time, _data_file_path, _contatore_url
    
    log.info(f"update_gse_stats_sync: url={_contatore_url}")
    
    if not _contatore_url:
        return {
            "status": "error",
            "message": "URL Contatore non configurato"
        }
    
    # Aggiorna i dati GSE
    try:
        response = requests.get(_contatore_url, timeout=30)
        
        if response.status_code != 200:
            log.error(f"Risposta non valida dal contatore: {response.status_code}")
            return {
                "status": "error",
                "message": f"Risposta non valida dal contatore: {response.status_code}"
            }
        
        html = response.text
        log.info(f"HTML contatore ricevuto: {len(html)} caratteri")
        
        # Usiamo BeautifulSoup per estrarre i dati dal contatore
        result = _extract_data_from_html(html)
        
        if "error" in result:
            return result
        
        # Aggiorna i dati e il timestamp
        _stats = result["data"]
        _last_successful_fetch_time = datetime.now()
        
        # Salva i dati su file
        save_success = _save_to_file()
        
        return {
            "status": "success",
            "message": "Dati GSE aggiornati con successo",
            "data": _stats,
            "saved_to_file": save_success
        }
    
    except Exception as e:
        log.error(f"Errore nell'aggiornamento dei dati GSE: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Errore nell'aggiornamento dei dati GSE: {str(e)}"
        }

def _extract_data_from_html(html):
    """Estrae i dati dal contenuto HTML"""
    try:
        # Usiamo BeautifulSoup per estrarre i dati
        soup = BeautifulSoup(html, 'html.parser')
        
        # Cerchiamo i tag h3 che contengono i valori
        h3_tags = soup.find_all('h3')
        
        risorse_disponibili = None
        risorse_totali = None
        risorse_prenotate = None
        risorse_utilizzate = None
        data_aggiornamento = None
        
        for h3 in h3_tags:
            text = h3.get_text().strip()
            
            # Ottieni risorse disponibili e totali
            if "Risorse disponibili:" in text:
                match_disponibili = re.search(r'€\s*([\d.,]+)', text)
                match_totali = re.search(r'di\s*€\s*([\d.,]+)', text)
                
                if match_disponibili:
                    risorse_disponibili = match_disponibili.group(1).strip()
                if match_totali:
                    risorse_totali = match_totali.group(1).strip()
            
            # Ottieni risorse prenotate
            elif "Risorse prenotate per i progetti non ancora completati" in text:
                match = re.search(r'€\s*([\d.,]+)', text)
                if match:
                    risorse_prenotate = match.group(1).strip()
            
            # Ottieni risorse utilizzate
            elif "Risorse utilizzate per progetti completati" in text:
                match = re.search(r'€\s*([\d.,]+)', text)
                if match:
                    risorse_utilizzate = match.group(1).strip()
            
            # Ottieni data aggiornamento
            elif "Data ultimo aggiornamento" in text:
                match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
                if match:
                    data_aggiornamento = match.group(1).strip()
        
        # Verifica che abbiamo ottenuto tutti i valori necessari
        missing_values = []
        if not risorse_disponibili:
            missing_values.append("risorse_disponibili")
        if not risorse_totali:
            missing_values.append("risorse_totali")
        if not risorse_prenotate:
            missing_values.append("risorse_prenotate")
        if not risorse_utilizzate:
            missing_values.append("risorse_utilizzate")
        
        if missing_values:
            log.error(f"Valori mancanti nell'estrazione dei dati: {missing_values}")
            return {
                "error": f"Impossibile estrarre tutti i valori necessari: {', '.join(missing_values)}"
            }
        
        # Crea oggetto dati
        stats_data = {
            "risorse_disponibili": risorse_disponibili,
            "risorse_totali": risorse_totali,
            "risorse_prenotate": risorse_prenotate,
            "risorse_utilizzate": risorse_utilizzate,
            "ultimo_aggiornamento": data_aggiornamento or datetime.now().strftime("%d/%m/%Y")
        }
        
        log.info(f"Dati estratti: {stats_data}")
        
        return {
            "data": stats_data
        }
    
    except Exception as e:
        log.error(f"Errore nell'estrazione dei dati: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return {
            "error": f"Errore nell'estrazione dei dati: {str(e)}"
        }

def _save_to_file():
    """Salva i dati su file per persistenza"""
    global _stats, _last_successful_fetch_time
    
    try:
        # Crea la directory se non esiste
        dir_path = os.path.dirname(DATA_FILE_PATH)
        os.makedirs(dir_path, exist_ok=True)
        
        # Salva i dati attuali con timestamp
        data_to_save = {
            **_stats,
            "timestamp": _last_successful_fetch_time.isoformat() if _last_successful_fetch_time else datetime.now().isoformat()
        }
        
        # Salva il file
        with open(DATA_FILE_PATH, "w") as f:
            json.dump(data_to_save, f, indent=2)
        
        log.info(f"Dati GSE salvati su file: {DATA_FILE_PATH}")
        return True
    except Exception as e:
        log.error(f"Errore nel salvataggio dei dati GSE: {str(e)}")
        import traceback
        log.error(traceback.format_exc())
        return False