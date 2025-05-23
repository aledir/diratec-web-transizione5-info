// frontend/components/Chat/ChatWidget.tsx
import React, { useEffect, useState, useRef } from 'react';
import ChatMessage from './chat-message';
import ChatInput from './chat-input';
import LoadingIndicator from './loading-indicator';
import PredefinedQuestions from './predefined-questions';
import UserSessionManager from './user-session-manager';
import { UserSession, updateLastActivity, ConversationData, saveConversation, extractConversationTitle } from '../../utils/sessionManager';
import useCheshireCat from '../../hooks/useCheshireCat';
import useSharedConfig from '../../hooks/useSharedConfig';
import styles from './chat.module.css';

// Implementiamo throttle direttamente in questo file per evitare problemi di importazione
function throttle(callback: Function, limit: number = 100) {
  let inThrottle: boolean = false;
  
  return function(this: any, ...args: any[]) {
    if (!inThrottle) {
      callback.apply(this, args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

// Interfacce
interface ChatWidgetProps {
  config: {
    host?: string;
    port?: number;
    secure?: boolean;
    apiKey?: string;
  };
  predefinedQuestions?: string[];
  welcomeMessage?: string;
  className?: string;
}

// Interfaccia Message
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  isThinking?: boolean;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({ 
  config: apiConfig, 
  predefinedQuestions = [], 
  welcomeMessage,
  className = ''
}) => {
  // Utilizziamo il nostro hook per il config
  const { config, loading: configLoading, error: configError } = useSharedConfig();
  
  const [userSession, setUserSession] = useState<UserSession | null>(null);
  const [thinkingMessage, setThinkingMessage] = useState<Message | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatMessagesRef = useRef<HTMLDivElement>(null);
  const conversationId = useRef<string>(`conv-${Date.now()}`);
  
  // Usa il messaggio di benvenuto dalla configurazione, con fallback al prop
  const finalWelcomeMessage = welcomeMessage || 
    (config?.assistant?.welcomeMessage || "Benvenuto! Come posso aiutarti oggi?");
  
  // Utilizziamo il nostro hook personalizzato per la chat
  const { 
    messages, 
    isConnected, 
    isLoading, 
    error, 
    sessionId,
    sendMessage, 
    addWelcomeMessage,
    resetConversation 
  } = useCheshireCat({
    host: apiConfig.host || 'api.transizione5.info',
    secure: apiConfig.secure !== undefined ? apiConfig.secure : true,
    port: apiConfig.port,
    autoConnect: false, // Connetteremo manualmente dopo l'inizializzazione della sessione
    onError: (errorMessage) => {
      console.error(`[ChatWidget] Errore: ${errorMessage}`);
    }
  });
  
  // Formatta i messaggi per il componente ChatMessage
  const formattedMessages: Message[] = messages.map(msg => ({
    id: msg.id,
    role: (msg.role === 'human' ? 'user' : 'assistant') as 'user' | 'assistant',
    content: msg.content,
    isStreaming: isLoading && msg.role === 'bot' && msg === messages[messages.length - 1]
  }));
  
  // Funzione di scroll
  const scrollToBottom = () => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  };

  // Versione throttled per evitare troppi aggiornamenti
  const throttledScrollToBottom = throttle(scrollToBottom, 50);
  
  // Gestisce l'aggiornamento della sessione utente
  const handleSessionUpdate = (session: UserSession) => {
    setUserSession(session);
  };

  // Resetta la conversazione (nuova sessione)
  const handleReset = () => {
    // Chiama il reset del hook
    resetConversation();
    
    // Genera un nuovo ID conversazione
    conversationId.current = `conv-${Date.now()}`;
    
    // Aggiungi il messaggio di benvenuto
    setTimeout(() => {
      addWelcomeMessage(finalWelcomeMessage);
    }, 500);
  };

  // Effetto iniziale per aggiungere il messaggio di benvenuto
  useEffect(() => {
    if (messages.length === 0 && !configLoading) {
      addWelcomeMessage(finalWelcomeMessage);
    }
  }, [finalWelcomeMessage, addWelcomeMessage, messages.length, configLoading]);

  // Effetto di scrolling automatico
  useEffect(() => {
    scrollToBottom();
  }, [messages, thinkingMessage, isLoading]);

  // Aggiorna l'ultima attività quando si interagisce con la chat
  useEffect(() => {
    const interval = setInterval(() => {
      if (isConnected && userSession) {
        updateLastActivity();
      }
    }, 60000); // Aggiorna ogni minuto

    return () => clearInterval(interval);
  }, [isConnected, userSession]);
  
  // Gestione del messaggio "sto pensando"
  useEffect(() => {
    if (isLoading) {
      // Se sta caricando e non c'è già un messaggio di thinking, aggiungiamolo
      if (!thinkingMessage) {
        setThinkingMessage({
          id: 'thinking-' + Date.now(),
          role: 'assistant',
          content: '',
          isThinking: true
        });
      }
    } else {
      // Se non sta più caricando, rimuovi il messaggio di thinking
      setThinkingMessage(null);
    }
  }, [isLoading]);
  
  // Salva la conversazione se l'opzione è abilitata
  useEffect(() => {
    if (process.env.NEXT_PUBLIC_ENABLE_CONVERSATION_SAVE === 'true' && userSession && messages.length > 0) {
      const conversation: ConversationData = {
        id: conversationId.current,
        sessionId: userSession.sessionId,
        userId: userSession.userId,
        username: userSession.username,
        messages: messages.map(msg => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp
        })),
        createdAt: Date.now(),
        updatedAt: Date.now(),
        title: extractConversationTitle(messages)
      };
      
      saveConversation(conversation);
    }
  }, [messages, userSession]);

  // Gestore invio messaggi
  const handleSendMessage = (text: string) => {
    if (!isConnected || isLoading || !userSession) return;
    
    // Aggiorna l'ultima attività
    updateLastActivity();
    
    // Invia il messaggio
    sendMessage(text);
  };

  // Mostra messaggio di caricamento configurazione se necessario
  if (configLoading) {
    return (
      <div className={`${styles.chatWidget} ${className}`}>
        <div className={styles.chatHeader}>
          <h2>Assistente Virtuale</h2>
        </div>
        <div className={styles.loadingContainer}>
          <LoadingIndicator />
          <p>Caricamento configurazione...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.chatWidget} ${className}`}>
      <div className={styles.chatHeader}>
        <h2>{config?.assistant?.fullTitle || "Assistente Virtuale"}</h2>
        <div className={styles.connectionStatus}>
          <span className={isConnected ? styles.connected : styles.disconnected}></span>
          {isConnected ? 'Connesso' : 'Disconnesso'}
        </div>
      </div>
      
      {configError && (
        <div className={styles.errorMessage}>
          <span className={styles.errorIcon}>⚠️</span>
          Errore configurazione: {configError}
        </div>
      )}
      
      <UserSessionManager 
        onSessionUpdate={handleSessionUpdate} 
        onReset={handleReset}
      />
      
      <div className={styles.chatMessages} ref={chatMessagesRef}>
        {formattedMessages.map((message) => (
          <ChatMessage 
            key={message.id} 
            message={message}
            onUpdate={throttledScrollToBottom}
          />
        ))}
        
        {/* Messaggio di "sto pensando" */}
        {thinkingMessage && (
          <ChatMessage 
            key={thinkingMessage.id} 
            message={thinkingMessage}
            onUpdate={throttledScrollToBottom}
          />
        )}
        
        <div className={`${styles.typingIndicator} ${isLoading && !formattedMessages[formattedMessages.length - 1]?.isStreaming && !thinkingMessage ? styles.typingIndicatorVisible : ''}`}>
          <LoadingIndicator />
        </div>
        
        {error && (
          <div className={styles.errorMessage}>
            <span className={styles.errorIcon}>⚠️</span>
            {error}
          </div>
        )}
        
        <div className={styles.messagesEndSpacer} ref={messagesEndRef}></div>
      </div>
      
      {predefinedQuestions.length > 0 && (
        <PredefinedQuestions 
          questions={predefinedQuestions} 
          onSelectQuestion={handleSendMessage} 
        />
      )}
      
      <ChatInput 
        onSendMessage={handleSendMessage} 
        disabled={!isConnected || isLoading} 
      />
    </div>
  );
};

export default ChatWidget;