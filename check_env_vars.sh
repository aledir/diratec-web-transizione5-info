#!/bin/bash

# Percorso del file .env da analizzare
ENV_FILE=".env.dev"  # Cambia con il tuo file .env specifico
SEARCH_DIR="."  # Directory radice del progetto

# Estrai nomi variabili, escludendo commenti e righe vuote
VARIABLES=$(grep -v '^#' "$ENV_FILE" | grep -v '^$' | sed -E 's/([^=]+)=.*/\1/')

echo "===== ANALISI UTILIZZO VARIABILI D'AMBIENTE ====="
echo "Cercando in: $SEARCH_DIR"
echo "File .env analizzato: $ENV_FILE"
echo ""

# Conta le variabili totali
TOTAL_VARS=$(echo "$VARIABLES" | wc -l)
echo "Totale variabili trovate in $ENV_FILE: $TOTAL_VARS"
echo ""

# Per ogni variabile, cerca dove viene utilizzata
for VAR in $VARIABLES; do
  echo "===== $VAR ====="
  
  # Cerca sia process.env.VAR, ${VAR} (per docker-compose) e VAR= (per Dockerfile)
  USAGE=$(find "$SEARCH_DIR" -type f -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/\.git/*" -not -path "*/backup/*" -exec grep -l "process\.env\.$VAR\|\${$VAR}\|$VAR=" {} \; | sort)
  
  if [ -z "$USAGE" ]; then
    echo "⚠️ Non utilizzata in alcun file"
  else
    USAGE_COUNT=$(echo "$USAGE" | wc -l)
    echo "✅ Utilizzata in $USAGE_COUNT file:"
    echo "$USAGE" | sed 's/^/  - /'
  fi
  
  echo ""
done

echo "===== FINE ANALISI ====="
