#!/bin/bash

# Definisci le vecchie variabili che vogliamo verificare non esistano più
OLD_VARIABLES=(
  "CHESHIRE_CAT_INTERNAL_URL"
  "CHESHIRE_CAT_API_KEY"
  "NEXT_PUBLIC_CHESHIRE_CAT_URL"
  "NEXT_PUBLIC_WEBSOCKET_URL"
  "DEV_CPU_LIMIT"
  "DEV_MEMORY_LIMIT"
)

echo "===== VERIFICA VARIABILI RINOMINATE O RIMOSSE ====="
echo "Cercando in tutto il progetto..."
echo ""

# Contatore per variabili trovate
found_count=0

# Per ogni variabile, cerca in tutto il progetto
for var in "${OLD_VARIABLES[@]}"; do
  echo "===== Cercando: $var ====="
  
  # Cerca la variabile in tutti i file, escludendo directory non rilevanti
  FOUND_FILES=$(find . -type f -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/\.git/*" -not -path "*/backup/*" -exec grep -l "$var" {} \; | sort)
  
  if [ -z "$FOUND_FILES" ]; then
    echo "✅ Non trovata in alcun file"
  else
    found_count=$((found_count + 1))
    FILE_COUNT=$(echo "$FOUND_FILES" | wc -l)
    echo "❌ Trovata in $FILE_COUNT file:"
    echo "$FOUND_FILES" | sed 's/^/  - /'
  fi
  
  echo ""
done

echo "===== RIEPILOGO ====="
if [ $found_count -eq 0 ]; then
  echo "🎉 Ottimo! Nessuna delle vecchie variabili è presente nel progetto."
else
  echo "⚠️ Attenzione: $found_count vecchie variabili sono ancora presenti nel progetto."
  echo "Controlla i file sopra indicati e aggiornali con i nuovi nomi standardizzati."
fi
echo "===== FINE VERIFICA ====="
