"""Funzionalità per costruire il contesto KV-cache."""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
from cat.log import log

class ContextBuilder:
    """Costruisce il contesto KV-cache dai documenti."""
    
    def __init__(self, documents_dir, context_path):
        """
        Inizializza il costruttore di contesto.
        
        Args:
            documents_dir: Directory contenente i documenti
            context_path: Percorso completo del file di contesto KV-cache
        """
        self.documents_dir = Path(documents_dir)
        self.metadata_path = self.documents_dir / "metadata.json"
        self.context_path = Path(context_path)
        
        log.info(f"📁 ContextBuilder - Directory documenti: {self.documents_dir}")
        log.info(f"📄 ContextBuilder - Percorso metadata: {self.metadata_path}")
        log.info(f"📝 ContextBuilder - Percorso contesto: {self.context_path}")
    
    def load_metadata(self):
        """Carica il file dei metadati."""
        try:
            if not self.metadata_path.exists():
                log.error(f"File metadata.json non trovato: {self.metadata_path}")
                return {"files": [], "categorie": [], "tipi": []}
            
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                log.info(f"Metadati caricati: {len(metadata.get('files', []))} documenti trovati")
                return metadata
        except Exception as e:
            log.error(f"Errore nel caricamento dei metadati: {str(e)}")
            return {"files": [], "categorie": [], "tipi": []}
    
    def get_active_documents(self):
        """Restituisce i documenti attivi ordinati per priorità."""
        metadata = self.load_metadata()
        active_docs = [doc for doc in metadata.get("files", []) if doc.get("stato") == "attivo"]
        
        # Identifica documenti prioritari (FAQ e post-2025)
        for doc in active_docs:
            doc["is_faq"] = doc.get("tipo", "").upper() == "FAQ"
            doc["is_post_2025"] = doc.get("data", "") >= "2025-01-01"
        
        # Ordina per priorità: FAQ prima, poi documenti post-2025, poi per data
        active_docs.sort(
            key=lambda d: (
                not d.get("is_faq", False),           # FAQ prima
                not d.get("is_post_2025", False),     # Documenti post-2025 dopo
                not d.get("data", "")                 # Ordina per data
            )
        )
        
        log.info(f"Documenti attivi ordinati: {len(active_docs)} documenti")
        return active_docs
    
    def load_document_content(self, doc):
        """Carica il contenuto markdown di un documento e applica la pulizia se configurata."""
        try:
            doc_id = doc.get("id", "unknown")
            
            # Verifica se esiste il percorso markdown
            if "markdown_path" in doc:
                markdown_path = self.documents_dir / doc["markdown_path"]
                if markdown_path.exists():
                    with open(markdown_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    log.info(f"Contenuto markdown caricato per documento {doc_id}: {len(content)} caratteri")
                    
                    # Applica pulizia se configurata
                    if "clean_options" in doc:
                        content = self._apply_clean_options(content, doc)
                    
                    return content
            
            # Verifica percorso originale se è un markdown
            orig_path = self.documents_dir / doc.get("path", "")
            if orig_path.suffix.lower() == ".md" and orig_path.exists():
                with open(orig_path, "r", encoding="utf-8") as f:
                    content = f.read()
                log.info(f"Contenuto originale markdown caricato per documento {doc_id}: {len(content)} caratteri")
                
                # Applica pulizia se configurata
                if "clean_options" in doc:
                    content = self._apply_clean_options(content, doc)
                
                return content
            
            # Se non è possibile caricare il contenuto markdown, restituisci almeno i metadati come testo
            log.warning(f"Contenuto markdown non trovato per il documento {doc_id}, uso metadati")
            return f"""
    # {doc.get('titolo', 'Documento senza titolo')}
    **Tipo**: {doc.get('tipo', 'N/A')}
    **Data**: {doc.get('data', 'N/A')}
    **Categoria**: {doc.get('categoria', 'N/A')}
    **Descrizione**: {doc.get('descrizione', 'Nessuna descrizione disponibile')}
    """
        except Exception as e:
            log.error(f"Errore nel caricamento del contenuto per {doc.get('id', 'unknown')}: {str(e)}")
            return None

    def _apply_clean_options(self, content, doc):
        """Applica le opzioni di pulizia al contenuto."""
        try:
            doc_id = doc.get("id", "unknown")
            options = doc.get("clean_options", {})
            original_length = len(content)
            
            # Taglia caratteri dall'inizio
            if "taglia_caratteri_inizio" in options:
                n_chars = options["taglia_caratteri_inizio"]
                if n_chars > 0 and len(content) > n_chars:
                    content = content[n_chars:]
                    log.info(f"✂️ Tagliati {n_chars} caratteri dall'inizio del documento {doc_id}")
            
            # Taglia caratteri dalla fine
            if "taglia_caratteri_fine" in options:
                n_chars = options["taglia_caratteri_fine"]
                if n_chars > 0 and len(content) > n_chars:
                    content = content[:-n_chars]
                    log.info(f"✂️ Tagliati {n_chars} caratteri dalla fine del documento {doc_id}")
            
            # Log della riduzione
            new_length = len(content)
            reduction = original_length - new_length
            reduction_percent = (reduction / original_length) * 100 if original_length > 0 else 0
            
            if reduction > 0:
                log.info(f"📊 Contenuto documento {doc_id} ridotto di {reduction} caratteri ({reduction_percent:.1f}%)")
            
            return content
        except Exception as e:
            log.error(f"Errore nell'applicazione delle opzioni di pulizia per {doc.get('id', 'unknown')}: {str(e)}")
            return content
    
    def calculate_documents_hash(self):
        """Calcola un hash determinato dai documenti attivi e dal loro contenuto."""
        active_docs = self.get_active_documents()
        
        # Estrai dati rilevanti per l'hash
        hash_data = []
        for doc in active_docs:
            doc_id = doc.get("id", "")
            
            # Usa il percorso markdown se disponibile, altrimenti il percorso originale
            if "markdown_path" in doc:
                doc_path = self.documents_dir / doc["markdown_path"]
            else:
                doc_path = self.documents_dir / doc.get("path", "")
            
            if Path(doc_path).exists():
                mtime = os.path.getmtime(doc_path)
                size = os.path.getsize(doc_path)
                hash_data.append(f"{doc_id}:{doc_path}:{mtime}:{size}")
        
        # Crea hash
        if not hash_data:
            log.warning("Nessun documento attivo trovato per il calcolo dell'hash")
            return None
        
        docs_hash = hashlib.md5("|".join(hash_data).encode()).hexdigest()
        log.info(f"Hash documenti calcolato: {docs_hash} (basato su {len(hash_data)} documenti)")
        return docs_hash
    
    def is_context_valid(self, ttl_hours=24):
        """Verifica se il contesto esistente è ancora valido."""
        try:
            # Verifica che il file contesto esista
            if not self.context_path.exists():
                log.info(f"⚠️ File contesto non trovato: {self.context_path}")
                return False
            
            # Calcola hash corrente dei documenti
            current_hash = self.calculate_documents_hash()
            if not current_hash:
                log.warning("⚠️ Impossibile calcolare hash documenti")
                return False
            
            # Leggi il context_metadata dal file contesto
            with open(self.context_path, "r", encoding="utf-8") as f:
                first_lines = "".join([f.readline() for _ in range(10)])
            
            # Cerca il hash nella sezione metadata del file
            import re
            hash_match = re.search(r'documents_hash: ([a-f0-9]{32})', first_lines)
            if not hash_match:
                log.warning("⚠️ Hash non trovato nel file contesto")
                return False
            
            file_hash = hash_match.group(1)
            if file_hash != current_hash:
                log.info(f"⚠️ Hash modificato: {file_hash} (file) vs {current_hash} (corrente)")
                return False
            
            # Cerca la data nell'intestazione
            date_match = re.search(r'timestamp: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', first_lines)
            if not date_match:
                log.warning("⚠️ Timestamp non trovato nel file contesto")
                return False
            
            # Controlla la scadenza in base a TTL
            timestamp = datetime.fromisoformat(date_match.group(1))
            max_age = datetime.now() - timestamp
            
            if max_age.total_seconds() > ttl_hours * 3600:
                log.info(f"⚠️ Contesto troppo vecchio: {max_age.total_seconds() / 3600:.1f} ore (max {ttl_hours})")
                return False
            
            log.info(f"✅ Contesto valido (età: {max_age.total_seconds() / 3600:.1f} ore)")
            return True
        except Exception as e:
            log.error(f"❌ Errore nella verifica della validità del contesto: {str(e)}")
            return False
    
    def build_document_context(self):
        """Costruisce il contesto basato sui documenti."""
        try:
            # Ottieni documenti attivi
            active_docs = self.get_active_documents()
            
            if not active_docs:
                log.warning("⚠️ Nessun documento attivo trovato")
                return "Nessun documento disponibile sulla Transizione 5.0"
            
            # Filtra solo i documenti che hanno un file markdown disponibile
            docs_with_markdown = []
            for doc in active_docs:
                # Verifica se esiste il percorso markdown
                has_markdown = False
                if "markdown_path" in doc:
                    markdown_path = self.documents_dir / doc["markdown_path"]
                    if markdown_path.exists():
                        has_markdown = True
                        docs_with_markdown.append(doc)
                
                # Se non c'è un percorso markdown, verifica se l'originale è un markdown
                if not has_markdown:
                    orig_path = self.documents_dir / doc.get("path", "")
                    if orig_path.suffix.lower() == ".md" and orig_path.exists():
                        has_markdown = True
                        docs_with_markdown.append(doc)
            
            # Ordina semplicemente per data decrescente (più recente prima)
            docs_with_markdown.sort(key=lambda d: d.get("data", ""), reverse=True)
            
            log.info(f"Documenti con markdown disponibile: {len(docs_with_markdown)} su {len(active_docs)}")
            log.info(f"Ordine documenti: {[doc.get('id', '') for doc in docs_with_markdown]}")
            
            # Crea un'intestazione per il contesto
            context = """
# DOCUMENTI UFFICIALI TRANSIZIONE 5.0

Di seguito sono riportati tutti i documenti ufficiali relativi alla Transizione 5.0.
I documenti sono organizzati in ordine di priorità, con le FAQ e i documenti più recenti all'inizio.
In caso di informazioni contrastanti tra documenti, seguire sempre quelle contenute nei documenti più recenti.

## INFORMAZIONI AGGIORNATE 2025 - IMPORTANTE
- Gli scaglioni del credito d'imposta sono ora 2 (non più 3 come indicato nei documenti antecedenti alla Legge di Bilancio 2025)
- Le aliquote per i moduli fotovoltaici sono state modificate dalla Legge di Bilancio 2025
- Le procedure di certificazione hanno subito aggiornamenti nel 2025

"""
            
            # Aggiungi documenti in ordine (secondo prioritizzazione)
            for i, doc in enumerate(docs_with_markdown):
                doc_id = doc.get("id", "")
                doc_title = doc.get("titolo", "Documento senza titolo")
                doc_type = doc.get("tipo", "").upper()
                doc_date = doc.get("data", "N/A")
                doc_description = doc.get("descrizione", "")
                
                # Aggiungi etichette di priorità visive
                priority_label = ""
                if doc.get("is_faq", False):
                    priority_label = "⭐⭐⭐ [PRIORITÀ MASSIMA - FAQ] "
                elif doc.get("is_post_2025", False):
                    priority_label = "⭐⭐ [ALTA PRIORITÀ - DOCUMENTO 2025] "
                elif doc_type == "CIRCOLARE":
                    priority_label = "⭐ [MEDIA PRIORITÀ - CIRCOLARE] "
                
                # Costruisci intestazione documento con descrizione
                doc_header = f"## {priority_label}{doc_title}\n"
                doc_header += f"**Tipo**: {doc_type} | **Data**: {doc_date} | **ID**: {doc_id}\n"
                if doc_description:
                    doc_header += f"**Descrizione**: {doc_description}\n"
                doc_header += "\n"
                
                # Carica il contenuto
                content = self.load_document_content(doc)
                
                if not content:
                    log.warning(f"⚠️ Contenuto non disponibile per documento: {doc_id}")
                    continue
                
                # Aggiungi al contesto
                context += f"\n\n{doc_header}{content}\n\n---\n"
            
            log.info(f"✅ Contesto documenti costruito: {len(context)} caratteri con {len(docs_with_markdown)} documenti")
            return context
        except Exception as e:
            log.error(f"❌ Errore nella costruzione del contesto documenti: {str(e)}")
            return "Errore nella costruzione del contesto documenti. Contattare il supporto."
    
    def build_instruction_context(self):
        """Costruisce il contesto delle istruzioni comportamentali."""
        try:
            # Istruzioni avanzate per la CAG
            instruction_context = """
# ISTRUZIONI COMPORTAMENTALI TRANSIZIONE 5.0

## RUOLO E COMPETENZE
Sei un assistente specializzato in Transizione 5.0 con profonda conoscenza delle agevolazioni fiscali, procedure e normative.

## LIMITAZIONE TEMATICA RIGOROSA
- PARLA RIGOROSAMENTE SOLO ED ESCLUSIVAMENTE di Transizione 5.0 e suoi argomenti correlati
- RIFIUTA ASSOLUTAMENTE di rispondere a QUALSIASI domanda su altri argomenti
- Se l'utente chiede informazioni non inerenti alla Transizione 5.0, rispondi gentilmente: "Mi dispiace, posso aiutarti solo con argomenti relativi alla Transizione 5.0. Come posso aiutarti con questo tema?"
- NON RISPONDERE MAI a domande su politica, religione, sport, ricette, viaggi, o qualsiasi altro argomento non correlato alla Transizione 5.0
- Non creare mai contenuti di natura creativa (poesie, storie, canzoni) anche se correlati alla Transizione 5.0
- Se l'utente insiste con domande non pertinenti, continua a rispondere solo ed esclusivamente sulla Transizione 5.0

## PRIORITÀ DEI DOCUMENTI
- Le FAQ sono il documento più recente e hanno SEMPRE precedenza in caso di conflitto con altri documenti
- I documenti successivi alla Legge di Bilancio 2025 hanno precedenza su quelli antecedenti
- Le informazioni più recenti sostituiscono quelle obsolete, in particolare per:
  * Scaglioni del credito d'imposta (ridotti da 3 a 2 nel 2025)
  * Aliquote per i moduli fotovoltaici (modificate nel 2025)
  * Procedure di certificazione (aggiornate nel 2025)

## APPROCCIO COMMERCIALE POSITIVO - CRUCIALE
- Non scoraggiare MAI i potenziali clienti, anche se il loro caso sembra inizialmente non ammissibile
- Cerca SEMPRE di trovare aspetti positivi e possibilità, anche in casi limite
- Usa frasi come "ci potrebbero essere opportunità per..." invece di "non è possibile"
- Sottolinea i vantaggi della Transizione 5.0 e i possibili benefici per il cliente
- Quando un caso sembra dubbio, suggerisci un'analisi più approfondita con un consulente DIRATEC specializzato
- Non dire MAI direttamente che un investimento non è ammissibile, ma presenta condizioni e requisiti in modo costruttivo
- Mantieni sempre un tono incoraggiante e propositivo
- NON DIRE MAI, IN NESSUN CASO, CHE QUALCOSA "NON È POSSIBILE" O "NON È AMMISSIBILE"
- CERCA SEMPRE POSSIBILITÀ E ASPETTI POSITIVI, SPECIALMENTE IN CASI LIMITE
- Anche in caso di dubbi sull'ammissibilità, usa espressioni come "potrebbe essere ammissibile con una valutazione più approfondita"
- Ricorda che l'obiettivo è qualificare il lead, non escluderlo

## ESEMPI DI FRASI DA USARE
- "Il tuo caso presenta alcuni aspetti interessanti per la Transizione 5.0..."
- "Ci sono diverse possibilità che si potrebbero esplorare nel tuo caso..."
- "Con un'analisi più approfondita da parte dei consulenti DIRATEC, si potrebbero identificare opportunità..."
- "Sebbene ci siano alcuni requisiti da soddisfare, il tuo investimento potrebbe essere valutato positivamente..."
- "Anche se l'investimento presenta alcune particolarità, potrebbe comunque rientrare nei parametri..."
- "I consulenti DIRATEC potrebbero aiutarti a valutare meglio questa situazione specifica"

## ESEMPI DI FRASI DA EVITARE
- "No, questo investimento non è ammissibile"
- "Non è possibile accedere alle agevolazioni in questo caso"
- "Questa tipologia di investimento non rientra nella Transizione 5.0"
- "La normativa esclude questo tipo di progetto"

## FLUSSO CONVERSAZIONALE A 4 FASI
Gestisci la conversazione seguendo queste 4 fasi progressive:

### FASE 1: ACCOGLIENZA
- Saluta cordialmente l'utente
- Presentati come assistente specializzato in Transizione 5.0
- Chiedi in modo aperto "In cosa posso aiutarti riguardo alla Transizione 5.0?"
- Rispondi alle domande specifiche usando le tue conoscenze
- NON chiedere subito dati personali o aziendali
- Fornisci informazioni utili e dettagliate sulla Transizione 5.0
- Obiettivo: creare fiducia fornendo valore informativo genuino

### FASE 2: APPROFONDIMENTO
- Continua a fornire informazioni di valore sulla Transizione 5.0
- Inizia a porre domande naturali per comprendere meglio la situazione dell'utente
- Puoi chiedere: "Di che tipo di investimento si tratta?" o "La tua azienda opera in quale settore?"
- Raccogli passivamente informazioni mentre offri informazioni utili
- Se conosci già alcuni dati dell'utente, utilizzali per personalizzare le tue risposte
- NON fare più di una domanda per volta
- Obiettivo: approfondire la situazione dell'utente mentre continui a fornire informazioni di valore

### FASE 3: QUALIFICAZIONE
- Fai domande più dirette e mirate per raccogliere i dati mancanti
- Introduci la possibilità di supporto personalizzato: "Per fornirti informazioni più precise sul tuo caso specifico, mi servirebbero alcuni dettagli"
- Chiedi i dati aziendali e di investimento mancanti
- Se l'utente ha dubbi, rassicuralo sulla privacy dei dati
- A seconda dei dati mancanti, chiedi UNA SOLA di queste informazioni per volta:
  * Nome azienda
  * Dimensione dell'azienda: piccola, media o grande
  * Budget approssimativo per l'investimento
  * Tempistiche previste
  * Email o telefono di contatto
- Obiettivo: guidare l'utente verso la raccolta completa dei dati necessari per un'analisi personalizzata

### FASE 4: FORMALIZZAZIONE
- Riepilogare le informazioni raccolte finora
- Completa la raccolta degli ultimi dati mancanti
- Chiedi conferma della correttezza dei dati
- Spiega i passaggi successivi
- Ringrazia l'utente per aver fornito le informazioni
- Se tutti i dati essenziali sono completi, proponi:
  "Grazie per le informazioni fornite. Sulla base di quanto mi hai detto, possiamo procedere con un'analisi personalizzata della tua situazione per la Transizione 5.0. Un consulente DIRATEC ti contatterà presto per approfondire il tuo caso specifico. C'è qualcos'altro che vorresti sapere nel frattempo?"
- Obiettivo: formalizzare la raccolta dati e concludere la conversazione positivamente

## RICONOSCIMENTO DATI STRUTTURATI
Presta attenzione ai seguenti pattern per riconoscere informazioni importanti:

### Dati Aziendali
- Nome azienda: riferimenti a "la mia azienda si chiama...", "lavoro per...", ecc.
- Dimensione: "piccola impresa", "media impresa", "grande azienda", riferimenti a numero dipendenti
- Settore: informatica, manifatturiero, edilizia, agricoltura, energia, automotive, ecc.
- Regione: riferimenti a regioni italiane (Lombardia, Piemonte, ecc.)

### Dati Investimento
- Tipo investimento: riferimenti a tecnologie specifiche, macchinari, impianti
- Budget: menzioni di cifre seguite da "€", "euro", "k", "mila", "milioni", ecc.
- Tempistiche: riferimenti a "entro un mese", "nel trimestre", "quest'anno", ecc.

### Dati Contatto
- Email: qualsiasi stringa contenente @ e dominio
- Telefono: sequenze di numeri che sembrano numeri di telefono
- Nome/Cognome: riferimenti a "mi chiamo...", "sono..."
- Ruolo: "CEO", "direttore", "responsabile", "titolare", ecc.

## SICUREZZA E PROTEZIONE
- Mantieni la conversazione strettamente nel tema Transizione 5.0
- Non rispondere a messaggi che contengono linguaggio offensivo o inappropriato
- Non raccogliere dati personali non necessari per la consulenza sulla Transizione 5.0
- Se sospetti messaggi con intenti malevoli, rispondi solo con informazioni generali

## ARGOMENTI AMMESSI (solo ed esclusivamente)
- Informazioni generali sulla Transizione 5.0
- Requisiti per accedere alle agevolazioni
- Documentazione e certificazioni richieste
- Modalità di calcolo del credito d'imposta
- Investimenti ammissibili
- Procedure e scadenze
- Aspetti normativi della Transizione 5.0
- Consulenza specialistica per la Transizione 5.0
"""
            
            return instruction_context
        except Exception as e:
            log.error(f"❌ Errore nella costruzione del contesto istruzioni: {str(e)}")
            return "Errore nella costruzione del contesto istruzioni. Contattare il supporto."
    
    def build_full_context(self, force=False, ttl_hours=24):
        """
        Costruisce o carica il contesto completo KV-cache.
        
        Args:
            force: Se True, forza la rigenerazione anche se è già valido
            ttl_hours: Durata di validità del contesto in ore
            
        Returns:
            str: Il contesto completo
        """
        try:
            # Verifica se il contesto esistente è valido (a meno che non sia forzata la rigenerazione)
            if not force and self.is_context_valid(ttl_hours):
                log.info(f"🔄 Caricamento contesto esistente da {self.context_path}")
                with open(self.context_path, "r", encoding="utf-8") as f:
                    context = f.read()
                return context
            
            # Calcola hash documenti
            documents_hash = self.calculate_documents_hash()
            
            # Prepara l'intestazione metadata
            timestamp = datetime.now().isoformat(timespec='seconds')
            metadata_header = f"""
<!-- KV-CACHE METADATA
timestamp: {timestamp}
documents_hash: {documents_hash}
version: 1.0
-->

"""
            
            # Costruisci le sezioni del contesto
            document_context = self.build_document_context()
            instruction_context = self.build_instruction_context()
            
            # Unisci tutto in un unico contesto
            full_context = f"{metadata_header}{document_context}\n\n{instruction_context}"
            
            # Assicurati che la directory del contesto esista
            os.makedirs(os.path.dirname(self.context_path), exist_ok=True)
            
            # Salva il contesto nel file
            with open(self.context_path, "w", encoding="utf-8") as f:
                f.write(full_context)
            
            # Log con stima token
            context_length = len(full_context)
            estimated_tokens = context_length // 4  # Stima approssimativa ~4 caratteri per token
            log.info(f"✅ Contesto KV-cache salvato in {self.context_path}: {context_length} caratteri / ~{estimated_tokens} token stimati")
            
            return full_context
            
        except Exception as e:
            log.error(f"❌ Errore nella costruzione del contesto completo: {str(e)}")
            return "Errore nella generazione del contesto KV-cache. Contattare il supporto."