# RAG Lead Management Plugin

Plugin per Cheshire Cat AI che implementa un sistema completo di gestione dei lead per la Transizione 5.0, integrando funzionalità conversazionali, sicurezza avanzata e analisi per la qualificazione dei potenziali clienti.

## Funzionalità principali

- Gestione completa del flusso conversazionale in 4 fasi
- Raccolta progressiva e naturale dei dati del lead
- Estrazione automatica di informazioni dal testo dell'utente
- Sistema di scoring per qualificazione dei lead
- Prioritizzazione dei documenti in base a data e tipo
- Controlli di sicurezza avanzati
- Verifica e correzione delle risposte per garantire un approccio commerciale positivo
- Persistenza dei dati su database PostgreSQL
- API REST per l'integrazione con sistemi esterni

## Struttura del database

Il plugin utilizza PostgreSQL per memorizzare i seguenti dati:

```
leads:                 # Tabella dei lead qualificati
conversazioni:         # Tabella delle conversazioni con utenti
analytics:             # Tabella per eventi di analytics
audit_log:             # Tabella per audit di sicurezza
```

## Moduli principali

### form_operations.py
Contiene funzioni per gestire il form conversazionale:

- `extract_information(text)`: Estrae informazioni rilevanti dal testo
- `process_user_message(session_id, user_message)`: Elabora i messaggi utente
- `save_lead_data()`: Salva i dati del lead nel sistema
- `create_lead_from_conversation(session_id)`: Crea un lead dalla conversazione
- `evaluate_conversation_completion(session_id)`: Valuta quanto è completa la conversazione
- `get_conversation_phase(session_id)`: Determina la fase attuale della conversazione

### conversation_instructions.py
Gestisce le istruzioni per guidare il comportamento del modello:

- `get_phase_prompt(session_id)`: Genera il prompt specifico per ogni fase
- `get_next_question(session_id)`: Suggerisce la prossima domanda da porre

### database_operations.py
Gestisce tutte le operazioni sul database:

- `connect_db()`: Crea una connessione al database
- `verify_tables_exist()`: Verifica che le tabelle necessarie esistano
- `create_lead()`: Crea un nuovo lead
- `update_lead()`: Aggiorna un lead esistente
- `create_conversation()`: Crea o aggiorna una conversazione
- `get_conversation()`: Recupera una conversazione attiva
- `log_analytics_event()`: Registra un evento analytics
- `get_leads_from_db()`: Recupera l'elenco dei lead
- `get_lead_details_from_db()`: Recupera i dettagli di un lead
- `update_lead_status_in_db()`: Aggiorna lo stato di un lead
- `finalize_lead_from_conversation()`: Finalizza la creazione di un lead dalla conversazione

### scoring_operations.py
Implementa il sistema di scoring per i lead:

- `calculate_lead_score(azienda_data, investimenti_data)`: Calcola lo score del lead
- `get_lead_status(score)`: Determina lo stato del lead in base allo score

### fact_checking.py
Verifica e ottimizza le risposte dell'AI:

- `verify_response(content, declarative_memories, cat)`: Verifica che la risposta sia basata sui fatti disponibili e mantenga un approccio commerciale positivo

### document_priority.py
Gestisce la priorità dei documenti nel RAG:

- `prioritize_documents(memories)`: Ordina le memorie per priorità
- `format_memory_context(memories)`: Formatta le memorie come contesto

### analytics_operations.py
Gestisce la raccolta di dati analytics:

- `log_analytics_event()`: Registra eventi analytics nel database

### safety_checks.py
Implementa controlli di sicurezza per i messaggi:

- `is_off_topic(text)`: Verifica se un messaggio è fuori tema
- `generate_stay_on_topic_response()`: Genera una risposta per reindirizzare l'utente
- `filter_offensive_content(text)`: Filtra contenuti offensivi

### security/
Moduli per la gestione avanzata della sicurezza:

- `security_core.py`: Funzionalità di sicurezza di base
- `security_rate.py`: Rate limiting e protezione DoS
- `security_audit.py`: Audit trail e logging di sicurezza
- `security_scan.py`: Scansione dipendenze per vulnerabilità
- `security_session.py`: Gestione sicura delle sessioni
- `security_config.py`: Configurazione parametri di sicurezza

### hooks.py
Implementa gli hook di Cheshire Cat:

- `after_cat_bootstrap()`: Avvia task in background dopo l'avvio
- `agent_prompt_prefix()`: Aggiunge istruzioni personalizzate al prompt
- `before_chat_completion()`: Processa il messaggio utente prima della generazione
- `after_chat_completion()`: Processa la risposta dell'AI dopo la generazione

### tools.py
Definisce gli strumenti a disposizione del modello:

- `save_lead_data()`: Tool per salvare i dati del lead
- `create_lead()`: Tool per creare un nuovo lead

### endpoints.py
Definisce gli endpoint REST per l'interazione con il plugin:

- `GET /api/leads`: Ottiene l'elenco dei lead
- `GET /api/lead/{lead_id}`: Ottiene i dettagli di un lead specifico
- `POST /api/lead/update/{lead_id}`: Aggiorna lo stato di un lead

## Flusso conversazionale a 4 fasi

### 1. Fase di accoglienza
- Saluto cordiale dell'utente
- Presentazione come assistente specializzato in Transizione 5.0
- Domanda aperta "In cosa posso aiutarti?"
- Risposta alle domande specifiche usando il RAG
- Nessuna richiesta di dati personali o aziendali

### 2. Fase di approfondimento
- Continua a fornire informazioni di valore sulla Transizione 5.0
- Inizia a porre domande naturali per comprendere meglio la situazione dell'utente
- Raccolta passiva di informazioni durante la conversazione
- Personalizzazione delle risposte in base ai dati già raccolti

### 3. Fase di qualificazione
- Domande più dirette e mirate per raccogliere i dati mancanti
- Introduzione della possibilità di supporto personalizzato
- Richiesta di dati aziendali e di investimento
- Rassicurazione sulla privacy dei dati

### 4. Fase di formalizzazione
- Riepilogo delle informazioni raccolte
- Completamento della raccolta degli ultimi dati mancanti
- Conferma della correttezza dei dati
- Spiegazione dei passaggi successivi
- Ringraziamento per le informazioni fornite

## Sistema di scoring

Il plugin implementa un sistema di scoring sofisticato per la qualificazione dei lead:

### Dimensione dell'azienda
- Grande impresa: 20 punti
- Media impresa: 15 punti
- Piccola impresa: 10 punti

### Budget di investimento
- > 1M€: 30 punti
- > 500K€: 20 punti
- > 100K€: 10 punti

### Tempistiche
- Entro un mese/immediato: 25 punti
- Entro tre mesi/trimestre: 15 punti
- Altra tempistica: 5 punti

### Classificazione finale
- ≥ 70 punti: "qualificato"
- ≥ 40 punti: "interessante"
- < 40 punti: "da approfondire"

## Gestione priorità documenti

Il plugin implementa un sistema di prioritizzazione dei documenti nel RAG, basato su:

### Tipo di documento
- FAQ: Massima priorità (100 punti)
- Documenti post-2025: Alta priorità (50 punti)
- Circolari: 40 punti
- Normativa: 30 punti
- Guide: 20 punti
- Modelli: 10 punti

### Data documento
- I documenti più recenti hanno precedenza sui più vecchi

## Funzionalità di sicurezza

Il plugin implementa diverse funzionalità di sicurezza:

- **Sanitizzazione input**: Pulizia degli input per prevenire iniezioni
- **Rate limiting**: Limitazione delle richieste per prevenire abusi
- **Protezione DoS**: Difesa contro attacchi Denial of Service
- **Protezione brute force**: Blocco dopo troppi tentativi falliti
- **Validazione email**: Verifica della validità degli indirizzi email
- **Audit trail**: Registrazione completa delle modifiche ai lead
- **Rilevamento argomenti fuori tema**: Mantenimento focus su Transizione 5.0
- **Filtraggio contenuti offensivi**: Protezione contro linguaggio inappropriato
- **Verifiche dipendenze**: Controllo vulnerabilità nelle dipendenze
- **Gestione sessioni sicura**: Timeout, rotazione token e invalidazione

## Configurazione del database

Per utilizzare il plugin, è necessario configurare un database PostgreSQL:

1. Impostare le variabili d'ambiente:
   ```bash
   export POSTGRES_HOST="localhost"
   export POSTGRES_PORT="5432"
   export POSTGRES_DB="diratec_leads"
   export POSTGRES_USER="diratec_user"
   export POSTGRES_PASSWORD="securepassword"
   ```
   oppure configurare le impostazioni nel file `settings.py` del plugin.

2. Creare le tabelle necessarie nel database:
   ```sql
   CREATE TABLE leads (
     id SERIAL PRIMARY KEY,
     azienda_data JSONB,
     investimenti_data JSONB,
     contatto_data JSONB,
     fonte VARCHAR(100),
     data_creazione TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
     score INTEGER,
     stato VARCHAR(50),
     assegnato_a VARCHAR(100),
     note TEXT
   );

   CREATE TABLE conversazioni (
     id SERIAL PRIMARY KEY,
     session_id VARCHAR(100) UNIQUE,
     data JSONB,
     lead_id INTEGER REFERENCES leads(id),
     inizio_conversazione TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
     fine_conversazione TIMESTAMP WITH TIME ZONE,
     completato_form BOOLEAN DEFAULT FALSE
   );

   CREATE TABLE analytics (
     id SERIAL PRIMARY KEY,
     evento VARCHAR(100),
     session_id VARCHAR(100),
     lead_id INTEGER,
     dati JSONB,
     timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );

   CREATE TABLE audit_log (
     id SERIAL PRIMARY KEY,
     lead_id INTEGER REFERENCES leads(id),
     user_id VARCHAR(100) NOT NULL,
     action VARCHAR(50) NOT NULL,
     old_data JSONB,
     new_data JSONB,
     timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );
   ```

## Utilizzo degli endpoint API

### Ottenere l'elenco dei lead

```bash
curl -X GET "https://api.transizione5.info/api/leads" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Ottenere i dettagli di un lead specifico

```bash
curl -X GET "https://api.transizione5.info/api/lead/123" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Aggiornare lo stato di un lead

```bash
curl -X POST "https://api.transizione5.info/api/lead/update/123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"stato": "qualificato"}'
```

## Debugging

Per monitorare l'attività del plugin, controllare i log di Cheshire Cat:

```bash
# Visualizza tutti i log
docker logs -f cheshire_cat_core

# Filtra i log per vedere solo le operazioni del plugin
docker logs cheshire_cat_core | grep -E "Lead|Fase|Session|Analytics"
```

## Esempi di risposta conversazionale

### Esempio di risposta in fase di accoglienza

```
Salve! Sono l'assistente specializzato in Transizione 5.0, il programma di agevolazioni fiscali per investimenti in digitalizzazione e sostenibilità.

In cosa posso aiutarti riguardo alla Transizione 5.0? Posso fornirti informazioni sui requisiti, le procedure per accedere ai crediti d'imposta, la documentazione necessaria o qualsiasi altro aspetto di questo programma.
```

### Esempio di risposta in fase di qualificazione

```
Grazie per le informazioni che mi hai fornito finora. Per poterti dare indicazioni più precise sul tuo caso specifico, mi servirebbero alcuni dettagli aggiuntivi.

Potresti dirmi qual è il budget approssimativo che state considerando per questo investimento in automazione? Questo mi aiuterebbe a valutare meglio le potenziali aliquote del credito d'imposta applicabili al vostro caso.
```

## Note implementative

Il plugin utilizza espressioni regolari per estrarre informazioni dal testo dell'utente in modo non invasivo, senza richiedere esplicitamente la compilazione di un form.

La verifica delle risposte garantisce che le informazioni fornite siano accurate e mantengano sempre un approccio commerciale positivo, evitando risposte negative o scoraggianti anche in casi limite.

Il sistema di sicurezza implementa pratiche moderne come la difesa in profondità, limitando i rischi di attacchi comuni e proteggendo i dati sensibili degli utenti.

Il plugin gestisce automaticamente l'evoluzione della conversazione attraverso le diverse fasi, adattando le domande e le risposte in base al contesto e alle informazioni già raccolte.