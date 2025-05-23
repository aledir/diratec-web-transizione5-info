# RAG Document Manager Plugin

## Flusso di lavoro

Il plugin gestisce i documenti Transizione 5.0 attraverso il seguente flusso di lavoro:

### 1. Autenticazione

```bash
export ACCESS_TOKEN=$(curl -s -X POST "https://api.transizione5.info/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | grep -o '"access_token":"[^"]*"' | cut -d':' -f2 | tr -d '"')

echo $ACCESS_TOKEN
```

### 2. Conversione dei documenti PDF in Markdown

**Converti tutti i documenti attivi con `converti_cag=True`:**

```bash
curl -s -X GET "https://api.transizione5.info/custom/rag/documents/convert-cag" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

**Oppure converti un documento specifico:**

```bash
curl -s -X GET "https://api.transizione5.info/custom/rag/documents/convert/documento-id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

### 3. Pulizia manuale dei file Markdown

**Esegui lo script interattivo di pulizia:**

```bash
docker exec -it cheshire_cat_core python3 /app/cat/plugins/rag_document_manager/clean_markers.py
```

Questo mostrerà un'interfaccia interattiva per selezionare i punti di taglio nei file markdown. Lo script aggiorna il file `shared/documents/metadata.json` aggiungendo:

```json
"clean_options": {
  "taglia_caratteri_inizio": 3058, 
  "taglia_caratteri_fine": 5422
}
```

Questi valori determinano quali parti del documento saranno rimosse durante l'inserimento nel RAG.

### 4. Inserimento nel RAG

**Inserisci un singolo documento:**

```bash
curl -s -X GET "https://api.transizione5.info/custom/rag/documents/insert-markdown/documento-id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

**Inserisci tutti i documenti markdown:**

```bash
curl -s -X GET "https://api.transizione5.info/custom/rag/documents/insert-all-markdown" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

### 5. Rimozione di un documento dal RAG

**Rimuovi un documento specifico:**

```bash
curl -s -X GET "https://api.transizione5.info/custom/rag/documents/remove-from-rag/documento-id" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

## Funzionalità principali

- Gestione dei documenti tramite metadati
- Conversione PDF in Markdown tramite API Mathpix
- Conversione selettiva dei documenti marcati con `converti_cag=True`
- Pulizia manuale dei file Markdown
- Inserimento dei documenti Markdown nel RAG con parametri di chunking personalizzati
- Rimozione efficiente dei documenti dal RAG

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
      "converti_cag": true,
      "descrizione": "Descrizione del documento",
      "tags": ["tag1", "tag2"],
      "chunk_size": 1000,
      "chunk_overlap": 200,
      "markdown_path": "markdown/documento.md",
      "clean_options": {
        "taglia_caratteri_inizio": 3058,
        "taglia_caratteri_fine": 5422
      }
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

## Guida alla compilazione del metadata.json

Ogni documento nel sistema RAG è definito tramite un oggetto JSON con i seguenti campi:

| Campo | Tipo | Descrizione | Obbligatorio |
|-------|------|-------------|--------------|
| `id` | string | Identificatore univoco del documento, usato in tutte le operazioni API. Consigliato: formato slug (solo lettere minuscole, numeri e trattini) | **Sì** |
| `path` | string | Percorso relativo al file fisico all'interno della directory `/shared/documents/` | **Sì** |
| `titolo` | string | Titolo descrittivo del documento, mostrato nell'interfaccia utente | **Sì** |
| `categoria` | string | Categoria del documento, deve essere presente nell'array `categorie` | **Sì** |
| `tipo` | string | Tipo di documento, deve essere presente nell'array `tipi` | **Sì** |
| `data` | string | Data del documento in formato YYYY-MM-DD | **Sì** |
| `stato` | string | Stato del documento: `attivo` o `obsoleto`. Solo i documenti attivi vengono inseriti nel RAG | **Sì** |
| `converti_cag` | boolean | Indica se il documento deve essere convertito in markdown tramite l'API Mathpix | **Sì** |
| `descrizione` | string | Descrizione estesa del documento | **Sì** |
| `tags` | array | Array di stringhe che descrivono il contenuto, usato per la ricerca | **Sì** |
| `chunk_size` | number | Dimensione in caratteri dei chunk per il RAG. Default: 1000 | No |
| `chunk_overlap` | number | Sovrapposizione in caratteri tra chunk consecutivi. Default: 200 | No |
| `priorita_rag` | number | Priorità del documento nel sistema RAG (1-5, dove 1 è massima priorità). Influenza i risultati di ricerca | No |
| `visibile_frontend` | boolean | Indica se il documento deve essere visibile nell'interfaccia frontend | No |
| `markdown_path` | string | Percorso al file markdown convertito (generato automaticamente) | No |
| `clean_options` | object | Opzioni per la pulizia del markdown (generato automaticamente) | No |

### Note specifiche sui campi

#### priorita_rag

La priorità RAG influenza il ranking dei risultati di ricerca nel sistema. È un valore da 1 a 5, dove:

- **1**: Massima priorità. Documenti ufficiali più recenti, FAQ aggiornate
- **2**: Alta priorità. Documenti ufficiali recenti ma secondari
- **3**: Media priorità. Documenti di base o riferimento necessari ma non recenti
- **4**: Bassa priorità. Documenti informativi di contesto
- **5**: Minima priorità. Documenti storici o di archivio

Esempio di assegnazione delle priorità:
- FAQ MIMIT aggiornate: priorità 1
- Circolari operative MIMIT recenti: priorità 1-2
- Decreti attuativi recenti: priorità 2
- Documenti normativi precedenti ma rilevanti: priorità 3
- Documentazione tecnica di supporto: priorità 4
- Documenti storici o superati: priorità 5

#### stato

Lo stato determina se un documento deve essere incluso nel RAG:
- `attivo`: il documento è valido e viene inserito nel RAG
- `obsoleto`: il documento non è più valido ma viene mantenuto per riferimento storico e non inserito nel RAG

Se un documento precedentemente attivo viene segnato come obsoleto, verrà automaticamente rimosso dal RAG al successivo riavvio del sistema.

#### chunk_size e chunk_overlap

Questi parametri controllano come il documento viene suddiviso in frammenti (chunk) per l'inserimento nel database vettoriale:

- `chunk_size`: dimensione massima in caratteri di ogni chunk
- `chunk_overlap`: numero di caratteri che si sovrappongono tra chunk consecutivi

Valori consigliati:
- Documenti tecnici densi: chunk_size 800-1000, overlap 200-250
- Documenti normativi: chunk_size 1000-1200, overlap 250-300
- FAQ e contenuti strutturati: chunk_size 1200-1500, overlap 300-350

#### clean_options

Questo campo viene generato automaticamente dallo script `clean_markers.py` e contiene:

- `taglia_caratteri_inizio`: numero di caratteri da rimuovere all'inizio del file markdown
- `taglia_caratteri_fine`: numero di caratteri da rimuovere alla fine del file markdown

Queste opzioni permettono di rimuovere contenuti non rilevanti come copertine, indici, appendici o contenuti amministrativi.

## Configurazione Mathpix

Per utilizzare la conversione PDF → Markdown, è necessario configurare le credenziali Mathpix nel file `.env`:

```
# Configurazione Mathpix
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key
```

## Moduli principali

### document_operations.py
Contiene funzioni per la gestione dei metadati:

- `read_metadata()`: Legge i metadati da metadata.json
- `get_document_by_id(doc_id)`: Ottiene un documento dal suo ID
- `get_active_documents()`: Restituisce tutti i documenti attivi, opzionalmente con filtri aggiuntivi
- `set_document_status(doc_id, status)`: Imposta lo stato di un documento
- `save_uuid_mapping(doc_id, uuid)`: Salva la mappatura tra ID e UUID
- `get_uuid_mapping(doc_id)`: Ottiene l'UUID associato a un documento
- `delete_uuid_mapping(doc_id)`: Rimuove la mappatura per un documento
- `update_document_markdown_path(doc_id, markdown_path)`: Aggiorna il percorso markdown nei metadati

### pdf_converter.py
Implementa la conversione da PDF a Markdown tramite API Mathpix:

- `MathpixConverter`: Classe che gestisce la conversione tramite API Mathpix
  - `convert_pdf(pdf_path, output_dir)`: Converte un singolo PDF in Markdown

### rag_utils.py
Contiene funzioni per interagire con il sistema RAG:

- `generate_deterministic_uuid(doc_id)`: Genera un UUID deterministico per i documenti
- `delete_document_from_memory(doc_id, cat, uuid=None)`: Rimuove un documento dalla memoria RAG
- `insert_markdown_into_rag(doc_id, cat)`: Inserisce un singolo documento markdown nel RAG
- `insert_all_markdown_into_rag(cat)`: Inserisce tutti i documenti markdown nel RAG

### clean_markers.py
Strumento interattivo per la pulizia manuale dei file Markdown:

- `find_and_apply_positions(doc_id)`: Aiuta a trovare le posizioni di taglio e applica le opzioni di pulizia
- `get_markdown_documents()`: Restituisce i documenti attivi con file markdown esistenti o con `converti_cag=true`
- `interactive_mode()`: Esegue lo script in modalità interattiva

### endpoints.py
Definisce gli endpoint REST per l'interazione con il plugin:

- `GET /rag/documents/remove-from-rag/{doc_id}`: Rimuove un documento dal RAG
- `GET /rag/documents/convert/{doc_id}`: Converte un documento in markdown tramite Mathpix
- `GET /rag/documents/convert-cag`: Converte tutti i documenti attivi con `converti_cag=True` in markdown
- `GET /rag/documents/insert-markdown/{doc_id}`: Inserisce un singolo documento markdown nel RAG
- `GET /rag/documents/insert-all-markdown`: Inserisce tutti i documenti markdown nel RAG

## Strumenti di diagnostica e monitoraggio

Il plugin include endpoint di diagnostica che aiutano a monitorare lo stato del sistema RAG e analizzare il processo di chunking dei documenti:

### Analisi del processo di chunking

```bash
curl -s -X GET "https://api.transizione5.info/custom/rag/documents/analyze-chunking/{doc_id}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

Questo endpoint fornisce un'analisi dettagliata del processo di chunking per un documento specifico, inclusi:
- Statistiche sul contenuto (dimensione, numero di righe)
- Effetto delle opzioni di pulizia
- Stima del numero di chunks previsti
- Numero di chunks effettivamente generati
- Chunks presenti nel sistema RAG

### Stato complessivo del sistema

```bash
curl -s -X GET "https://api.transizione5.info/custom/rag/documents/system-status" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

Questo endpoint fornisce informazioni complete sullo stato del sistema RAG:
- Coerenza tra metadati, file system e memoria vettoriale
- Statistiche sulla memoria vettoriale
- Statistiche sui file presenti nel sistema
- Mappature UUID mancanti o inconsistenti

Questi strumenti sono particolarmente utili per diagnosticare eventuali problemi con il sistema RAG o per verificare lo stato dell'integrazione dei documenti.

## Debugging

Per monitorare l'attività del plugin, controllare i log di Cheshire Cat:

```bash
# Visualizza tutti i log
docker logs -f cheshire_cat_core

# Filtra i log per vedere solo le operazioni del plugin
docker logs cheshire_cat_core | grep -E "Documento|RAG|metadata|Mathpix"
```