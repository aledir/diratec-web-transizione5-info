#!/bin/bash
# Script unificato per avviare l'ambiente di Transizione5.info
# Supporta ambienti di sviluppo e produzione

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verifica del parametro di ambiente
if [ "$1" != "dev" ] && [ "$1" != "prod" ]; then
  echo -e "${RED}Errore: specificare l'ambiente (dev o prod)${NC}"
  echo -e "Uso: ./start.sh dev|prod"
  exit 1
fi

ENV="$1"

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}  Avvio ambiente di ${ENV^^} per Transizione5.info  ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Copia il file .env.dev/.env.prod in .env
echo -e "${BLUE}Copiando il file di configurazione di ${ENV}...${NC}"
cp .env.${ENV} .env

# Ottieni l'IP Tailscale e aggiungilo all'ambiente
echo -e "${BLUE}Rilevamento indirizzo IP Tailscale...${NC}"
TAILSCALE_IP=$(tailscale ip -4)
if [ -z "$TAILSCALE_IP" ]; then
  echo -e "${YELLOW}ATTENZIONE: Impossibile rilevare l'IP Tailscale. Verrà usato quello configurato nel file .env.${NC}"
else
  echo -e "${GREEN}IP Tailscale rilevato: ${TAILSCALE_IP}${NC}"
  # Aggiorna il file .env con l'IP Tailscale rilevato
  sed -i "s/^TAILSCALE_IP=.*/TAILSCALE_IP=${TAILSCALE_IP}/" .env
fi

# Avvia i container con docker-compose
echo -e "${BLUE}Avvio dei container in modalità ${ENV}...${NC}"
docker compose down
sleep 2
# docker compose up -d
docker compose up

# Verifica lo stato dei container
echo -e "${BLUE}Verifica dello stato dei container...${NC}"
sleep 5
docker compose ps

echo -e "${GREEN}Ambiente di ${ENV^^} avviato con successo!${NC}"
echo -e "${YELLOW}Frontend disponibile su: https://www.transizione5.info${NC}"
echo -e "${YELLOW}API disponibile su: https://api.transizione5.info${NC}"

# Mostra informazioni di accesso a dashboard e admin
echo -e "${BLUE}========== ACCESSI AMMINISTRATIVI (VIA TAILSCALE) ==========${NC}"
echo -e "${YELLOW}Admin UI Cheshire Cat: http://${TAILSCALE_IP}:1865/admin${NC}"
echo -e "${YELLOW}Admin UI alternativa: http://diratec-dev:1865/admin${NC}"
echo -e "${YELLOW}Dashboard Traefik: http://${TAILSCALE_IP}:8080/dashboard/${NC}"
echo -e "${YELLOW}Dashboard alternativa: http://diratec-dev:8080/dashboard/${NC}"
echo -e "${BLUE}====================================================${NC}"