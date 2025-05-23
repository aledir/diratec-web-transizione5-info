#!/bin/bash

# Configurazione
API_BASE="https://api.transizione5.info"

# Carica credenziali da .env
if [ -f ".env" ]; then
    # Carica le variabili dal file .env
    export $(grep -v '^#' .env | xargs)
    # Usa le credenziali dal file .env
    USERNAME="admin"
    PASSWORD="$ADMIN_PASSWORD"
    
    if [ -z "$PASSWORD" ]; then
        echo -e "\033[0;31mPassword non trovata nel file .env. Assicurati che ADMIN_PASSWORD sia definita nel file .env nella root del progetto.\033[0m"
        exit 1
    fi
else
    echo -e "\033[0;31mFile .env non trovato. Impossibile caricare le credenziali.\033[0m"
    exit 1
fi

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Funzione per creare separatori visuali
separator() {
    echo -e "\n${YELLOW}==============================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}==============================================${NC}"
}

# Ottieni ACCESS_TOKEN dinamicamente
get_access_token() {
    local token_response=$(curl -s -X POST "$API_BASE/auth/token" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

    # Estrai il token senza echo aggiuntivi
    local access_token=$(echo "$token_response" | grep -o '"access_token":"[^"]*"' | cut -d':' -f2 | tr -d '"')

    if [[ -z "$access_token" ]]; then
        return 1
    fi

    echo "$access_token"
    return 0
}

# Ottieni il token
separator "AUTENTICAZIONE"
echo -e "${BLUE}Ottenimento token di accesso...${NC}"
ACCESS_TOKEN=$(get_access_token)

# Verifica che il token sia stato ottenuto
if [[ -z "$ACCESS_TOKEN" ]]; then
    echo -e "${RED}❌ Errore nell'ottenimento del token di accesso${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Token di accesso ottenuto con successo${NC}"
fi

# Verifica validità del token
echo -e "${BLUE}Verifica validità del token...${NC}"
echo -e "${CYAN}Tentativo di chiamata all'API: $API_BASE/custom/api/rag/diagnostic${NC}"

# Prima verifichiamo che l'host sia raggiungibile
host_check=$(curl -s -I "$API_BASE" | head -n 1)
echo -e "${CYAN}Test connettività base: ${host_check}${NC}"

# Poi facciamo il controllo completo
token_response=$(curl -s -v "$API_BASE/custom/api/rag/diagnostic" \
    -H "Authorization: Bearer $ACCESS_TOKEN" 2>&1)

# Estrai il codice di stato da curl verbose output
http_code=$(echo "$token_response" | grep -o "< HTTP/[0-9.]* [0-9]*" | grep -o "[0-9][0-9][0-9]" | tail -n 1)

echo -e "${CYAN}Risposta dell'API: $token_response${NC}"
echo -e "${CYAN}Codice HTTP: $http_code${NC}"

if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
    echo -e "${GREEN}✅ Token valido${NC}"
else
    echo -e "${RED}❌ Token non valido (HTTP $http_code)${NC}"
    echo -e "${RED}Risposta dettagliata:${NC}"
    echo "$token_response"
    echo -e "${RED}Test interrotto: token non valido${NC}"
    exit 1
fi

# Funzione per verificare successo o fallimento
check_success() {
    local condition=$1
    local success_message=$2
    local failure_message=$3

    if $condition; then
        echo -e "${GREEN}✅ $success_message${NC}"
        return 0
    else
        echo -e "${RED}❌ $failure_message${NC}"
        return 1
    fi
}

# Funzione per verificare che un valore sia presente in una risposta JSON
check_json_contains() {
    local json=$1
    local field=$2
    local expected_value=$3

    local actual_value=$(echo "$json" | jq -r "$field")
    if [[ "$actual_value" == "$expected_value" ]]; then
        echo -e "${GREEN}✅ Campo $field contiene il valore atteso: $expected_value${NC}"
        return 0
    else
        echo -e "${RED}❌ Campo $field non contiene il valore atteso${NC}"
        echo -e "${RED}   Atteso: $expected_value${NC}"
        echo -e "${RED}   Trovato: $actual_value${NC}"
        return 1
    fi
}

# Funzione per recuperare log pertinenti
get_relevant_logs() {
    echo -e "\n${BLUE}RECUPERO LOG PERTINENTI${NC}"
    docker logs cheshire_cat_core --tail 100 | grep -E 'Hook|hook|🔍|working_memory|conversation_id|session_id|messaggi|Aggiunt|working_memory|❌|⚠️|✅' | tail -50
}

# Funzione per verifica di RAM (Retrieval-Augmented Memory)
test_ram_functionality() {
    local session_id=$1
    local query=$2

    separator "TEST FUNZIONALITÀ RAG: $query"

    echo -e "${CYAN}Invio query RAG: $query${NC}"

    # Invia messaggio che richiede conoscenza dai documenti
    response=$(curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"$query\",
        \"conversation_id\": \"$session_id\"
      }")

    # Estrai risposta
    response_text=$(echo "$response" | jq -r '.text')
    echo -e "${CYAN}Risposta AI:${NC}"
    echo -e "$response_text" | head -n 10

    # Attesa per elaborazione
    echo -e "\n${CYAN}Attesa elaborazione...${NC}"
    sleep 2

    # Verifica log per controllo RAM
    echo -e "\n${BLUE}VERIFICA LOG PER CONFERMA RAG${NC}"
    docker logs cheshire_cat_core --tail 100 | grep -E 'Memoria dichiarativa|memories|document|prioritizzazione|declarative_memories' | tail -10

    # Verifica conversazione
    echo -e "\n${BLUE}VERIFICA CONVERSAZIONE PER CONFERMA SALVATAGGIO RISPOSTA${NC}"
    conv_response=$(curl -s -X GET "$API_BASE/custom/api/rag/debug/get-conversation/$session_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    msgs_count=$(echo "$conv_response" | jq '.conversation.data.messaggi | length')
    echo -e "${GREEN}Numero messaggi nella conversazione: $msgs_count${NC}"

    # Mostra ultimo messaggio (risposta AI)
    last_msg=$(echo "$conv_response" | jq -r '.conversation.data.messaggi[-1].content' 2>/dev/null)
    if [[ -n "$last_msg" ]]; then
        echo -e "${GREEN}Ultimo messaggio (AI):${NC}"
        echo -e "$last_msg" | head -n 3
        return 0
    else
        echo -e "${RED}❌ Nessuna risposta AI salvata nella conversazione${NC}"
        return 1
    fi
}

# Funzione per testare persistenza delle sessioni
test_session_persistence() {
    local session_id=$1
    local message1=$2
    local message2=$3
    local description=$4

    separator "TEST PERSISTENZA SESSIONI: $description"

    # 1. Invia primo messaggio
    echo -e "${CYAN}Invio primo messaggio: $message1${NC}"
    response1=$(curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"$message1\",
        \"conversation_id\": \"$session_id\"
      }")

    # Estrai risposta
    response_text1=$(echo "$response1" | jq -r '.text')
    echo -e "${CYAN}Risposta AI al primo messaggio:${NC}"
    echo -e "${response_text1}" | head -n 3

    # Attesa simula interruzione sessione
    echo -e "\n${CYAN}Attesa di 5 secondi che simula interruzione sessione...${NC}"
    sleep 5

    # 2. Invia secondo messaggio nella stessa sessione
    echo -e "${CYAN}Invio secondo messaggio: $message2${NC}"
    response2=$(curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"$message2\",
        \"conversation_id\": \"$session_id\"
      }")

    # Estrai risposta
    response_text2=$(echo "$response2" | jq -r '.text')
    echo -e "${CYAN}Risposta AI al secondo messaggio:${NC}"
    echo -e "${response_text2}" | head -n 3

    # Verifica che entrambi i messaggi siano nella stessa conversazione
    echo -e "\n${BLUE}VERIFICA CONVERSAZIONE PER CONFERMA PERSISTENZA${NC}"
    conv_response=$(curl -s -X GET "$API_BASE/custom/api/rag/debug/get-conversation/$session_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    msgs_count=$(echo "$conv_response" | jq '.conversation.data.messaggi | length')

    if [[ $msgs_count -ge 4 ]]; then
        echo -e "${GREEN}✅ Persistenza confermata: $msgs_count messaggi nella conversazione${NC}"

        # Mostra tutti i messaggi
        echo -e "\n${BLUE}MESSAGGI NELLA CONVERSAZIONE:${NC}"
        echo "$conv_response" | jq '.conversation.data.messaggi[] | {role, content: (.content | if length > 50 then .[:50] + "..." else . end)}'
        return 0
    else
        echo -e "${RED}❌ Persistenza fallita: trovati solo $msgs_count messaggi invece di almeno 4${NC}"
        return 1
    fi
}

# Funzione per testare estrazione informazioni
test_information_extraction() {
    local session_id=$1
    local message=$2

    separator "TEST ESTRAZIONE INFORMAZIONI"

    echo -e "${CYAN}Invio messaggio con informazioni: $message${NC}"

    # Prima testiamo l'endpoint diretto di estrazione
    echo -e "\n${BLUE}TEST ENDPOINT DIRETTO DI ESTRAZIONE${NC}"
    extraction_response=$(curl -s -X POST "$API_BASE/custom/api/rag/test-extraction" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"$message\",
        \"process_message\": true,
        \"session_id\": \"$session_id\"
      }")

    echo -e "${CYAN}Risultato estrazione diretta:${NC}"
    echo "$extraction_response" | jq '.extracted_info'

    # Ora inviamo il messaggio tramite chat per vedere se l'estrazione avviene
    echo -e "\n${BLUE}TEST ESTRAZIONE DURANTE CHAT NORMALE${NC}"
    chat_response=$(curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"$message\",
        \"conversation_id\": \"$session_id\"
      }")

    # Estrai risposta
    response_text=$(echo "$chat_response" | jq -r '.text')
    echo -e "${CYAN}Risposta AI:${NC}"
    echo -e "$response_text" 

    # Attesa per elaborazione
    echo -e "\n${CYAN}Attesa elaborazione ed estrazione informazioni...${NC}"
    sleep 3

    # Verifica conversazione per lead_data
    echo -e "\n${BLUE}VERIFICA LEAD_DATA NELLA CONVERSAZIONE${NC}"
    conv_response=$(curl -s -X GET "$API_BASE/custom/api/rag/debug/get-conversation/$session_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    # Estrai lead_data
    lead_data=$(echo "$conv_response" | jq '.conversation.data.lead_data')
    echo -e "${CYAN}Lead data estratto:${NC}"
    echo "$lead_data" | jq '.'

    # Verifica se ci sono informazioni estratte
    if [[ $(echo "$lead_data" | jq -r 'if . == {} or . == null then "empty" else "has_data" end') == "has_data" ]]; then
        echo -e "${GREEN}✅ Estrazione informazioni riuscita${NC}"
        return 0
    else
        echo -e "${RED}❌ Nessuna informazione estratta${NC}"
        return 1
    fi
}

# Funzione per testare endpoint di conversazione
test_conversation_endpoints() {
    local test_id="test-endpoint-$(date +%s)"

    separator "TEST ENDPOINT CONVERSAZIONE: $test_id"

    # Test creazione conversazione
    echo -e "${BLUE}TEST CREAZIONE CONVERSAZIONE${NC}"
    create_response=$(curl -s -X GET "$API_BASE/custom/api/rag/debug/create-conversation/$test_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    echo "$create_response" | jq '.'

    # Verifica creazione
    if [[ $(echo "$create_response" | jq -r '.success') == "true" ]]; then
        echo -e "${GREEN}✅ Creazione conversazione riuscita${NC}"
    else
        echo -e "${RED}❌ Creazione conversazione fallita${NC}"
        return 1
    fi

    # Test aggiunta messaggio
    echo -e "\n${BLUE}TEST AGGIUNTA MESSAGGIO${NC}"
    add_message_response=$(curl -s -X POST "$API_BASE/custom/api/rag/debug/add-message-to-conversation" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -d "{
            \"session_id\": \"$test_id\",
            \"user_message\": \"Questo è un messaggio di test\",
            \"ai_message\": \"Questa è una risposta di test\"
        }")

    echo "$add_message_response" | jq '.success'

    # Verifica aggiunta
    if [[ $(echo "$add_message_response" | jq -r '.success') == "true" ]]; then
        echo -e "${GREEN}✅ Aggiunta messaggi riuscita${NC}"
    else
        echo -e "${RED}❌ Aggiunta messaggi fallita${NC}"
        return 1
    fi

    # Test recupero conversazione
    echo -e "\n${BLUE}TEST RECUPERO CONVERSAZIONE${NC}"
    get_response=$(curl -s -X GET "$API_BASE/custom/api/rag/debug/get-conversation/$test_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    echo "$get_response" | jq '.found'

    # Verifica recupero
    if [[ $(echo "$get_response" | jq -r '.found') == "true" ]]; then
        echo -e "${GREEN}✅ Recupero conversazione riuscito${NC}"

        # Verifica che i messaggi siano presenti
        msgs_count=$(echo "$get_response" | jq '.conversation.data.messaggi | length')
        echo -e "${GREEN}Numero messaggi: $msgs_count${NC}"

        if [[ $msgs_count -eq 2 ]]; then
            echo -e "${GREEN}✅ Numero corretto di messaggi${NC}"
            return 0
        else
            echo -e "${RED}❌ Numero errato di messaggi: $msgs_count invece di 2${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Recupero conversazione fallito${NC}"
        return 1
    fi
}

# Funzione per testare simulare più utenti contemporanei
test_multiple_users() {
    local user1_id="user1-$(date +%s)"
    local user2_id="user2-$(date +%s)"

    separator "TEST UTENTI MULTIPLI SIMULTANEI"

    # Crea conversazioni per entrambi gli utenti
    echo -e "${BLUE}CREAZIONE CONVERSAZIONI PER DUE UTENTI${NC}"
    curl -s -X GET "$API_BASE/custom/api/rag/debug/create-conversation/$user1_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null
    curl -s -X GET "$API_BASE/custom/api/rag/debug/create-conversation/$user2_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

    # Utente 1 invia messaggio
    echo -e "\n${CYAN}UTENTE 1 ($user1_id) INVIA MESSAGGIO${NC}"
    curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"Sono l'utente 1 e voglio sapere cosa è la Transizione 5.0\",
        \"conversation_id\": \"$user1_id\"
      }" > /dev/null

    # Quasi simultaneamente, utente 2 invia messaggio
    echo -e "${CYAN}UTENTE 2 ($user2_id) INVIA MESSAGGIO${NC}"
    curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"Ciao, sono l'utente 2. Quali sono i requisiti per la Transizione 5.0?\",
        \"conversation_id\": \"$user2_id\"
      }" > /dev/null

    # Attesa per elaborazione
    echo -e "\n${CYAN}Attesa elaborazione di entrambe le richieste...${NC}"
    sleep 10

    # Verifica separazione delle conversazioni
    echo -e "\n${BLUE}VERIFICA SEPARAZIONE DELLE CONVERSAZIONI${NC}"

    # Recupera conversazione utente 1
    user1_conv=$(curl -s -X GET "$API_BASE/custom/api/rag/debug/get-conversation/$user1_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    # Recupera conversazione utente 2
    user2_conv=$(curl -s -X GET "$API_BASE/custom/api/rag/debug/get-conversation/$user2_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    # Conta messaggi utente 1
    user1_msgs=$(echo "$user1_conv" | jq '.conversation.data.messaggi | length')
    echo -e "${CYAN}Utente 1: $user1_msgs messaggi${NC}"

    # Conta messaggi utente 2
    user2_msgs=$(echo "$user2_conv" | jq '.conversation.data.messaggi | length')
    echo -e "${CYAN}Utente 2: $user2_msgs messaggi${NC}"

    # Verifica il contenuto per assicurarsi che non ci sia confusione tra le sessioni
    user1_content=$(echo "$user1_conv" | jq -r '.conversation.data.messaggi[0].content' 2>/dev/null)
    user2_content=$(echo "$user2_conv" | jq -r '.conversation.data.messaggi[0].content' 2>/dev/null)

    echo -e "\n${CYAN}Contenuto primo messaggio utente 1: ${NC}\"${user1_content}\""
    echo -e "${CYAN}Contenuto primo messaggio utente 2: ${NC}\"${user2_content}\""

    # Verifica che i contenuti siano diversi
    if [[ "$user1_content" != "$user2_content" ]]; then
        echo -e "${GREEN}✅ Le conversazioni sono correttamente separate${NC}"
        return 0
    else
        echo -e "${RED}❌ Le conversazioni potrebbero essere confuse${NC}"
        return 1
    fi
}

# Funzione per testare l'integrazione completa del plug-in
test_complete_integration() {
    local session_id="test-full-$(date +%s)"

    separator "TEST INTEGRAZIONE COMPLETA: $session_id"

    # Crea conversazione
    echo -e "${BLUE}CREAZIONE CONVERSAZIONE${NC}"
    curl -s -X GET "$API_BASE/custom/api/rag/debug/create-conversation/$session_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

    # Step 1: Domanda generica sulla Transizione 5.0
    echo -e "\n${CYAN}STEP 1: DOMANDA GENERICA${NC}"
    response1=$(curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"Ciao, cosa è la Transizione 5.0 e quali benefici offre?\",
        \"conversation_id\": \"$session_id\"
      }")

    echo -e "${CYAN}Risposta 1:${NC}"
    echo "$(echo "$response1" | jq -r '.text')" | head -n 3

    sleep 3

    # Step 2: Domanda specifica che dovrebbe attivare il RAG
    echo -e "\n${CYAN}STEP 2: DOMANDA SPECIFICA PER RAG${NC}"
    response2=$(curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"Quali sono le percentuali del credito d'imposta per la Transizione 5.0?\",
        \"conversation_id\": \"$session_id\"
      }")

    echo -e "${CYAN}Risposta 2:${NC}"
    echo "$(echo "$response2" | jq -r '.text')" | head -n 3

    sleep 3

    # Step 3: Fornisci informazioni personali per estrazione usando l'endpoint test-extraction
    echo -e "\n${CYAN}STEP 3: INFORMAZIONI PERSONALI PER ESTRAZIONE${NC}"
        
    # Usa l'endpoint di estrazione diretta con process_message=true
    echo -e "${CYAN}Esecuzione estrazione diretta con process_message=true${NC}"
    extraction_result=$(curl -s -X POST "$API_BASE/custom/api/rag/test-extraction" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -d "{
        \"text\": \"Sono Marco Bianchi, CTO di TechFuture, un'azienda media del settore IT in Lombardia. Vorremmo investire 350.000 euro in automazione. La mia email è marco@techfuture.it\",
        \"process_message\": true,
        \"session_id\": \"$session_id\"
    }")
        
    echo -e "${CYAN}Risultato estrazione diretta:${NC}"
    echo "$extraction_result"

    # Estrai il session_id restituito per verifica
    result_session_id=$(echo "$extraction_result" | jq -r '.session_id // ""')
    if [[ -n "$result_session_id" ]]; then
        echo -e "${GREEN}✅ Session ID restituito: $result_session_id${NC}"
        if [[ "$result_session_id" != "$session_id" ]]; then
            echo -e "${YELLOW}⚠️ Il session_id restituito è diverso da quello inviato!${NC}"
        fi
    fi

    # Verifica lo stato attuale della conversazione dopo l'estrazione
    echo -e "\n${CYAN}Verifica stato conversazione dopo estrazione:${NC}"
    check_conversation=$(curl -s -X GET "$API_BASE/custom/api/rag/debug/get-conversation/$session_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    lead_data_after_extraction=$(echo "$check_conversation" | jq '.conversation.data.lead_data')
    echo -e "${CYAN}Lead data dopo estrazione:${NC}"
    echo "$lead_data_after_extraction" | jq '.'

    # Attendi un attimo per assicurarti che tutto sia stato salvato
    sleep 2
    
    # Invia messaggio normale per continuare la conversazione
    response3=$(curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"Questi sono i miei dati, puoi aiutarmi con la Transizione 5.0?\",
        \"conversation_id\": \"$session_id\"
      }")

    echo -e "${CYAN}Risposta 3:${NC}"
    echo "$(echo "$response3" | jq -r '.text')" | head -n 3

    sleep 3

    # Step 4: Simula interruzione e ripresa sessione
    echo -e "\n${CYAN}STEP 4: SIMULA INTERRUZIONE E RIPRESA SESSIONE${NC}"
    echo -e "${CYAN}Attesa di 5 secondi che simula chiusura browser...${NC}"
    sleep 5

    response4=$(curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"Sono tornato. Puoi riassumermi i requisiti per accedere alle agevolazioni?\",
        \"conversation_id\": \"$session_id\"
      }")

    echo -e "${CYAN}Risposta 4:${NC}"
    echo "$(echo "$response4" | jq -r '.text')" | head -n 3

    # Verifica finale della conversazione
    echo -e "\n${BLUE}VERIFICA FINALE CONVERSAZIONE${NC}"
    final_conv=$(curl -s -X GET "$API_BASE/custom/api/rag/debug/get-conversation/$session_id" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    msgs_count=$(echo "$final_conv" | jq '.conversation.data.messaggi | length')
    echo -e "${CYAN}Numero totale messaggi: $msgs_count${NC}"

    lead_data=$(echo "$final_conv" | jq '.conversation.data.lead_data')
    echo -e "${CYAN}Lead data estratto:${NC}"
    echo "$lead_data" | jq '.'

    # Verifica valori specifici
    nome_azienda=$(echo "$lead_data" | jq -r '.azienda_data.nome_azienda // "null"')
    email=$(echo "$lead_data" | jq -r '.contatto_data.email // "null"')
    ruolo=$(echo "$lead_data" | jq -r '.contatto_data.ruolo // "null"')
    
    # Verifica se i dati sono stati estratti correttamente
    if [[ "$nome_azienda" == "TechFuture" && "$email" == "marco@techfuture.it" && "$ruolo" == "CTO" ]]; then
        echo -e "${GREEN}✅ Test integrazione completa superato - dati estratti correttamente${NC}"
        return 0
    else
        echo -e "${RED}❌ Test integrazione fallito - dati non estratti correttamente${NC}"
        echo -e "${RED}Azienda: $nome_azienda, Email: $email, Ruolo: $ruolo${NC}"
        return 1
    fi
}

# TEST ENDPOINT WELCOME MESSAGE
separator "TEST ENDPOINT WELCOME MESSAGE"
echo -e "${CYAN}Chiamata endpoint welcome message...${NC}"
welcome_response=$(curl -s -X GET "$API_BASE/custom/api/rag/welcome-message" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$welcome_response" | jq '.'

# Verifica risposta
if [[ $(echo "$welcome_response" | jq -r '.message') && ! $(echo "$welcome_response" | jq -r '.error') ]]; then
    ((TESTS_TOTAL++))
    ((TESTS_PASSED++))
    echo -e "${GREEN}✅ Endpoint welcome message funziona correttamente${NC}"
else
    ((TESTS_TOTAL++))
    echo -e "${RED}❌ Endpoint welcome message non funziona correttamente${NC}"
fi

# TEST CARICAMENTO FILE PROMPT
separator "TEST CARICAMENTO FILE PROMPT"
echo -e "${CYAN}Simulazione errore file mancante...${NC}"

# Rinomina temporaneamente un file prompt per forzare un errore
if [ -f "cheshire-cat/plugins/rag_lead_management/prompts/01_prompt_base.md" ]; then
    mv "cheshire-cat/plugins/rag_lead_management/prompts/01_prompt_base.md" "cheshire-cat/plugins/rag_lead_management/prompts/01_prompt_base.md.bak"
    
    # Tenta di inviare un messaggio che forzerà il caricamento del prompt
    error_response=$(curl -s -X POST "$API_BASE/message" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -d "{
        \"text\": \"Cos'è la Transizione 5.0?\",
        \"conversation_id\": \"test-error-$(date +%s)\"
      }")
    
    # Controlla se c'è un messaggio di errore
    if [[ $(echo "$error_response" | grep -i "error" | wc -l) -gt 0 || $(docker logs cheshire_cat_core --tail 20 | grep -i "file prompt non trovato" | wc -l) -gt 0 ]]; then
        ((TESTS_TOTAL++))
        ((TESTS_PASSED++))
        echo -e "${GREEN}✅ Errore di file mancante gestito correttamente${NC}"
    else
        ((TESTS_TOTAL++))
        echo -e "${RED}❌ Errore di file mancante non rilevato${NC}"
    fi
    
    # Ripristina il file
    mv "cheshire-cat/plugins/rag_lead_management/prompts/01_prompt_base.md.bak" "cheshire-cat/plugins/rag_lead_management/prompts/01_prompt_base.md"
else
    echo -e "${YELLOW}⚠️ File prompt non trovato per il test, salto...${NC}"
fi

# TEST FACT CHECKING
separator "TEST FACT CHECKING"
echo -e "${CYAN}Test risposta con fact checking...${NC}"

# Prima inviamo una query che dovrebbe attivare fact checking
fact_check_session="test-factcheck-$(date +%s)"
fact_check_response=$(curl -s -X POST "$API_BASE/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"text\": \"Il fotovoltaico può accedere alla Transizione 5.0 da solo?\",
    \"conversation_id\": \"$fact_check_session\"
  }")

# Estrai il testo della risposta
response_text=$(echo "$fact_check_response" | jq -r '.text')
echo -e "${CYAN}Risposta:${NC}"
echo "$response_text" | head -n 5

# Verifica che la risposta rispetti i criteri di approccio positivo
negative_patterns=("non è possibile" "non è ammissibile" "non può" "impossibile" "negativo")
negative_count=0

for pattern in "${negative_patterns[@]}"; do
    count=$(echo "$response_text" | grep -i "$pattern" | wc -l)
    negative_count=$((negative_count + count))
done

if [[ $negative_count -eq 0 ]]; then
    ((TESTS_TOTAL++))
    ((TESTS_PASSED++))
    echo -e "${GREEN}✅ Risposta mantiene un approccio positivo${NC}"
else
    ((TESTS_TOTAL++))
    echo -e "${RED}❌ Risposta contiene termini negativi: $negative_count occorrenze${NC}"
fi

# Verifica nei log che fact checking sia stato eseguito
if docker logs cheshire_cat_core --tail 50 | grep -q "Risposta verificata con controllo priorità documenti"; then
    ((TESTS_TOTAL++))
    ((TESTS_PASSED++))
    echo -e "${GREEN}✅ Fact checking eseguito correttamente${NC}"
else
    ((TESTS_TOTAL++))
    echo -e "${RED}❌ Fact checking non eseguito${NC}"
fi

# TEST PRIORITIZZAZIONE DOCUMENTI
separator "TEST PRIORITIZZAZIONE DOCUMENTI"
echo -e "${CYAN}Test prioritizzazione documenti...${NC}"

# Inviamo una query che dovrebbe attivare la prioritizzazione
priority_response=$(curl -s -X POST "$API_BASE/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"text\": \"Quali sono le aliquote del credito d'imposta secondo la normativa più recente?\",
    \"conversation_id\": \"test-priority-$(date +%s)\"
  }")

# Verifica nei log che la prioritizzazione sia stata eseguita
if docker logs cheshire_cat_core --tail 50 | grep -q "Ordine priorità documenti"; then
    ((TESTS_TOTAL++))
    ((TESTS_PASSED++))
    echo -e "${GREEN}✅ Prioritizzazione documenti eseguita correttamente${NC}"
else
    ((TESTS_TOTAL++))
    echo -e "${RED}❌ Prioritizzazione documenti non eseguita${NC}"
fi

# Verifica che nei log ci siano le etichette di priorità (FAQ, DOCUMENTO 2025, ecc.)
if docker logs cheshire_cat_core --tail 50 | grep -E "PRIORITÀ - FAQ|PRIORITÀ - DOCUMENTO 2025" | wc -l > 0; then
    ((TESTS_TOTAL++))
    ((TESTS_PASSED++))
    echo -e "${GREEN}✅ Etichette di priorità presenti nei log${NC}"
else
    ((TESTS_TOTAL++))
    echo -e "${RED}❌ Etichette di priorità non trovate nei log${NC}"
fi

# INIZIO ESECUZIONE DEI TEST
clear
echo -e "${MAGENTA}======================================================${NC}"
echo -e "${MAGENTA}   TEST COMPLETO DEL PLUGIN TRANSIZIONE 5.0${NC}"
echo -e "${MAGENTA}======================================================${NC}"
echo -e "${CYAN}Data di esecuzione: $(date)${NC}"
echo -e "${CYAN}API Base: $API_BASE${NC}"

# Risultati test
TESTS_TOTAL=0
TESTS_PASSED=0

# Verifica plugin attivo
separator "VERIFICA PLUGIN ATTIVO"
plugin_check=$(curl -s -X GET "$API_BASE/custom/api/rag/diagnostic" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$plugin_check" | jq '.'

# Verifica plugin caricato
if [[ $(echo "$plugin_check" | jq -r '.status') == "Plugin is loaded" ]]; then
    ((TESTS_TOTAL++))
    ((TESTS_PASSED++))
    echo -e "${GREEN}✅ Plugin attivo e operativo${NC}"
else
    ((TESTS_TOTAL++))
    echo -e "${RED}❌ Plugin non attivo${NC}"
    # Uscita anticipata se il plugin non è attivo
    echo -e "${RED}Test interrotto: plugin non attivo${NC}"
    exit 1
fi

# Test endpoint
separator "TEST ENDPOINT DISPONIBILI"
endpoint_list=$(curl -s -X GET "$API_BASE/openapi.json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.paths | keys[] | select(contains("api/rag"))')

echo -e "${CYAN}Endpoint disponibili:${NC}"
echo "$endpoint_list"

if [[ -n "$endpoint_list" ]]; then
    ((TESTS_TOTAL++))
    ((TESTS_PASSED++))
    echo -e "${GREEN}✅ Endpoint verificati${NC}"
else
    ((TESTS_TOTAL++))
    echo -e "${RED}❌ Nessun endpoint trovato${NC}"
fi

# Test endpoint di conversazione
echo -e "\n${CYAN}Esecuzione test endpoint conversazione...${NC}"
test_conversation_endpoints
result=$?
((TESTS_TOTAL++))
if [[ $result -eq 0 ]]; then ((TESTS_PASSED++)); fi

# Test RAG (Recupero documenti)
echo -e "\n${CYAN}Esecuzione test RAG...${NC}"
test_ram_functionality "test-rag-$(date +%s)" "Quali sono le aliquote del credito d'imposta per la Transizione 5.0?"
result=$?
((TESTS_TOTAL++))
if [[ $result -eq 0 ]]; then ((TESTS_PASSED++)); fi

# Test persistenza sessioni
echo -e "\n${CYAN}Esecuzione test persistenza sessioni...${NC}"
test_session_persistence "test-session-$(date +%s)" "Ciao, vorrei sapere cosa è la Transizione 5.0" "Grazie per l'informazione, quali aziende possono accedere alle agevolazioni?" "Test persistenza base"
result=$?
((TESTS_TOTAL++))
if [[ $result -eq 0 ]]; then ((TESTS_PASSED++)); fi

# Test estrazione informazioni
echo -e "\n${CYAN}Esecuzione test estrazione informazioni...${NC}"
test_information_extraction "test-extraction-$(date +%s)" "Sono Luigi Verdi, CEO di InnoTech. Siamo una piccola azienda di manifattura in Piemonte e vorremmo investire 250.000 euro in digitalizzazione entro 2 mesi. La mia email è luigi@innotech.it e il telefono è 3334455667"
result=$?
((TESTS_TOTAL++))
if [[ $result -eq 0 ]]; then ((TESTS_PASSED++)); fi

# Test utenti multipli simultanei
echo -e "\n${CYAN}Esecuzione test utenti multipli simultanei...${NC}"
test_multiple_users
result=$?
((TESTS_TOTAL++))
if [[ $result -eq 0 ]]; then ((TESTS_PASSED++)); fi

# Test integrazione completa
echo -e "\n${CYAN}Esecuzione test integrazione completa...${NC}"
test_complete_integration
result=$?
((TESTS_TOTAL++))
if [[ $result -eq 0 ]]; then ((TESTS_PASSED++)); fi

# Riepilogo finale
separator "RIEPILOGO FINALE"
echo -e "${CYAN}Test eseguiti: $TESTS_TOTAL${NC}"
echo -e "${GREEN}Test superati: $TESTS_PASSED${NC}"
echo -e "${RED}Test falliti: $(($TESTS_TOTAL - $TESTS_PASSED))${NC}"

echo -e "\n${CYAN}Percentuale di successo: $(($TESTS_PASSED * 100 / $TESTS_TOTAL))%${NC}"

if [[ $TESTS_PASSED -eq $TESTS_TOTAL ]]; then
    echo -e "\n${GREEN}✅ TUTTI I TEST SUPERATI${NC}"
else
    echo -e "\n${RED}❌ ALCUNI TEST FALLITI${NC}"
fi

# Log finali
echo -e "\n${CYAN}Ultimi log pertinenti:${NC}"
get_relevant_logs

echo -e "\n${MAGENTA}======================================================${NC}"
echo -e "${MAGENTA}   FINE DEI TEST${NC}"
echo -e "${MAGENTA}======================================================${NC}"