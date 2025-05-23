# README.md - Documentazione per l'infrastruttura Transizione5.info

# Transizione5.info - Documentazione Infrastruttura

## Panoramica

Questo progetto implementa un sito web basato su AI conversazionale per raccogliere lead qualificati per certificazioni Transizione 5.0, offerte da DIRATEC SRL. L'infrastruttura è basata su:

- **Cheshire Cat AI**: Core della soluzione con plugin personalizzati
- **Next.js**: Frontend con integrazione WebSocket per streaming token per token
- **PostgreSQL**: Database per la persistenza dei lead
- **Docker & Docker Compose**: Orchestrazione dei servizi
- **Traefik**: Reverse proxy con supporto SSL automatico
- **Tailscale**: Accesso sicuro alle interfacce amministrative

## Struttura del Progetto

```
/transizione5-info/
├── docker-compose.yml          # Configurazione unificata e parametrizzata
├── .env                        # Variabili d'ambiente attuali (generate dallo script)
├── .env.example                # Template delle variabili con documentazione
├── .env.dev                    # Variabili per sviluppo
├── .env.prod                   # Variabili per produzione
├── start.sh                    # Script unificato per avvio dev/prod
├── backup-config.sh            # Script di backup configurazione
├── frontend/                   # Applicazione Next.js
├── cheshire-cat/               # Configurazione Cheshire Cat AI
│   ├── plugins/                # Plugin personalizzati
│   │   ├── rag_document_manager/  # Gestione documenti e PDF->MD via Mathpix
│   │   ├── rag_lead_management/   # Estrazione e gestione lead
│   ├── data/                   # Dati persistenti
│   └── static/                 # File statici
├── traefik/                    # Configurazione Traefik
│   └── acme/                   # Certificati SSL Let's Encrypt
├── postgres/                   # Configurazione PostgreSQL
│   └── init-scripts/           # Script di inizializzazione DB
└── shared/                     # Directory condivisa per documenti
    └── documents/              # Documenti strutturati
```

## Configurazione e Avvio

### Sistema di Avvio Unificato

Il progetto ora utilizza un unico script di avvio parametrizzato che supporta entrambi gli ambienti:

```bash
./start.sh dev     # Avvia in modalità sviluppo
./start.sh prod    # Avvia in modalità produzione
```

Lo script esegue automaticamente:
1. Backup della configurazione corrente
2. Applicazione delle variabili d'ambiente appropriate
3. Rilevamento automatico dell'IP Tailscale per accesso amministrativo
4. Avvio dei container con la configurazione corretta

### Parametrizzazione

Il file `docker-compose.yml` è ora completamente parametrizzato e funziona sia in ambiente di sviluppo che di produzione. Le differenze di comportamento sono controllate dalle variabili in `.env.dev` e `.env.prod`.

## Accesso agli Strumenti Amministrativi

Tutte le interfacce amministrative sono ora accessibili **esclusivamente via Tailscale** per massima sicurezza:

| Interfaccia | URL di Accesso |
|-------------|---------------|
| Admin Cheshire Cat | `http://diratec-dev:1865/admin/` |
| Dashboard Traefik | `http://diratec-dev:8080/dashboard/` |

L'IP Tailscale viene rilevato automaticamente dallo script di avvio e mostrato nei messaggi di avvio.

## Plugin Personalizzati

### 1. Plugin RAG Document Manager

Plugin per Cheshire Cat AI che gestisce la conversione di documenti:
- Conversione da PDF a Markdown tramite Mathpix API
- Indicizzazione automatica nella knowledge base
- Supporto per estrazione semantica dai documenti

### 2. Plugin RAG Lead Management

Plugin per gestione conversazionale dei lead:
- Estrazione automatica di informazioni dalla chat
- Salvataggio dati nel database PostgreSQL
- Arricchimento conversazioni con informazioni sui lead

## Sicurezza

L'infrastruttura implementa diverse misure di sicurezza:

- **Autenticazione API**: Tutti gli endpoint richiedono autenticazione
- **Sicurezza SSL**: Certificati SSL automatici con Let's Encrypt
- **Rate limiting**: Protezione contro abusi (configurabile per ambiente)
- **Header di sicurezza**: Configurazione ottimizzata Traefik
- **Admin UI inaccessibile pubblicamente**: Accesso solo tramite Tailscale
- **Dashboard Traefik protetta**: Autenticazione Basic e accesso solo via Tailscale

## Backup e Monitoraggio

### Backup Automatici

In ambiente di produzione, il sistema esegue automaticamente:
- Backup giornalieri del database PostgreSQL
- Conservazione configurabile dei backup (default: 7 giorni)

Per eseguire un backup manuale della configurazione:
```bash
./backup-config.sh
```

### Visualizzare i log

```bash
# Log di tutti i servizi
docker compose logs -f

# Log di un servizio specifico
docker compose logs -f cheshire-cat
docker compose logs -f traefik
docker compose logs -f frontend
```

## Risorse di Sistema

Il sistema ora gestisce in modo intelligente le risorse in base all'ambiente:

| Risorsa | Sviluppo | Produzione |
|---------|----------|------------|
| CPU Cheshire Cat | 2 | 1 |
| Memoria Cheshire Cat | 2G | 1G |
| CPU PostgreSQL | 1 | 0.5 |
| Memoria PostgreSQL | 1G | 512M |
| Ottimizzazione PostgreSQL | No | Sì |

## Migrazione e Manutenzione

### Migrazione a un nuovo server

Per migrare su un nuovo server:

1. Installare Docker e Docker Compose
2. Installare Tailscale e autenticare il nodo
3. Clonare il repository
4. Copiare i volumi persistenti (o inizializzare da zero)
5. Eseguire `./start.sh prod`

Lo script rileverà automaticamente il nuovo IP Tailscale e configurerà il sistema correttamente.

### API esterne utilizzate

Il sistema utilizza diversi servizi esterni:

- **Mathpix**: Conversione PDF a Markdown
- **OpenAI**: Estrazione dati strutturati dai lead e embedding
- **Anthropic**: Modello conversazionale principale (Claude)

Le chiavi API sono configurate nei file `.env.dev` e `.env.prod`.

## Riferimenti

- Documentazione Cheshire Cat AI: https://cheshire-cat-ai.github.io/docs/
- Documentazione Traefik: https://doc.traefik.io/traefik/
- Documentazione Next.js: https://nextjs.org/docs
- Documentazione Tailscale: https://tailscale.com/kb/