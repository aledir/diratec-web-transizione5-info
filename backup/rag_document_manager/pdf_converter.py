"""Funzionalità per convertire PDF in Markdown utilizzando Mathpix."""
import os
import requests
import json
import time
from pathlib import Path
from cat.log import log

class MathpixConverter:
    """Gestisce la conversione dei PDF in Markdown tramite API Mathpix."""
    
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key
        self.headers = {
            "app_id": app_id,
            "app_key": app_key
        }
        # API URL in base alla documentazione ufficiale
        self.api_url = "https://api.mathpix.com/v3/pdf"
    
    def convert_pdf(self, pdf_path, output_dir=None):
        """
        Converte un file PDF in Markdown usando Mathpix.
        
        Args:
            pdf_path: Percorso del file PDF da convertire
            output_dir: Directory in cui salvare l'output (opzionale)
            
        Returns:
            dict: Risultato della conversione con percorso del file markdown
        """
        try:
            # Prepara il percorso di output
            pdf_path = Path(pdf_path)
            if not output_dir:
                output_dir = pdf_path.parent
            else:
                output_dir = Path(output_dir)
                os.makedirs(output_dir, exist_ok=True)
            
            output_filename = f"{pdf_path.stem}.md"
            output_path = output_dir / output_filename
            
            # Controlla se il file è già stato convertito
            if output_path.exists():
                log.info(f"File markdown già esistente: {output_path}")
                return {
                    "success": True,
                    "markdown_path": str(output_path),
                    "from_cache": True
                }
            
            log.info(f"Conversione PDF: {pdf_path}")
            
            # STEP 1: Converti il PDF usando l'API Mathpix
            # Implementazione basata sulla documentazione ufficiale: https://mathpix.com/docs/convert/endpoints
            
            # Le opzioni corrette in base alla documentazione
            options = {
                "conversion_formats": {
                    "md": True
                }
            }
            
            log.info("Invio richiesta POST a Mathpix convertire il PDF...")
            
            # Upload del file PDF con il form multipart
            with open(pdf_path, 'rb') as pdf_file:
                files = {'file': (pdf_path.name, pdf_file, 'application/pdf')}
                data = {'options_json': json.dumps(options)}
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code != 200:
                log.error(f"Errore nella richiesta: {response.status_code}, {response.text}")
                return {
                    "success": False,
                    "error": f"Errore richiesta: {response.status_code}"
                }
            
            # Estrai l'ID conversione
            response_data = response.json()
            pdf_id = response_data.get("pdf_id")
            if not pdf_id:
                log.error(f"PDF ID non trovato nella risposta: {response_data}")
                return {
                    "success": False,
                    "error": "PDF ID non trovato"
                }
            
            log.info(f"PDF caricato con ID: {pdf_id}")
            
            # STEP 2: Attendi il completamento
            status_url = f"{self.api_url}/{pdf_id}"
            wait_time = 5  # secondi tra i controlli
            max_wait = 300  # tempo massimo di attesa (5 minuti)
            start_time = time.time()
            
            log.info("Monitoraggio dello stato della conversione...")
            
            while (time.time() - start_time) < max_wait:
                time.sleep(wait_time)
                
                status_response = requests.get(status_url, headers=self.headers)
                if status_response.status_code != 200:
                    log.error(f"Errore nel controllo stato: {status_response.status_code}, {status_response.text}")
                    continue
                
                status_data = status_response.json()
                status = status_data.get("status")
                
                if "percent_done" in status_data:
                    log.info(f"Progresso: {status_data['percent_done']}%")
                
                if status == "completed":
                    log.info("Conversione completata!")
                    break
                elif status == "error":
                    error_msg = status_data.get("error", "Errore sconosciuto")
                    log.error(f"Errore nella conversione: {error_msg}")
                    return {
                        "success": False,
                        "error": f"Errore conversione: {error_msg}"
                    }
            
            # STEP 3: Scarica il risultato in formato Markdown
            # In base alla documentazione ufficiale: https://mathpix.com/docs/convert/endpoints
            # Dobbiamo usare l'endpoint "GET /v3/pdf/{pdf_id}.md" come specificato
            
            log.info(f"Download del markdown usando l'endpoint ufficiale...")
            
            # L'URL corretto secondo la documentazione
            download_url = f"{self.api_url}/{pdf_id}.md"
            
            download_response = requests.get(
                download_url,
                headers=self.headers,
                timeout=30
            )
            
            if download_response.status_code != 200:
                log.error(f"Errore nel download: {download_response.status_code}, {download_response.text}")
                return {
                    "success": False,
                    "error": f"Errore download: {download_response.status_code}"
                }
            
            # Salva il markdown
            markdown_content = download_response.text
            
            if not markdown_content:
                log.error("Contenuto markdown vuoto")
                return {
                    "success": False,
                    "error": "Contenuto markdown vuoto"
                }
            
            log.info(f"Markdown ricevuto, lunghezza: {len(markdown_content)} caratteri")
            
            # Anteprima dei primi 200 caratteri
            preview = markdown_content[:200] + "..." if len(markdown_content) > 200 else markdown_content
            log.info(f"Anteprima del contenuto: {preview}")
            
            # Salva il file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            log.info(f"File markdown salvato in: {output_path}")
            
            return {
                "success": True,
                "markdown_path": str(output_path),
                "from_cache": False
            }
            
        except Exception as e:
            log.error(f"Errore generale: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }