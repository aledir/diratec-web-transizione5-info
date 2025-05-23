"""Funzioni di utilità condivise tra i vari moduli."""
import os
from cat.log import log

def load_prompt_file(filename):
    """
    Carica un file prompt dalla directory prompts.
    
    Args:
        filename: Nome del file prompt da caricare
        
    Returns:
        str: Contenuto del file prompt
        
    Raises:
        FileNotFoundError: Se il file non esiste
        IOError: Se ci sono problemi nella lettura del file
    """
    # Ottieni il percorso del file corrente
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Costruisci il percorso del file prompt
    prompt_path = os.path.join(current_dir, "prompts", filename)
    
    # Verifica che il file esista - solleva eccezione se non esiste
    if not os.path.exists(prompt_path):
        log.error(f"❌ File prompt non trovato: {prompt_path}")
        raise FileNotFoundError(f"File prompt non trovato: {prompt_path}")
    
    # Leggi il contenuto del file
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    log.info(f"✅ File prompt caricato: {filename}")
    return content