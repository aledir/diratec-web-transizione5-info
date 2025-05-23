#!/usr/bin/env python3
"""
Script per trovare punti di taglio nei documenti markdown.
Semplice, pratico e a prova di errore.
"""

import sys
import os
import json
from pathlib import Path

def find_and_apply_positions(doc_id, documents_dir="/app/cat/shared/documents"):
    """
    Aiuta a trovare le posizioni di taglio e applica le opzioni di pulizia.
    """
    try:
        # Carica i metadati
        metadata_path = Path(documents_dir) / "metadata.json"
        if not metadata_path.exists():
            print(f"File metadata.json non trovato: {metadata_path}")
            return False
            
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Trova il documento
        doc_info = next((doc for doc in metadata.get("files", []) if doc.get("id") == doc_id), None)
        if not doc_info:
            print(f"Documento non trovato: {doc_id}")
            return False
        
        # Trova il percorso del markdown
        markdown_path = None
        if "markdown_path" in doc_info:
            markdown_path = Path(documents_dir) / doc_info["markdown_path"]
            if not markdown_path.exists():
                markdown_path = None
        
        # Se non trovato, cerca l'originale se è markdown
        if not markdown_path:
            orig_path = Path(documents_dir) / doc_info.get("path", "")
            if orig_path.suffix.lower() == ".md" and orig_path.exists():
                markdown_path = orig_path
        
        if not markdown_path or not markdown_path.exists():
            print(f"File markdown non trovato per il documento {doc_id}")
            return False
        
        # Carica il contenuto
        with open(markdown_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Dividi in righe
        lines = content.split('\n')
        total_lines = len(lines)
        
        # ===== INIZIO DOCUMENTO =====
        num_lines = 15  # Default: 15 righe
        
        while True:
            # Mostra le prime righe
            print(f"\n=== INIZIO DEL DOCUMENTO ({num_lines} righe) ===")
            for i in range(min(num_lines, total_lines)):
                print(f"{i+1}: {lines[i]}")
            
            # Chiedi all'utente se vuole vedere più righe o procedere
            view_more = False
            while True:
                action = input("\nVuoi vedere più righe? (s/n): ").strip().lower()
                if action in ['s', 'si', 'sì', 'y', 'yes']:
                    view_more = True
                    break
                elif action in ['n', 'no']:
                    view_more = False
                    break
                else:
                    print("Inserisci 's' per sì o 'n' per no")
            
            if not view_more:
                break
                
            try:
                more_lines = input("Quante righe visualizzare in totale? ")
                num_lines = int(more_lines)
            except ValueError:
                print("Numero non valido, usiamo il numero precedente")
        
        # Chiedi la riga di inizio
        while True:
            try:
                print("\nScegli la riga da cui iniziare a mantenere il testo (la riga selezionata sarà INCLUSA nel risultato)")
                riga_inizio = input("Inserisci il NUMERO DI RIGA iniziale: ")
                riga_inizio = int(riga_inizio.strip())
                
                if 1 <= riga_inizio <= total_lines:
                    # Calcola i caratteri da tagliare
                    taglia_inizio = sum(len(lines[i]) + 1 for i in range(riga_inizio - 1))
                    
                    # Mostra le righe intorno al punto di taglio
                    print("\n=== PUNTO DI TAGLIO INIZIALE ===")
                    print("Tutto il testo PRIMA di questa riga sarà rimosso")
                    start_preview = max(0, riga_inizio - 2)
                    end_preview = min(total_lines, riga_inizio + 3)
                    
                    for i in range(start_preview, end_preview):
                        marker = "→ INIZIO QUI →" if i+1 == riga_inizio else ""
                        print(f"{'>' if i+1 == riga_inizio else ' '} {i+1}: {lines[i]} {marker}")
                    
                    # Conferma
                    confirmed = False
                    while True:
                        confirm = input(f"\nConfermi di iniziare DALLA riga {riga_inizio}? (s/n): ").strip().lower()
                        if confirm in ['s', 'si', 'sì', 'y', 'yes']:
                            confirmed = True
                            break
                        elif confirm in ['n', 'no']:
                            confirmed = False
                            break
                        else:
                            print("Inserisci 's' per sì o 'n' per no")
                    
                    if confirmed:
                        break
                else:
                    print(f"Inserisci un numero di riga tra 1 e {total_lines}")
            except ValueError:
                print("Inserisci un numero valido")
            except KeyboardInterrupt:
                print("\nOperazione interrotta")
                return False
        
        # ===== FINE DOCUMENTO =====
        num_lines = 15  # Default: 15 righe
        
        while True:
            # Mostra le ultime righe
            print(f"\n=== FINE DEL DOCUMENTO ({num_lines} righe) ===")
            for i in range(max(0, total_lines - num_lines), total_lines):
                print(f"{i+1}: {lines[i]}")
            
            # Chiedi all'utente se vuole vedere più righe o procedere
            view_more = False
            while True:
                action = input("\nVuoi vedere più righe? (s/n): ").strip().lower()
                if action in ['s', 'si', 'sì', 'y', 'yes']:
                    view_more = True
                    break
                elif action in ['n', 'no']:
                    view_more = False
                    break
                else:
                    print("Inserisci 's' per sì o 'n' per no")
            
            if not view_more:
                break
                
            try:
                more_lines = input("Quante righe visualizzare in totale? ")
                num_lines = int(more_lines)
            except ValueError:
                print("Numero non valido, usiamo il numero precedente")
        
        # Chiedi la riga di fine
        while True:
            try:
                print("\nScegli la riga fino a cui mantenere il testo (la riga selezionata sarà INCLUSA nel risultato)")
                riga_fine = input("Inserisci il NUMERO DI RIGA finale: ")
                riga_fine = int(riga_fine.strip())
                
                if riga_inizio <= riga_fine <= total_lines:
                    # Calcola i caratteri da tagliare
                    taglia_fine = sum(len(lines[i]) + 1 for i in range(riga_fine, total_lines))
                    
                    # Mostra le righe intorno al punto di taglio
                    print("\n=== PUNTO DI TAGLIO FINALE ===")
                    print("Tutto il testo DOPO questa riga sarà rimosso")
                    start_preview = max(0, riga_fine - 2)
                    end_preview = min(total_lines, riga_fine + 3)
                    
                    for i in range(start_preview, end_preview):
                        marker = "← FINE QUI ←" if i+1 == riga_fine else ""
                        print(f"{'>' if i+1 == riga_fine else ' '} {i+1}: {lines[i]} {marker}")
                    
                    # Conferma
                    confirmed = False
                    while True:
                        confirm = input(f"\nConfermi di terminare FINO ALLA riga {riga_fine} (inclusa)? (s/n): ").strip().lower()
                        if confirm in ['s', 'si', 'sì', 'y', 'yes']:
                            confirmed = True
                            break
                        elif confirm in ['n', 'no']:
                            confirmed = False
                            break
                        else:
                            print("Inserisci 's' per sì o 'n' per no")
                    
                    if confirmed:
                        break
                else:
                    print(f"Inserisci un numero di riga tra {riga_inizio} e {total_lines}")
            except ValueError:
                print("Inserisci un numero valido")
            except KeyboardInterrupt:
                print("\nOperazione interrotta")
                return False
        
        # Crea un'anteprima del testo risultante
        testo_risultante = '\n'.join(lines[riga_inizio-1:riga_fine])
        lunghezza_risultante = len(testo_risultante)
        
        # Se il testo è troppo lungo, mostrarne solo l'inizio e la fine
        max_preview_length = 1000
        if len(testo_risultante) > max_preview_length:
            inizio_preview = testo_risultante[:400]
            fine_preview = testo_risultante[-400:]
            testo_preview = f"{inizio_preview}\n\n[...]\n\n{fine_preview}"
        else:
            testo_preview = testo_risultante
        
        # Riepilogo finale
        print("\n=== RIEPILOGO ===")
        print(f"Documento: {doc_id}")
        print(f"Inizio: riga {riga_inizio}")
        print(f"Fine: riga {riga_fine}")
        print(f"Tagliare {taglia_inizio} caratteri all'inizio")
        print(f"Tagliare {taglia_fine} caratteri alla fine")
        print(f"Nuova lunghezza: {lunghezza_risultante} caratteri")
        
        # Mostra anteprima
        print("\n=== ANTEPRIMA DEL TESTO RISULTANTE ===")
        print(testo_preview)
        print("\n[Fine anteprima]")
        
        # Conferma finale
        apply_changes = False
        while True:
            confirm = input("\nVuoi applicare queste modifiche? (s/n): ").strip().lower()
            if confirm in ['s', 'si', 'sì', 'y', 'yes']:
                apply_changes = True
                break
            elif confirm in ['n', 'no']:
                print("Operazione annullata")
                return False
            else:
                print("Inserisci 's' per sì o 'n' per no")
        
        if not apply_changes:
            print("Operazione annullata")
            return False
        
        # Aggiorna il file di metadati
        doc_index = next((i for i, doc in enumerate(metadata.get("files", [])) 
                         if doc.get("id") == doc_id), None)
        
        if doc_index is None:
            print(f"Documento non trovato nei metadati: {doc_id}")
            return False
        
        # Aggiorna le opzioni di pulizia
        clean_options = {
            "taglia_caratteri_inizio": taglia_inizio,
            "taglia_caratteri_fine": taglia_fine
        }
        
        metadata["files"][doc_index]["clean_options"] = clean_options
        
        # Imposta anche converti_cag su true
        metadata["files"][doc_index]["converti_cag"] = True
        
        # Salva i metadati
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        # Calcola e mostra gli indicatori dell'operazione
        lunghezza_originale = len(content)
        percentuale_riduzione = ((taglia_inizio + taglia_fine) / lunghezza_originale) * 100
        
        # Anteprima del testo iniziale e finale
        inizio_testo = lines[riga_inizio-1].strip()
        fine_testo = lines[riga_fine-1].strip()
        
        # Limita la lunghezza per visualizzazione
        max_preview_char = 50
        if len(inizio_testo) > max_preview_char:
            inizio_testo = inizio_testo[:max_preview_char] + "..."
        if len(fine_testo) > max_preview_char:
            fine_testo = "..." + fine_testo[-max_preview_char:]
        
        print(f"\nMetadati aggiornati con successo in {metadata_path}!")
        print("=== METADATI AGGIORNATI CON SUCCESSO ===")
        print(f"Opzioni di pulizia impostate:")
        print(f"  - Taglio iniziale: {taglia_inizio} caratteri (rimuove le prime {riga_inizio-1} righe)")
        print(f"  - Taglio finale: {taglia_fine} caratteri (rimuove le righe dalla {riga_fine+1} alla {total_lines})")
        print(f"  - Documento originale: {lunghezza_originale} caratteri / {total_lines} righe")
        print(f"  - Documento risultante: {lunghezza_risultante} caratteri / {riga_fine - riga_inizio + 1} righe")
        print(f"  - Riduzione: {percentuale_riduzione:.1f}% del contenuto originale")
        print(f"  - Il documento inizierà con: \"{inizio_testo}\"")
        print(f"  - Il documento terminerà con: \"{fine_testo}\"")
        print(f"  - Queste modifiche verranno applicate quando il contesto CAG verrà rigenerato")
        
        return True
        
    except Exception as e:
        print(f"Errore: {str(e)}")
        return False

def get_markdown_documents(documents_dir="/app/cat/shared/documents"):
    """
    Restituisce i documenti attivi con file markdown esistenti o con converti_cag=true.
    """
    try:
        # Carica i metadati
        metadata_path = Path(documents_dir) / "metadata.json"
        if not metadata_path.exists():
            print(f"File metadata.json non trovato: {metadata_path}")
            return []
            
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        markdown_docs = []
        
        # Controlla ogni documento attivo
        for doc in metadata.get("files", []):
            if doc.get("stato") != "attivo":
                continue
                
            # Priorità 1: documenti con converti_cag=true
            if doc.get("converti_cag") == True:
                markdown_docs.append(doc)
                continue
                
            # Priorità 2: documenti con file markdown esistenti
            markdown_path = None
            if "markdown_path" in doc:
                markdown_path = Path(documents_dir) / doc["markdown_path"]
                if markdown_path.exists():
                    markdown_docs.append(doc)
                    continue
            
            # Priorità 3: documenti originali che sono markdown
            orig_path = Path(documents_dir) / doc.get("path", "")
            if orig_path.suffix.lower() == ".md" and orig_path.exists():
                markdown_docs.append(doc)
        
        return markdown_docs
    except Exception as e:
        print(f"Errore nel recupero dei documenti markdown: {str(e)}")
        return []

def interactive_mode():
    """Esegue lo script in modalità interattiva."""
    print("=== TROVA PUNTI DI TAGLIO NEI DOCUMENTI MARKDOWN ===")
    print("Questo strumento ti aiuta a eliminare parti non necessarie all'inizio e alla fine dei file markdown.")
    print("Le righe che selezioni saranno INCLUSE nel testo finale.")
    
    # Elenca documenti disponibili in formato markdown
    print("\nRecupero documenti markdown disponibili...")
    docs = get_markdown_documents()
    
    if not docs:
        print("Nessun documento markdown trovato!")
        return False
    
    print("\nDocumenti markdown disponibili:")
    for i, doc in enumerate(docs, 1):
        # Aggiungi indicatore per converti_cag=true
        cag_indicator = " [CAG]" if doc.get("converti_cag") == True else ""
        print(f"{i}. {doc.get('id')} - {doc.get('titolo', 'Senza titolo')}{cag_indicator}")
    
    # Chiedi ID documento
    doc_id = None
    
    while doc_id is None:
        try:
            selection = input("\nInserisci il numero del documento da elaborare (o 'q' per uscire): ")
            
            if selection.lower() == 'q':
                print("Operazione annullata")
                return False
            
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(docs):
                    doc_id = docs[idx]['id']
                    doc_title = docs[idx].get('titolo', 'Senza titolo')
                    print(f"Documento selezionato: {doc_id} - {doc_title}")
                else:
                    print(f"Selezione non valida. Inserisci un numero tra 1 e {len(docs)}")
                    doc_id = None
            except ValueError:
                print("Inserisci un numero valido o 'q' per uscire")
                doc_id = None
                
        except KeyboardInterrupt:
            print("\nOperazione interrotta")
            return False
    
    # Analizza e applica le opzioni di pulizia
    return find_and_apply_positions(doc_id)

def print_usage():
    print("Utilizzo:")
    print(f"python3 {sys.argv[0]}")
    print("\nQuesto script ti aiuta a trovare i punti di taglio in un documento markdown.")
    print("Ti mostrerà l'inizio e la fine del documento e ti chiederà di specificare")
    print("le righe da cui iniziare e fino a cui mantenere il testo.")
    print("Le righe selezionate saranno INCLUSE nel testo finale.")

if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            # Modalità interattiva
            success = interactive_mode()
        else:
            print_usage()
            sys.exit(1)
        
        if success:
            print("\nProcesso completato con successo!")
        else:
            print("\nProcesso fallito o annullato!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperazione interrotta dall'utente")
        sys.exit(1)