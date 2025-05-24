// frontend/components/ChatBox.tsx
"use client"
import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './chat-message';
import { useAuthContext } from '@/contexts/auth-context';
import useCheshireCat from '@/hooks/use-cheshire-cat';
import useSharedConfig from '@/hooks/use-shared-config';

// Definizione di tipo per l'interfaccia Message attesa da ChatMessage
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  isThinking?: boolean;
}

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

export default function ChatBox() {
  const [inputValue, setInputValue] = useState('');
  const [thinkingMessage, setThinkingMessage] = useState<Message | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const { isAuthenticated, authToken, isLoading: authLoading, autoLogin } = useAuthContext();
  
  // Otteniamo la configurazione dal hook
  const { config, loading: configLoading, error: configError } = useSharedConfig();
  
  // Utilizziamo il nostro hook personalizzato per la chat
  const { 
    messages: chatMessages, 
    isConnected, 
    isLoading, 
    error,
    sendMessage,
    addWelcomeMessage
  } = useCheshireCat({
    host: 'api.transizione5.info',
    secure: true,
    autoConnect: true,
    onError: (errorMessage) => {
      console.error(`[ChatBox] Errore: ${errorMessage}`);
    }
  });
  
  // Converti i messaggi nel formato atteso da ChatMessage
  const formattedMessages: Message[] = chatMessages.map(msg => ({
    id: msg.id,
    role: msg.role === 'human' ? 'user' : 'assistant',
    content: msg.content,
    isStreaming: isLoading && msg.role === 'bot' && msg === chatMessages[chatMessages.length - 1]
  }));
  
  // Funzione di scroll
  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  // Versione throttled per evitare troppi aggiornamenti
  const throttledScrollToBottom = throttle(scrollToBottom, 50);
  
  // Esegui l'autologin all'avvio se necessario
  useEffect(() => {
    const initAuth = async () => {
      if (!isAuthenticated && !authLoading) {
        console.log('Tentativo di auto-login all\'avvio del ChatBox');
        await autoLogin();
      }
    };
    
    initAuth();
  }, [isAuthenticated, authLoading, autoLogin]);
  
  // Aggiungi messaggio di benvenuto all'avvio quando la configurazione è caricata
  useEffect(() => {
    if (formattedMessages.length === 0 && config && !configLoading) {
      // Ora usiamo config? per accesso sicuro
      const welcomeMessage = config.assistant?.welcomeMessage || "Benvenuto! Come posso aiutarti oggi?";
      addWelcomeMessage(welcomeMessage);
    }
  }, [addWelcomeMessage, formattedMessages.length, config, configLoading]);
  
  // Scroll alla fine della chat quando arrivano nuovi messaggi
  useEffect(() => {
    scrollToBottom();
  }, [formattedMessages, thinkingMessage]);
  
  // Gestisce il messaggio di "sto pensando"
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
  
  // Gestisce invio messaggio
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;
    
    // Se non siamo autenticati, prova l'auto-login
    if (!isAuthenticated) {
      autoLogin().then(success => {
        if (success) {
          // Se l'auto-login ha successo, riprova l'invio
          handleSubmit(e);
        } else {
          console.error('Autenticazione fallita.');
        }
      });
      return;
    }
    
    // Invia il messaggio
    const success = await sendMessage(inputValue.trim());
    
    if (success) {
      // Se l'invio è riuscito, resetta l'input
      setInputValue('');
    }
  };
  
  // Mostra un loader durante il caricamento della configurazione
  if (configLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 flex items-center justify-center h-[500px]">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 mx-auto border-4 border-emerald-500 border-t-transparent rounded-full"></div>
          <p className="mt-2 text-gray-600">Caricamento configurazione...</p>
        </div>
      </div>
    );
  }
  
  // Titolo dell'assistente (con fallback se config non ha il valore)
  const assistantTitle = config?.assistant?.fullTitle || "Assistente Virtuale";
  
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="bg-emerald-600 text-white px-4 py-3">
        <h2 className="font-medium">{assistantTitle}</h2>
      </div>
      
      <div className="p-4">
        {/* Avviso di errore configurazione - solo se c'è un errore */}
        {configError && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
            <h3 className="text-amber-800 font-medium">Errore configurazione</h3>
            <p className="text-amber-700 mt-1">
              {configError}
            </p>
          </div>
        )}
        
        {/* Avviso di autenticazione - mostrato solo durante il caricamento iniziale */}
        {authLoading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4 animate-pulse">
            <h3 className="text-blue-800 font-medium">Inizializzazione in corso</h3>
            <p className="text-blue-700 mt-1">
              Connessione all'assistente virtuale in corso...
            </p>
          </div>
        )}
        
        {/* Errore di autenticazione - mostrato solo se l'autenticazione è fallita definitivamente */}
        {!isAuthenticated && !authLoading && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
            <h3 className="text-amber-800 font-medium">Autenticazione fallita</h3>
            <p className="text-amber-700 mt-1">
              Non è stato possibile connettersi all'assistente virtuale. Ricarica la pagina o contatta l'amministratore.
            </p>
            <button 
              onClick={() => autoLogin()} 
              className="mt-2 px-4 py-2 bg-amber-600 text-white rounded hover:bg-amber-700"
            >
              Riprova
            </button>
          </div>
        )}
        
        <div 
          ref={chatContainerRef} 
          className="space-y-4 mb-4 max-h-[60vh] overflow-y-auto relative" 
          style={{height: "400px"}}
        >
          {formattedMessages.map(message => (
          // Renderizza solo messaggi con contenuto
          message.content ? (
            <ChatMessage 
              key={message.id} 
              message={message}
              onUpdate={throttledScrollToBottom}
            />
          ) : null
        ))}
          
          {/* Messaggio di "sto pensando" */}
          {thinkingMessage && (
            <ChatMessage 
              key={thinkingMessage.id} 
              message={thinkingMessage}
              onUpdate={throttledScrollToBottom}
            />
          )}
          
          <div ref={messagesEndRef} style={{height: '40px'}}></div>
          
          {/* Errore */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-2 text-red-600 text-sm">
              {error}
            </div>
          )}
        </div>
        
        {/* Form invio messaggio */}
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading || (authLoading || (!isAuthenticated && !authLoading))}
              placeholder={isAuthenticated ? "Scrivi un messaggio..." : "Autenticazione in corso..."}
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:bg-gray-100"
            />
            <button
              type="submit" 
              disabled={isLoading || !inputValue.trim() || (authLoading || (!isAuthenticated && !authLoading))}
              className="bg-emerald-600 text-white px-4 py-2 rounded-lg disabled:bg-gray-300 hover:bg-emerald-700 transition-colors"
            >
              {isLoading ? (
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : "Invia"}
            </button>
          </div>
        </form>
      </div>
      
      {/* Indicatore di stato connessione */}
      <div className="px-4 py-2 bg-gray-100 text-xs text-gray-500 flex items-center">
        <span className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
        {isConnected ? 'Connesso' : 'Disconnesso'}
      </div>
    </div>
  );
}