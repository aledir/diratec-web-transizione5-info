// frontend/utils/chatClient.ts
// Wrapper semplificato per CatClient
import { CatClient, CatSettings, SocketRequest, SocketResponse } from 'ccat-api';

export interface ChatMessage {
  id: string;
  type: string;
  content: string;
  role: 'human' | 'bot';
  timestamp?: number;
}

export interface ChatClientConfig {
  host?: string;
  port?: number;
  secure?: boolean;
  userId?: string;
  credential?: string;
  onToken?: (token: string) => void;
  onMessage?: (message: ChatMessage) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: any) => void;
}

// Questa classe è un singleton per evitare creazioni multiple
export class ChatClientWrapper {
  private client: CatClient | null = null;
  private callbacks: ChatClientConfig;
  private static instance: ChatClientWrapper | null = null;
  
  // Factory method per ottenere l'istanza singleton
  public static getInstance(config: ChatClientConfig): ChatClientWrapper {
    if (!ChatClientWrapper.instance) {
      ChatClientWrapper.instance = new ChatClientWrapper(config);
    } else {
      // Aggiorna i callback se l'istanza esiste già
      ChatClientWrapper.instance.updateCallbacks(config);
    }
    return ChatClientWrapper.instance;
  }
  
  // Costruttore privato per il pattern singleton
  private constructor(config: ChatClientConfig) {
    this.callbacks = config;
    console.log(`[ChatClientWrapper] Creato con host: ${config.host}, userId: ${config.userId?.substring(0, 8)}...`);
  }
  
  // Aggiorna i callback senza ricreare il client
  private updateCallbacks(config: ChatClientConfig) {
    console.log(`[ChatClientWrapper] Aggiornamento callbacks`);
    this.callbacks = {
      ...this.callbacks,
      onToken: config.onToken || this.callbacks.onToken,
      onMessage: config.onMessage || this.callbacks.onMessage,
      onConnected: config.onConnected || this.callbacks.onConnected,
      onDisconnected: config.onDisconnected || this.callbacks.onDisconnected,
      onError: config.onError || this.callbacks.onError
    };
  }
  
  private setupEventHandlers() {
    if (!this.client) return;
    
    // Gestisce la connessione stabilita
    this.client.onConnected(() => {
      console.log('[ChatClientWrapper] WebSocket connesso con successo');
      if (this.callbacks.onConnected) {
        this.callbacks.onConnected();
      }
    });
    
    // Gestisce la disconnessione
    this.client.onDisconnected(() => {
      console.log('[ChatClientWrapper] WebSocket disconnesso');
      if (this.callbacks.onDisconnected) {
        this.callbacks.onDisconnected();
      }
    });
    
    // Gestisce gli errori
    this.client.onError((error) => {
      console.error('[ChatClientWrapper] Errore WebSocket:', error);
      if (this.callbacks.onError) {
        this.callbacks.onError(error);
      }
    });
    
    // Gestisce i messaggi in arrivo (inclusi token e messaggi completi)
    this.client.onMessage((data: SocketResponse) => {
      if (data.type === 'chat_token' && data.text && this.callbacks.onToken) {
        // Streaming di token individuali
        this.callbacks.onToken(data.text);
      }
      else if (data.type === 'chat' && this.callbacks.onMessage) {
        // Messaggio completo
        const message: ChatMessage = {
          id: data.uuid || `msg-${Date.now()}`,
          type: data.type,
          content: data.text || '',
          role: 'bot',
          timestamp: Date.now()
        };
        
        this.callbacks.onMessage(message);
      }
    });
  }
  
  /**
   * Inizializza la connessione al server Cheshire Cat
   */
  public init(): boolean {
    try {
      // Se il client è già inizializzato e connesso, non fare nulla
      if (this.client && this.isConnected()) {
        console.log('[ChatClientWrapper] Client già connesso');
        return true;
      }
      
      // Se il client esiste ma non è connesso, riprova a connetterlo
      if (this.client) {
        console.log('[ChatClientWrapper] Riconnessione client esistente');
        this.client.init();
        return true;
      }
      
      // Configura il client con i parametri supportati dalla documentazione
      const config: CatSettings = {
        host: this.callbacks.host || 'localhost',
        secure: this.callbacks.secure !== undefined ? this.callbacks.secure : true,
        port: this.callbacks.port,
        userId: this.callbacks.userId,
        credential: this.callbacks.credential,
        // Usiamo instant: false per evitare connessione automatica
        instant: false
      };
      
      console.log('[ChatClientWrapper] Creazione nuova istanza CatClient');
      this.client = new CatClient(config);
      this.setupEventHandlers();
      
      console.log('[ChatClientWrapper] Inizializzazione connessione WebSocket...');
      this.client.init();
      return true;
    } catch (error) {
      console.error('[ChatClientWrapper] Errore nell\'inizializzazione:', error);
      if (this.callbacks.onError) {
        this.callbacks.onError(error);
      }
      return false;
    }
  }
  
  /**
   * Invia un messaggio al server
   */
  public sendMessage(text: string, metadata?: { userId?: string; sessionId?: string }): boolean {
    if (!this.client) {
      console.error('[ChatClientWrapper] Tentativo di invio messaggio con client non inizializzato');
      return false;
    }
    
    try {
      // Crea l'oggetto SocketRequest
      const request: SocketRequest = {
        text: text,
        user_id: metadata?.userId,
        conversation_id: metadata?.sessionId,
        timestamp: Date.now()
      };
      
      // Invia il messaggio
      console.log(`[ChatClientWrapper] Invio messaggio: ${text.substring(0, 20)}...`);
      this.client.send(request);
      return true;
    } catch (error) {
      console.error('[ChatClientWrapper] Errore nell\'invio del messaggio:', error);
      if (this.callbacks.onError) {
        this.callbacks.onError(error);
      }
      return false;
    }
  }
  
  /**
   * Disconnette dal server
   */
  public disconnect() {
    if (!this.client) {
      console.warn('[ChatClientWrapper] Tentativo di disconnessione con client non inizializzato');
      return;
    }
    
    try {
      console.log('[ChatClientWrapper] Disconnessione WebSocket in corso...');
      this.client.close();
    } catch (error) {
      console.error('[ChatClientWrapper] Errore nella disconnessione:', error);
    }
  }
  
  /**
   * Aggiorna i parametri userId e sessionId
   */
  public updateSession(userId?: string, sessionId?: string) {
    if (!userId && !sessionId) {
      console.warn('[ChatClientWrapper] updateSession chiamato senza nuovi parametri');
      return;
    }
    
    // Se non abbiamo un client, non fare nulla
    if (!this.client) {
      console.warn('[ChatClientWrapper] Impossibile aggiornare sessione senza client inizializzato');
      return;
    }
    
    try {
      console.log(`[ChatClientWrapper] Aggiornamento sessione: userId=${userId?.substring(0, 8)}..., sessionId=${sessionId?.substring(0, 8)}...`);
      
      // Chiudi il client attuale
      this.client.close();
      this.client = null;
      
      // Crea un nuovo client con i parametri aggiornati
      const config: CatSettings = {
        host: this.callbacks.host || 'localhost',
        secure: this.callbacks.secure !== undefined ? this.callbacks.secure : true,
        port: this.callbacks.port,
        userId: userId || this.callbacks.userId,
        credential: this.callbacks.credential,
        instant: false
      };
      
      console.log('[ChatClientWrapper] Ricreazione client con nuovi parametri sessione');
      this.client = new CatClient(config);
      
      // Ripristina i callback sul nuovo client
      this.setupEventHandlers();
      
      // Reinizializza la connessione
      this.init();
    } catch (error) {
      console.error('[ChatClientWrapper] Errore nell\'aggiornamento della sessione:', error);
      if (this.callbacks.onError) {
        this.callbacks.onError(error);
      }
    }
  }
  
  /**
   * Verifica se la connessione è attiva
   */
  public isConnected(): boolean {
    try {
      // Controlliamo se il client esiste
      if (!this.client) return false;
      
      // Utilizziamo il cast per accedere alla proprietà socket se presente
      const socket = (this.client as any).socket;
      return socket && socket.readyState === WebSocket.OPEN;
    } catch (error) {
      console.error('[ChatClientWrapper] Errore nel controllo stato connessione:', error);
      return false;
    }
  }
  
  /**
   * Forza la disconnessione e ricreazione del client
   */
  public reset(): boolean {
    try {
      console.log('[ChatClientWrapper] Reset completo del client');
      
      // Chiudi il client esistente
      if (this.client) {
        this.client.close();
        this.client = null;
      }
      
      // Inizializza un nuovo client
      return this.init();
    } catch (error) {
      console.error('[ChatClientWrapper] Errore nel reset del client:', error);
      return false;
    }
  }
  
  /**
   * Esegue una pulizia completa prima della dismissione
   * Nota: per il singleton, questa funzione non elimina l'istanza
   */
  public cleanup() {
    if (this.client) {
      console.log('[ChatClientWrapper] Pulizia risorse WebSocket');
      // Chiudi la connessione in modo pulito
      this.client.close();
      // Rimuovi i riferimenti al client ma mantieni l'istanza singleton
      this.client = null;
    }
  }
}

export default ChatClientWrapper;