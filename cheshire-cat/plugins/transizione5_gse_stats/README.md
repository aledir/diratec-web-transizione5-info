# Transizione 5.0 GSE Stats Plugin

Plugin per Cheshire Cat AI che recupera e gestisce le statistiche sul portale GSE relative alla Transizione 5.0, fornendo dati aggiornati sulle risorse disponibili e utilizzate.

## Funzionalità principali

- Recupero automatico dei dati statistici dal portale GSE
- Aggiornamento periodico configurabile (default: ogni 3 ore)
- Persistenza dei dati su file JSON
- Esposizione delle statistiche tramite API REST
- Supporto per aggiornamento manuale dei dati

## Struttura dei file

```
/plugins/transizione5_gse_stats/
├── __init__.py               # Inizializzazione del plugin e definizione costanti globali
├── endpoints.py              # Definizione degli endpoint REST
├── gse_stats_operations.py   # Operazioni di parsing e gestione dati
├── plugin.json               # Metadati del plugin
├── requirements.txt          # Dipendenze Python
├── settings.json             # Impostazioni predefinite
├── settings.py               # Schema impostazioni
├── test-gse-stat.sh          # Script per verificare e risolvere problemi
└── transizione5_gse_stats.py # Classe principale del plugin
```

### Dati memorizzati

Il plugin salva i dati in un file JSON con la seguente struttura:

```json
{
  "risorse_disponibili": "5.373.382.666,84",
  "risorse_totali": "6.237.000.000,00",
  "risorse_prenotate": "831.965.098,52",
  "risorse_utilizzate": "31.652.234,64",
  "ultimo_aggiornamento": "09/05/2025",
  "timestamp": "2025-05-09T15:08:42.497440"
}
```

### Posizione del file dati

Il plugin salva i dati nel seguente percorso:
- **All'interno del container**: `/app/cat/data/gse_stats.json`
- **Sul file system host**: `./cheshire-cat/data/gse_stats.json` (in base alla configurazione dei volumi Docker)

## Moduli principali

### __init__.py
Contiene l'inizializzazione del plugin e la definizione del percorso del file dati, utilizzato da tutti gli altri moduli.

### transizione5_gse_stats.py
Contiene la classe principale `Transizione5StatsPlugin` che:
- Inizializza le impostazioni e i dati
- Configura il task di aggiornamento periodico in background
- Gestisce il caricamento/salvataggio dei dati su file

### gse_stats_operations.py
Contiene le funzioni per la gestione dei dati statistici:
- `initialize(plugin_instance)`: Inizializza le variabili globali con i dati del plugin
- `get_gse_stats_data()`: Restituisce i dati delle statistiche GSE memorizzati
- `update_gse_stats_data()`: Forza l'aggiornamento manuale dei dati GSE dal portale (versione asincrona)
- `update_gse_stats_sync()`: Forza l'aggiornamento manuale dei dati GSE dal portale (versione sincrona)

### endpoints.py
Definisce gli endpoint REST per l'interazione con il plugin:
- `GET /api/gse-stats`: Restituisce i dati statistici GSE più recenti
- `GET /api/gse-stats/update`: Forza un aggiornamento manuale dei dati

### test-gse-stat.sh
Script di verifica e riparazione del plugin che:
- Controlla la struttura delle directory
- Verifica l'esistenza del file dati
- Imposta i permessi corretti
- Crea un file di test se necessario
- Forza un aggiornamento dei dati GSE

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

### Utilizzo degli endpoint

#### Ottieni statistiche GSE aggiornate

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/gse-stats" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

#### Forza un aggiornamento manuale

```bash
curl -s -X GET "https://api.transizione5.info/custom/api/gse-stats/update" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq
```

## Flusso di lavoro

### Inizializzazione del plugin

1. Caricamento delle impostazioni (URL GSE, intervallo di aggiornamento)
2. Lettura dei dati esistenti dal file di persistenza (se presente)
3. Inizializzazione delle operazioni di gestione dati
4. Avvio del task di aggiornamento periodico in background

### Aggiornamento automatico dei dati

1. Connessione al portale GSE tramite HTTP
2. Parsing del contenuto HTML con BeautifulSoup
3. Estrazione dei valori delle risorse tramite espressioni regolari
4. Aggiornamento dei dati in memoria
5. Salvataggio dei dati su file per persistenza

### Fornitura delle statistiche via API

1. Ricezione della richiesta HTTP all'endpoint `/api/gse-stats`
2. Verifica della disponibilità dei dati
3. Formattazione e restituzione dei dati in formato JSON

## Debugging

Per monitorare l'attività del plugin, controllare i log di Cheshire Cat:

```bash
# Visualizza tutti i log
docker logs -f cheshire_cat_core

# Filtra i log per vedere solo le operazioni del plugin GSE Stats
docker logs cheshire_cat_core | grep -E "GSE|stats|risorse"
```

### Risoluzione dei problemi

Se il plugin non funziona correttamente, è possibile utilizzare lo script `test-gse-stat.sh`:

```bash
# Imposta i permessi di esecuzione
chmod +x test-gse-stat.sh

# Esegui lo script
./test-gse-stat.sh
```

Questo script verificherà lo stato del plugin e tenterà di risolvere i problemi più comuni.

## Configurazione

Il plugin supporta le seguenti impostazioni configurabili:

- **gse_url**: URL del portale GSE per il recupero dei dati (default: "https://www.gse.it/servizi-per-te/attuazione-misure-pnrr/transizione-5-0")
- **update_interval**: Intervallo di tempo in ore tra un aggiornamento e l'altro (default: 3.0)

Le impostazioni possono essere modificate tramite l'interfaccia di amministrazione di Cheshire Cat.

## Integrazione con Frontend

Il plugin è progettato per integrarsi con un componente React `GSEStatsWidget` che visualizza i dati nel frontend. Il componente può ottenere i dati chiamando l'endpoint `/custom/api/gse-stats` e visualizzare:

- Risorse disponibili
- Risorse totali
- Risorse prenotate
- Risorse utilizzate
- Data ultimo aggiornamento

## Note implementative

Il plugin utilizza BeautifulSoup4 per il parsing dell'HTML e espressioni regolari per estrarre i valori numerici. La struttura è stata ottimizzata per essere robusta a cambiamenti nella struttura del portale GSE.

I dati vengono estratti in tempo reale dal portale GSE, garantendo statistiche sempre aggiornate sulla disponibilità dei fondi per la Transizione 5.0.

### Contatori GSE

Il plugin utilizza un URL specifico per il recupero dei dati dei contatori:
- **URL contatore**: "https://gseorg1.my.salesforce-sites.com/transizione5contatori"

Questo URL punta direttamente alla pagina che contiene i contatori aggiornati, migliorando l'affidabilità del recupero dati rispetto all'estrazione dalla pagina principale del GSE.