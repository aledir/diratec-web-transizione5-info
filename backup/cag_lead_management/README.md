# CAG Lead Management

Plugin per Cheshire Cat AI che implementa un sistema di gestione dei lead per la Transizione 5.0 basato su Context Augmented Generation (CAG), sfruttando la KV-cache fornita dal plugin `cag_document_manager`.

## Funzionalità principali

- Estrazione automatica di informazioni dai messaggi dell'utente
- Gestione semplificata del flusso conversazionale
- Sistema di scoring per qualificazione dei lead
- Controlli di sicurezza avanzati
- Gestione della persistenza dei dati su database PostgreSQL
- API REST per l'integrazione con sistemi esterni

## Vantaggi dell'approccio CAG

A differenza del plugin `rag_lead_management` basato sul sistema RAG, questo plugin:

1. **Non manipola il prompt in modo dinamico**: Sfrutta la KV-cache precaricata da `cag_document_manager`
2. **Riduce l'overhead di processamento**: Elimina la necessità di ricerca vettoriale ad ogni interazione
3. **Semplifica gli hook**: Implementa solo le funzionalità essenziali per la gestione dei lead
4. **Migliora le prestazioni**: Riduce la latenza e il carico sul server

## Prerequisiti

- Plugin `cag_document_manager` installato e configurato
- Database PostgreSQL configurato con le tabelle necessarie

## Installazione

1. Copiare i file del plugin nella directory `plugins/cag_lead_management`
2. Configurare le variabili d'ambiente per il database:
   ```bash
   export POSTGRES_HOST="localhost"
   export POSTGRES_PORT="5432"
   export POSTGRES_DB="diratec_leads"
   export POSTGRES_USER="diratec_user"
   export POSTGRES_PASSWORD="securepassword"
   ```
3. Attivare il plugin dall'interfaccia amministrativa

## API Endpoints

Il plugin espone i seguenti endpoint API:

- `GET /api/cag/leads`: Ottiene l'elenco dei lead
- `GET /api/cag/lead/{lead_id}`: Ottiene i dettagli di un lead specifico
- `POST /api/cag/lead/update/{lead_id}`: Aggiorna lo stato di un lead
- `GET /api/cag/conversation/{session_id}/status`: Verifica lo stato di completamento della conversazione

## Configurazione

Dalla pagina di configurazione del plugin è possibile impostare:

- Parametri di connessione al database
- Controlli di sicurezza e filtri contenuti
- Timeout e limitazioni per le sessioni

## Integrazione con cag_document_manager

Il plugin `cag_lead_management` è progettato per lavorare in tandem con `cag_document_manager`:

1. `cag_document_manager` fornisce la KV-cache con tutte le istruzioni comportamentali e i documenti
2. `cag_lead_management` si occupa dell'estrazione e gestione dei lead

## Funzionamento

1. **Preprocessing messaggi**: Il plugin estrae automaticamente informazioni rilevanti (azienda, contatti, investimenti)
2. **Gestione delle sessioni**: Ogni conversazione è tracciata con un ID di sessione unico
3. **Salvataggio dati lead**: I dati estratti vengono salvati progressivamente nel database
4. **Analytics**: Eventi significativi vengono registrati per analisi successive
5. **Sicurezza**: Implementa controlli per messaggi fuori tema, contenuti offensivi e rate limiting

## Strumenti disponibili

Il plugin espone i seguenti strumenti per l'AI:

- `save_lead_data`: Salva manualmente i dati del lead
- `create_lead`: Crea un nuovo lead nel database dai dati raccolti

## Autore

DIRATEC SRL - https://www.diratec.com

## Licenza

Copyright © 2024 DIRATEC SRL. Tutti i diritti riservati.