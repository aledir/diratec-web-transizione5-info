// frontend/hooks/useCheshireCat.ts
import { useState, useEffect, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ChatClientWrapper, { ChatMessage } from '../utils/chat-client';
import { useAuthContext } from '@/contexts/auth-context';

// Definizione dei tipi
interface UseCheshireCatOptions {
  autoConnect?: boolean;
  host?: string;
  secure?: boolean;
  port?: number;
  maxReconnectAttempts?: number;
  onError?: (error: string) => void;
}

interface ChatState {
  messages: ChatMessage[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  sessionId: string;
  reconnectAttempts: number;
}

// Interfaccia per il risultato dell'hook
interface CheshireCatResult extends ChatState {
  sendMessage: (text: string) => Promise<boolean>;
  addWelcomeMessage: (content: string) => void;
  resetConversation: () => void;
  connect: () => boolean;
  disconnect: () => void;
  reconnect: () => boolean;
}

// Questa variabile controlla se l'hook è stato chiamato almeno una volta
let hookInitialized = false;

export default function useCheshireCat(options: UseCheshireCatOptions = {}): CheshireCatResult {
  // Ottieni il contesto di autenticazione
  const { authToken, isAuthenticated, autoLogin } = useAuthContext();
  
  // Stato della chat
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isConnected: false,
    isLoading: false,
    error: null,
    sessionId: '',
    reconnectAttempts: 0
  });
  
  // Flag per prevenire aggiornamenti di stato dopo lo smontaggio
  const isMountedRef = useRef(true);
  
  // Riferimento al token attuale che sta ricevendo streaming
  const currentTokensRef = useRef<string>('');
  const currentMessageIdRef = useRef<string | null>(null);
  
  // Imposta isMountedRef a false quando il componente viene smontato
  useEffect(() => {
    hookInitialized = true;
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);
  
  // Carica o genera un ID sessione (una sola volta)
  useEffect(() => {
    const storedSessionId = localStorage.getItem('chat_session_id');
    if (storedSessionId) {
      setChatState(prev => ({ ...prev, sessionId: storedSessionId }));
      console.log(`[useCheshireCat] Sessione recuperata: ${storedSessionId}`);
    } else {
      const newSessionId = uuidv4();
      localStorage.setItem('chat_session_id', newSessionId);
      setChatState(prev => ({ ...prev, sessionId: newSessionId }));
      console.log(`[useCheshireCat] Nuova sessione creata: ${newSessionId}`);
    }
  }, []);
  
  // Crea e inizializza il client quando authToken e sessionId sono disponibili
  useEffect(() => {
    // Se non abbiamo token o sessione, esci subito
    if (!authToken || !chatState.sessionId) return;
    
    // Aggiorniamo lo stato solo se il componente è montato
    const safeSetState = (updater: (prev: ChatState) => ChatState) => {
      if (isMountedRef.current) {
        setChatState(updater);
      }
    };
    
    // Ottieni l'istanza singleton del client e configura i callback
    const client = ChatClientWrapper.getInstance({
      host: options.host || 'api.transizione5.info',
      secure: options.secure !== undefined ? options.secure : true,
      port: options.port,
      credential: authToken ?? undefined,
      userId: chatState.sessionId,
      
      // Callbacks
      onConnected: () => {
        console.log('[useCheshireCat] Connessione WebSocket stabilita');
        safeSetState(prev => ({ 
          ...prev, 
          isConnected: true, 
          error: null,
          reconnectAttempts: 0
        }));
      },
      
      onDisconnected: () => {
        console.log('[useCheshireCat] Disconnesso dal WebSocket');
        
        safeSetState(prev => {
          return { 
            ...prev, 
            isConnected: false,
            error: 'Connessione WebSocket persa. Premi "Connetti" per riconnetterti.',
            reconnectAttempts: prev.reconnectAttempts + 1
          };
        });
      },
      
      onError: (error) => {
        const errorMessage = typeof error === 'string' 
          ? error 
          : error?.message || error?.description || 'Errore di connessione al server';
        
        console.error('[useCheshireCat] Errore WebSocket:', errorMessage);
        
        safeSetState(prev => ({ 
          ...prev, 
          error: errorMessage 
        }));
        
        if (options.onError) options.onError(errorMessage);
      },
      
      onToken: (token) => {
        // Aggiungi il token al buffer corrente
        currentTokensRef.current += token;
        
        // Aggiorna il messaggio in streaming
        if (currentMessageIdRef.current) {
          safeSetState(prev => {
            const updatedMessages = prev.messages.map(msg => {
              if (msg.id === currentMessageIdRef.current) {
                return {
                  ...msg,
                  content: currentTokensRef.current
                };
              }
              return msg;
            });
            
            return {
              ...prev,
              messages: updatedMessages
            };
          });
        }
      },
      
      onMessage: (message) => {
        // Il messaggio è completo, aggiorna lo stato e resetta lo streaming
        safeSetState(prev => {
          // Se c'è un messaggio in streaming, sostituiscilo
          if (currentMessageIdRef.current) {
            const updatedMessages = prev.messages.map(msg => {
              if (msg.id === currentMessageIdRef.current) {
                return {
                  ...msg,
                  content: message.content,
                  type: message.type
                };
              }
              return msg;
            });
            
            return {
              ...prev,
              messages: updatedMessages,
              isLoading: false
            };
          } else {
            // Altrimenti aggiungi un nuovo messaggio
            return {
              ...prev,
              messages: [...prev.messages, message],
              isLoading: false
            };
          }
        });
        
        // Resetta lo stato dello streaming
        currentTokensRef.current = '';
        currentMessageIdRef.current = null;
      }
    });
    
    // Connetti automaticamente se richiesto e non già connesso
    if (options.autoConnect !== false && !client.isConnected()) {
      console.log('[useCheshireCat] Avvio connessione automatica...');
      client.init();
    }
    
    // Non è necessario un cleanup, poiché stiamo usando un singleton
    
  }, [authToken, chatState.sessionId, options]);
  
  // Funzione per inviare un messaggio
  const sendMessage = useCallback(async (text: string): Promise<boolean> => {
    if (!text.trim()) {
      console.warn('[useCheshireCat] Tentativo di inviare messaggio vuoto');
      return false;
    }
    
    const client = ChatClientWrapper.getInstance({credential: authToken ?? undefined});
    
    if (!client) {
      console.error('[useCheshireCat] Client non inizializzato');
      if (isMountedRef.current) {
        setChatState(prev => ({
          ...prev,
          error: 'Client non inizializzato. Ricarica la pagina.'
        }));
      }
      return false;
    }
    
    if (!isAuthenticated && autoLogin) {
      console.log('[useCheshireCat] Tentativo di auto-login prima di inviare messaggio');
      const success = await autoLogin();
      if (!success) {
        if (isMountedRef.current) {
          setChatState(prev => ({
            ...prev,
            error: 'Autenticazione fallita. Ricarica la pagina o contatta il supporto.'
          }));
        }
        return false;
      }
    }
    
    // Messaggio dell'utente
    const userMessage: ChatMessage = {
      id: uuidv4(),
      type: 'chat',
      content: text.trim(),
      role: 'human',
      timestamp: Date.now()
    };
    
    // Prepara il messaggio in streaming del bot
    const botMessageId = uuidv4();
    currentMessageIdRef.current = botMessageId;
    currentTokensRef.current = '';
    
    const botMessage: ChatMessage = {
      id: botMessageId,
      type: 'chat',
      content: '',
      role: 'bot',
      timestamp: Date.now()
    };
    
    // Aggiorna lo stato con entrambi i messaggi
    if (isMountedRef.current) {
      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, userMessage, botMessage],
        isLoading: true,
        error: null
      }));
    }
    
    // Invia il messaggio al server
    try {
      console.log(`[useCheshireCat] Invio messaggio: "${text.substring(0, 30)}${text.length > 30 ? '...' : ''}"`);
      const success = client.sendMessage(text.trim(), {
        userId: chatState.sessionId,
        sessionId: chatState.sessionId
      });
      
      return success;
    } catch (error) {
      console.error('[useCheshireCat] Errore nell\'invio del messaggio:', error);
      if (isMountedRef.current) {
        setChatState(prev => ({
          ...prev,
          isLoading: false,
          error: `Errore nell'invio del messaggio: ${error instanceof Error ? error.message : String(error)}`
        }));
      }
      return false;
    }
  }, [isAuthenticated, autoLogin, chatState.sessionId, authToken]);
  
  // Funzione per aggiungere un messaggio di benvenuto
  const addWelcomeMessage = useCallback((content: string) => {
    const welcomeMsg: ChatMessage = {
      id: uuidv4(),
      type: 'chat',
      content: content,
      role: 'bot',
      timestamp: Date.now()
    };
    
    console.log('[useCheshireCat] Aggiunto messaggio di benvenuto');
    if (isMountedRef.current) {
      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, welcomeMsg]
      }));
    }
  }, []);
  
  // Funzione per resettare la conversazione
  const resetConversation = useCallback(() => {
    // Genera un nuovo ID sessione
    const newSessionId = uuidv4();
    localStorage.setItem('chat_session_id', newSessionId);
    
    console.log(`[useCheshireCat] Reset conversazione, nuova sessione: ${newSessionId}`);
    
    // Resetta lo stato
    if (isMountedRef.current) {
      setChatState(prev => ({
        ...prev,
        messages: [],
        isLoading: false,
        error: null,
        sessionId: newSessionId,
        reconnectAttempts: 0
      }));
    }
    
    // Aggiorna il client se esiste
    const client = ChatClientWrapper.getInstance({credential: authToken ?? undefined});
    if (client) {
      client.updateSession(newSessionId, newSessionId);
    }
  }, [authToken]);
  
  // Funzione per tentare manualmente la connessione
  const connect = useCallback(() => {
    console.log('[useCheshireCat] Tentativo manuale di connessione');
    
    const client = ChatClientWrapper.getInstance({credential: authToken ?? undefined});
    if (!client) {
      console.error('[useCheshireCat] Client non inizializzato');
      return false;
    }
    
    return client.init();
  }, [authToken]);
  
  // Funzione per disconnettere manualmente
  const disconnect = useCallback(() => {
    console.log('[useCheshireCat] Disconnessione manuale');
    const client = ChatClientWrapper.getInstance({credential: authToken ?? undefined});
    if (client) {
      client.disconnect();
    }
  }, [authToken]);
  
  // Funzione per tentare manualmente la riconnessione
  const reconnect = useCallback(() => {
    console.log('[useCheshireCat] Tentativo manuale di riconnessione');
    
    const client = ChatClientWrapper.getInstance({credential: authToken ?? undefined});
    if (!client) {
      console.error('[useCheshireCat] Client non inizializzato');
      return false;
    }
    
    return client.reset();
  }, [authToken]);
  
  // Ritorna le funzioni e lo stato
  return {
    ...chatState,
    sendMessage,
    addWelcomeMessage,
    resetConversation,
    connect,
    disconnect,
    reconnect
  };
}