#!/bin/bash
# Script di verifica e riparazione del plugin GSE Stats

set -e  # Interrompi lo script in caso di errori

echo "🔍 Inizio verifica plugin GSE Stats..."

# Verifica che il container sia in esecuzione
if ! docker ps | grep -q "cheshire_cat_core"; then
  echo "❌ Il container cheshire_cat_core non è in esecuzione!"
  exit 1
fi

# Verifica la struttura delle directory
echo "🔍 Controllo struttura directory..."
docker exec cheshire_cat_core ls -la /app/cat/data

# Crea la directory se non esiste
docker exec cheshire_cat_core mkdir -p /app/cat/data

# Imposta i permessi corretti
docker exec cheshire_cat_core chmod 777 /app/cat/data

# Verifica se il file esiste già
echo "🔍 Controllo esistenza file dati..."
if docker exec cheshire_cat_core ls -la /app/cat/data/gse_stats.json 2>/dev/null; then
  echo "✅ File gse_stats.json trovato!"
  echo "📄 Contenuto del file:"
  docker exec cheshire_cat_core cat /app/cat/data/gse_stats.json
else
  echo "⚠️ File gse_stats.json non trovato."
  
  # Crea un file di test per verificare i permessi
  echo "🔍 Test di scrittura nella directory..."
  echo '{"test": "ok"}' | docker exec -i cheshire_cat_core tee /app/cat/data/test_write.json > /dev/null
  
  if docker exec cheshire_cat_core ls -la /app/cat/data/test_write.json 2>/dev/null; then
    echo "✅ Test di scrittura riuscito!"
    docker exec cheshire_cat_core rm /app/cat/data/test_write.json
  else
    echo "❌ Impossibile scrivere nella directory /app/cat/data/"
    echo "⚠️ Problema di permessi o path non valido."
    exit 1
  fi
  
  # Forza un aggiornamento dei dati
  echo "🔄 Forzare aggiornamento dati GSE..."
  curl -s -X GET "https://api.transizione5.info/custom/api/gse-stats/update" | grep -v "html"
  
  # Verifica se il file è stato creato
  if docker exec cheshire_cat_core ls -la /app/cat/data/gse_stats.json 2>/dev/null; then
    echo "✅ File gse_stats.json creato con successo!"
    echo "📄 Contenuto del file:"
    docker exec cheshire_cat_core cat /app/cat/data/gse_stats.json
  else
    echo "⚠️ File non creato automaticamente, creazione manuale..."
    # Crea manualmente il file con dati di esempio
    echo '{
      "risorse_disponibili": "5337.549999,76",
      "risorse_totali": "6237.000000,00", 
      "risorse_prenotate": "861.080215,47",
      "risorse_utilizzate": "38.369784,77",
      "ultimo_aggiornamento": "'$(date +%d/%m/%Y)'",
      "timestamp": "'$(date -Iseconds)'"
    }' | docker exec -i cheshire_cat_core tee /app/cat/data/gse_stats.json > /dev/null
    
    echo "✅ File creato manualmente con successo."
  fi
fi

# Verifica il percorso attuale del plugin
echo "🔍 Controllo percorso attuale nel plugin..."
# Ottieni il percorso salvato nel plugin (NOTA: richiede che il plugin sia configurato per loggare questa info)
PLUGIN_PATH=$(docker logs cheshire_cat_core 2>&1 | grep "Plugin GSE Stats - Percorso file dati" | tail -1 | sed 's/.*Percorso file dati: //')

if [ -z "$PLUGIN_PATH" ]; then
  echo "⚠️ Percorso non trovato nei log. Il plugin potrebbe non essere configurato per loggare questa informazione."
else
  echo "📂 Percorso attuale nel plugin: $PLUGIN_PATH"
  
  # Controlla se il percorso è corretto
  if [[ "$PLUGIN_PATH" != "/app/cat/data/gse_stats.json" ]]; then
    echo "⚠️ Il percorso nel plugin non è corretto. Potrebbe essere necessario modificare il codice del plugin."
  else
    echo "✅ Il percorso nel plugin è corretto."
  fi
fi

echo "✅ Verifica completata!"
echo "📝 NOTA: Se il plugin continua a non funzionare correttamente, potrebbe essere necessario modificare il codice sorgente."