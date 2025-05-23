"""Funzionalità per la pulizia testo dei documenti."""
import re
from cat.log import log
from cat.mad_hatter.decorators import hook

@hook
def before_document_ingest(content, metadata, cat):
    """Pulisce il testo prima dell'ingestione nel RAG"""
    # Se il contenuto è stringa (testo), applica pulizia
    if isinstance(content, str):
        cleaned_content = clean_text(content, metadata)
        return cleaned_content, metadata
    return content, metadata

def clean_text(text, metadata=None):
    """Applica pulizia al testo in base al tipo di documento"""
    # Ottieni il tipo di documento dal nome del file o dai metadati
    doc_type = None
    if metadata and "tipo" in metadata:
        doc_type = metadata["tipo"].lower()
    elif metadata and "source" in metadata:
        filename = metadata["source"].lower()
        if "faq" in filename:
            doc_type = "faq"
        elif "circolare" in filename:
            doc_type = "circolare"
        elif "decreto" in filename or "legge" in filename:
            doc_type = "normativa"
    
    # Pulizia di base per tutti i documenti
    cleaned_text = basic_cleaning(text)
    
    # Pulizia specifica per tipo di documento
    if doc_type == "faq":
        cleaned_text = clean_faq(cleaned_text)
    elif doc_type == "circolare":
        cleaned_text = clean_circolare(cleaned_text)
    elif doc_type == "normativa":
        cleaned_text = clean_normativa(cleaned_text)
    
    return cleaned_text

def basic_cleaning(text):
    """Pulizia di base applicata a tutti i documenti"""
    # Rimuovi sequenze di punti ripetuti
    cleaned = re.sub(r'\.{2,}', '. ', text)
    
    # Sostituisci caratteri speciali CID 
    cleaned = re.sub(r'\(cid:\d+\)', '', cleaned)
    
    # Normalizza gli spazi
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Rimuovi caratteri di controllo
    cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', cleaned)
    
    # Normalizza i ritorni a capo multipli
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Standardizza i trattini
    cleaned = re.sub(r'[‐‑‒–—―]', '-', cleaned)
    
    return cleaned

def clean_faq(text):
    """Pulizia specifica per documenti FAQ"""
    # Identifica e standardizza i pattern di domanda/risposta
    cleaned = re.sub(r'(\d+\.\d+)\s*\.?\s*([QD]|Domanda)[\s:.]+', r'\1. D: ', text)
    cleaned = re.sub(r'([QD]|Domanda)[\s:.]+', 'D: ', cleaned)
    cleaned = re.sub(r'([AR]|Risposta)[\s:.]+', 'R: ', cleaned)
    
    # Assicura separazione chiara tra D e R
    cleaned = re.sub(r'(D:.+?)(\s*R:)', r'\1\n\2', cleaned)
    
    # Assicura separazione tra FAQ diverse
    cleaned = re.sub(r'(R:.+?)(\n\d+\.\d+\.)', r'\1\n\n\2', cleaned)
    
    return cleaned

def clean_circolare(text):
    """Pulizia specifica per circolari"""
    # Miglioramento leggibilità formule matematiche
    cleaned = re.sub(r'(𝑅𝑅𝐼𝐼𝑅𝑅𝑅𝑅|𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼𝐼)', 'RISP', text)
    
    # Rimuovi caratteri matematici speciali superflui
    cleaned = re.sub(r'[𝑝𝑝𝐼𝐼𝐼𝐼𝑉𝑉𝐼𝐼𝑂𝑂𝐼𝐼𝑎𝑎𝑛𝑛𝑎𝑎]', 'p', cleaned)
    
    # Standardizza le equazioni
    cleaned = re.sub(r'Equazione \d+:', 'FORMULA:', cleaned)
    
    return cleaned

def clean_normativa(text):
    """Pulizia specifica per decreti e leggi"""
    # Standardizza riferimenti a commi e articoli
    cleaned = re.sub(r'[aA]rt\.\s*(\d+)', r'Articolo \1', text)
    cleaned = re.sub(r'[cC]omma\s*(\d+)', r'Comma \1', cleaned)
    
    # Migliora la formattazione delle liste numerate
    cleaned = re.sub(r'(\n\s*)([a-z])\)\s*', r'\1- ', cleaned)
    
    return cleaned

def fix_pdf_layout_issues(text):
    """Corregge problemi comuni nei PDF estratti"""
    # Unisci parole divise a fine riga
    cleaned = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    
    # Correggi intestazioni spezzate
    cleaned = re.sub(r'(\d+\.\d+)\s*\n\s*([A-Z])', r'\1 \2', cleaned)
    
    # Correggi tabelle senza layout
    cleaned = re.sub(r'(\d+)\s*\|\s*(\d+)', r'\1: \2', cleaned)
    
    return cleaned