# CAG Document Manager

Plugin per Cheshire Cat AI che implementa un sistema di Context Augmented Generation (CAG) per la gestione dei documenti Transizione 5.0, fornendo un contesto completo e precaricato (KV-cache) al LLM.

## Funzionalità principali

- Caricamento e organizzazione dei documenti Transizione 5.0
- Generazione di una KV-cache contenente tutti i documenti pertinenti
- Conversione di PDF in Markdown tramite API Mathpix
- Pulizia automatica dei documenti convertiti
- Invio automatico della KV-cache a ogni richiesta dell'LLM

## Concetto di CAG vs RAG

A differenza del RAG (Retrieval Augmented Generation) che seleziona dinamicamente i documenti rilevanti, CAG (Context Augmented Generation) carica tutti i documenti pertinenti in un'unica KV-cache, offrendo diversi vantaggi:

- **Conoscenza completa**: L'assistente ha accesso a tutti i documenti simultaneamente
- **Prioritizzazione controllata**: I documenti vengono presentati in ordine di priorità
- **Comportamento coerente**: Istruzioni comportamentali chiare per guidare l'assistente
- **Ottimizzazione per LLM con contesti ampi**: Sfrutta modelli come Claude e Gemini che supportano contesti molto ampi

## Configurazione del plugin

Dopo l'installazione, configurare le seguenti impostazioni:

- `documents_dir`: Directory contenente i documenti (default: `/app/cat/shared/documents`)
- `context_dir`: Directory per il file di contesto (default: `/app/cat/shared/documents/context`)
- `context_file`: Nome del file contesto (default: `cag_context.md`)
- `max_context_tokens`: Dimensione massima del contesto in token (default: `180000`)

### Configurazione max_context_tokens

Il parametro `max_context_tokens` determina il limite massimo di token per la KV-cache. Questo valore è puramente una soglia di monitoraggio e non influisce sui costi o sulle prestazioni del modello, che dipendono solo dai token effettivamente utilizzati.

#### Valori consigliati per modello (maggio 2025)

Con l'evoluzione rapida dei modelli LLM, questi valori cambiano frequentemente:

| Modello LLM | Finestra contestuale (maggio 2025) |
|-------------|--------------------------|
| Claude 3.7 Sonnet | ~200,000 token |
| Claude 3 Opus | ~200,000 token |
| GPT-4o | ~128,000 token |
| Gemini 2.5 Pro | ~1,000,000 token |
| Llama 3 (70B) | ~128,000 token |
| Llama 4 Scout | ~10,000,000 token |

#### Aspetti importanti da considerare

1. **Il valore non influisce sui costi**: I costi dipendono solo dai token effettivamente utilizzati, non dal valore di `max_context_tokens`

2. **Nessun impatto sulle prestazioni**: Le prestazioni del modello non cambiano in base a questa impostazione

3. **Funzione principale**: Serve principalmente a monitorare se stai avvicinandoti al limite reale del modello utilizzato

4. **Impostazione ottimale**: 
   - Impostalo vicino al limite reale del modello che stai utilizzando (90-95%)
   - Per modelli con finestre molto ampie (es. Gemini 1.5 Pro), puoi impostarlo vicino al limite reale senza compromessi
   - Per modelli con finestre più limitate, un valore più conservativo può aiutare a evitare troncamenti

#### Esempio pratico

Se utilizzi 130,000 token di contesto:
- Con Gemini 1.5 Pro (limite 1M) e `max_context_tokens: 900,000`: utilizzo al 14%, nessun problema
- Con Claude (limite 180k) e `max_context_tokens: 180,000`: utilizzo al 72%, ancora sicuro
- Con GPT-4 (limite 128k) e `max_context_tokens: 128,000`: utilizzo al 102%, rischio di troncamento

### Configurazione Mathpix

Per la conversione PDF → Markdown, il plugin utilizza le credenziali Mathpix dalle variabili d'ambiente:

```bash
# Aggiungere al file .env
MATHPIX_APP_ID=your-app-id
MATHPIX_APP_KEY=your-app-key
```

## Autenticazione

Per utilizzare gli endpoint API, è necessario ottenere un token di autenticazione:

```bash
export ACCESS_TOKEN=$(curl -s -X POST "https://api.transizione5.info/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | grep -o '"access_token":"[^"]*"' | cut -d':' -f2 | tr -d '"')
```

## Flusso di lavoro standard

### 1. Convertire i documenti PDF in Markdown

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/cag/documents/convert-all" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

Questo endpoint converte automaticamente tutti i documenti PDF in formato Markdown, utilizzando l'API Mathpix.

### 2. Pulizia dei documenti Markdown

```bash
docker exec -it cheshire_cat_core python3 /app/cat/plugins/cag_document_manager/clean_markers.py
```

Questo script interattivo aiuta a:
- Selezionare i documenti da pulire
- Visualizzare il contenuto all'inizio e alla fine del documento
- Scegliere le righe da cui iniziare e terminare il testo utile
- Rimuovere il contenuto non pertinente o duplicato
- Salvare automaticamente le opzioni di pulizia nel file metadata.json

### 3. Generare la KV-cache

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/cag/regenerate-context" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

Questo endpoint forza la rigenerazione della KV-cache, combinando tutti i documenti Markdown e applicando le opzioni di pulizia definite nel passaggio precedente.

### 4. Verificare il numero di token

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/cag/check-tokens" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

Questo endpoint verifica che il numero di token nella KV-cache non superi il limite configurato, garantendo la compatibilità con il modello LLM.

## Autore

DIRATEC SRL - https://www.diratec.com

## Licenza

Copyright © 2024 DIRATEC SRL. Tutti i diritti riservati.