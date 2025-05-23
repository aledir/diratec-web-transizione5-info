# Document Manager Plugin

Plugin per Cheshire Cat AI che gestisce i documenti Transizione 5.0, implementando le funzionalità essenziali per il sistema RAG (Retrieval-Augmented Generation) e la conversione da PDF a Markdown tramite Mathpix.

## Funzionalità principali

- Gestione dei documenti tramite metadati
- Aggiunta di documenti individuali al RAG
- Aggiornamento del RAG con tutti i documenti attivi
- Supporto per metadati personalizzati dei documenti
- Eliminazione efficiente dei documenti dal RAG
- **Conversione PDF in Markdown tramite API Mathpix**
- **Conversione batch di documenti**

## Struttura dei file

```
/shared/documents/               # Directory base
├── metadata.json                # File centrale contenente i metadati
├── .uuid_map.json               # Mappatura tra ID documento e UUID nel sistema RAG
├── circolari/                   # Circolari emanate dal MIMIT
├── faq/                         # Domande frequenti con risposte ufficiali
├── guide/                       # Guide e istruzioni operative
├── markdown/                    # File markdown convertiti da PDF
├── modelli/                     # Moduli, allegati e modelli scaricabili
└── normativa/                   # Leggi, decreti e altra normativa ufficiale
```

### Formato metadata.json

```json
{
  "files": [
    {
      "id": "documento-1",
      "path": "normativa/documento.pdf",
      "titolo": "Titolo del documento",
      "categoria": "NORMATIVA SERVIZI",
      "tipo": "NORMATIVA",
      "data": "2024-05-07",
      "stato": "attivo",
      "descrizione": "Descrizione del documento",
      "tags": ["tag1", "tag2"],
      "markdown_path": "markdown/documento.md" // Campo aggiunto dopo la conversione
    }
  ],
  "categorie": [
    "NORMATIVA SERVIZI",
    "GUIDE",
    "MODULI E MODELLI",
    "PILLOLE INFORMATIVE"
  ],
  "tipi": [
    "NORMATIVA",
    "CIRCOLARE",
    "FAQ",
    "GUIDA",
    "MODELLO"
  ]
}
```

## Moduli principali

### document_operations.py
Contiene funzioni per la gestione dei metadati:

- `read_metadata()`: Legge i metadati da metadata.json
- `get_document_by_id(doc_id)`: Ottiene un documento dal suo ID
- `get_active_documents()`: Restituisce tutti i documenti attivi
- `set_document_status(doc_id, status)`: Imposta lo stato di un documento
- `save_uuid_mapping(doc_id, uuid)`: Salva la mappatura tra ID e UUID
- `get_uuid_mapping(doc_id)`: Ottiene l'UUID associato a un documento
- `delete_uuid_mapping(doc_id)`: Rimuove la mappatura per un documento
- `update_document_markdown_path(doc_id, markdown_path)`: Aggiorna il percorso markdown nei metadati
- `convert_document_to_markdown(doc_id, force_conversion=False)`: Converte un documento in markdown
- `convert_all_active_documents(force=False)`: Converte tutti i documenti attivi
- `get_documents_with_markdown()`: Restituisce i documenti che hanno un file markdown associato

### pdf_converter.py
Implementa la conversione da PDF a Markdown tramite API Mathpix:

- `MathpixConverter`: Classe che gestisce la conversione tramite API Mathpix
  - `convert_pdf(pdf_path, output_dir)`: Converte un singolo PDF in Markdown

### rag_operations.py
Contiene funzioni per interagire con il sistema RAG:

- `get_cat_instance()`: Ottiene un'istanza di CheshireCat in modo sicuro
- `generate_deterministic_uuid(doc_id)`: Genera un UUID deterministico per i documenti
- `add_document_to_rag(doc_id)`: Aggiunge un singolo documento al RAG
- `update_all_documents()`: Aggiorna tutti i documenti attivi nel RAG
- `delete_document_from_memory(doc_id, uuid=None)`: Rimuove un documento dalla memoria RAG utilizzando filtri di metadati

### endpoints.py
Definisce gli endpoint REST per l'interazione con il plugin:

- `GET /api/documents/add-to-rag/{doc_id}`: Aggiunge un documento specifico al RAG
- `GET /api/documents/update-rag`: Aggiorna tutti i documenti attivi nel RAG
- `GET /api/documents/remove-from-rag/{doc_id}`: Rimuove un documento dal RAG
- `GET /api/documents/convert/{doc_id}`: Converte un documento in markdown tramite Mathpix
- `GET /api/documents/convert-all`: Converte tutti i documenti attivi in markdown

## Autenticazione

Per utilizzare gli endpoint API, è necessario ottenere un token di autenticazione.

#### Genera il token di autenticazione

```bash
export ACCESS_TOKEN=$(curl -s -X POST "https://api.transizione5.info/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | grep -o '"access_token":"[^"]*"' | cut -d':' -f2 | tr -d '"')
```

#### Mostra il TOKEN

```bash
echo $ACCESS_TOKEN
```

### Gestione RAG

#### Aggiorna tutti i documenti nel RAG

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/rag/documents/update-rag" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

#### Aggiungi specifico documento al RAG

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/rag/documents/add-to-rag/documento-id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

#### Rimuovi un documento dal RAG

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/rag/documents/remove-from-rag/documento-id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

### Conversione PDF in Markdown

#### Converti un documento PDF in Markdown

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/rag/documents/convert/documento-id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

#### Converti tutti i documenti attivi in Markdown

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/rag/documents/convert-all" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

## Configurazione Mathpix

Per utilizzare la conversione PDF → Markdown, è necessario configurare le credenziali Mathpix:

1. Registrarsi su [Mathpix](https://accounts.mathpix.com/) per ottenere API credentials
2. Impostare le variabili d'ambiente:
   ```bash
   export MATHPIX_APP_ID="your-app-id"
   export MATHPIX_APP_KEY="your-app-key"
   ```
   o configurare le impostazioni nel file di configurazione dell'applicazione.

## Flusso di lavoro

### Aggiunta di un documento al RAG

1. Verificare che il documento esista nei metadati
2. Verificare che il documento sia marcato come "attivo"
3. Verificare che il file esista fisicamente
4. Rimuovere eventuali versioni precedenti dal RAG
5. **Convertire il PDF in Markdown se necessario**
6. Calcolare i parametri di chunking in base al tipo e dimensione del file
7. Generare un UUID deterministico per il documento
8. Aggiungere il documento al RAG con i metadati personalizzati
9. Salvare la mappatura tra ID documento e UUID RAG

### Aggiornamento completo del RAG

1. Ottenere la lista di tutti i documenti attivi
2. Per ogni documento attivo:
   - **Convertire il PDF in Markdown se necessario**
   - Aggiungere il documento al RAG (se non già presente)
   - Aggiornare il documento nel RAG (se già presente ma modificato)
3. Alla fine, restituire un riepilogo dell'operazione

### Conversione di un documento in Markdown

1. Verificare che il documento esista nei metadati
2. Verificare che il file PDF esista fisicamente
3. Verificare se il documento è già stato convertito
4. Inviare il file PDF a Mathpix per la conversione
5. Monitorare lo stato della conversione
6. Scaricare il file Markdown risultante
7. Aggiornare i metadati con il percorso del file Markdown

### Conversione batch di tutti i documenti

1. Ottenere la lista di tutti i documenti attivi
2. Per ogni documento attivo:
   - Verificare se è già stato convertito
   - Convertire il documento in Markdown tramite Mathpix
   - Aggiornare i metadati
3. Alla fine, restituire un riepilogo dell'operazione

### Rimozione di un documento dal RAG

1. Verificare che il documento esista nei metadati
2. Recuperare l'UUID associato al documento
3. Eliminare il documento dalla memoria vettoriale usando filtri di metadati
4. Marcare il documento come "obsoleto" nei metadati
5. Rimuovere la mappatura UUID

## Debugging

Per monitorare l'attività del plugin, controllare i log di Cheshire Cat:

```bash
# Visualizza tutti i log
docker logs -f cheshire_cat_core

# Filtra i log per vedere solo le operazioni del plugin
docker logs cheshire_cat_core | grep -E "Documento|RAG|metadata|Mathpix"
```

## Ottimizzazioni implementate

- **Generazione UUID deterministici**: Gli UUID vengono generati in modo deterministico basandosi sull'ID del documento
- **Eliminazione efficiente**: I documenti vengono rimossi tramite filtri di metadati anziché metodi diretti
- **Gestione sicura WebSocket**: Implementazione robusta per evitare errori WebSocket durante le operazioni batch
- **Chunking adattivo**: Parametri di chunking ottimizzati in base al tipo e alla dimensione del file
- **Conversione cache-aware**: Evita di riconvertire documenti già elaborati
- **Elaborazione batch asincrona**: Gestisce grandi volumi di documenti in modo efficiente

## Note implementative

Il plugin utilizza la libreria standard `pathlib` per la gestione dei percorsi, garantendo compatibilità cross-platform.

I documenti sono identificati da un ID univoco nel file metadata.json, e ogni documento ha un UUID nel sistema RAG, memorizzato nel file .uuid_map.json.

La conversione PDF → Markdown utilizza l'API Mathpix, che offre un'eccellente capacità di riconoscimento di formule matematiche, tabelle e layout complessi.