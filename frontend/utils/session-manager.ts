// frontend/utils/sessionManager.ts
// Gestione delle sessioni utente e salvataggio conversazioni

import { v4 as uuidv4 } from 'uuid';

// Definizione dei tipi
export interface UserSession {
  userId: string;
  sessionId: string;
  username?: string;
  createdAt: number;
  lastActivity: number;
}

export interface ConversationData {
  id: string;
  sessionId: string;
  userId: string;
  username?: string;
  messages: any[];
  createdAt: number;
  updatedAt: number;
  title?: string;
}

// Costanti
const USER_SESSION_KEY = 'cheshire_cat_user_session';
const CONVERSATIONS_KEY = 'cheshire_cat_conversations';
const MAX_SAVED_CONVERSATIONS = parseInt(process.env.NEXT_PUBLIC_MAX_SAVED_CONVERSATIONS || '10', 10);
const ENABLE_CONVERSATION_SAVE = process.env.NEXT_PUBLIC_ENABLE_CONVERSATION_SAVE === 'true';

/**
 * Ottiene la sessione utente corrente dal localStorage
 */
export function getCurrentUserSession(): UserSession | null {
  try {
    if (typeof window === 'undefined') return null;
    
    const sessionData = localStorage.getItem(USER_SESSION_KEY);
    if (!sessionData) return null;
    
    return JSON.parse(sessionData);
  } catch (error) {
    console.error('Error retrieving user session:', error);
    return null;
  }
}

/**
 * Crea o aggiorna la sessione utente
 */
export function createOrUpdateUserSession(username?: string): UserSession {
  try {
    if (typeof window === 'undefined') {
      // Fallback per il rendering lato server
      return {
        userId: 'temp-user',
        sessionId: 'temp-session',
        username: username || 'Temp User',
        createdAt: Date.now(),
        lastActivity: Date.now()
      };
    }
    
    const currentSession = getCurrentUserSession();
    
    // Se esiste una sessione, aggiorna solo alcuni campi
    if (currentSession) {
      const updatedSession = {
        ...currentSession,
        sessionId: uuidv4(), // Nuova sessione
        username: username || currentSession.username,
        lastActivity: Date.now()
      };
      
      localStorage.setItem(USER_SESSION_KEY, JSON.stringify(updatedSession));
      return updatedSession;
    }
    
    // Altrimenti crea una nuova sessione
    const newSession: UserSession = {
      userId: uuidv4(),
      sessionId: uuidv4(),
      username: username || 'Utente',
      createdAt: Date.now(),
      lastActivity: Date.now()
    };
    
    localStorage.setItem(USER_SESSION_KEY, JSON.stringify(newSession));
    return newSession;
  } catch (error) {
    console.error('Error creating/updating user session:', error);
    
    // Fallback in caso di errore
    return {
      userId: `fallback-${Date.now()}`,
      sessionId: `fallback-${Date.now()}`,
      username: username || 'Utente',
      createdAt: Date.now(),
      lastActivity: Date.now()
    };
  }
}

/**
 * Aggiorna il nome utente nella sessione
 */
export function updateUsername(username: string): UserSession | null {
  try {
    const currentSession = getCurrentUserSession();
    if (!currentSession) return null;
    
    const updatedSession = {
      ...currentSession,
      username
    };
    
    localStorage.setItem(USER_SESSION_KEY, JSON.stringify(updatedSession));
    return updatedSession;
  } catch (error) {
    console.error('Error updating username:', error);
    return null;
  }
}

/**
 * Aggiorna il timestamp dell'ultima attività
 */
export function updateLastActivity(): UserSession | null {
  try {
    const currentSession = getCurrentUserSession();
    if (!currentSession) return null;
    
    const updatedSession = {
      ...currentSession,
      lastActivity: Date.now()
    };
    
    localStorage.setItem(USER_SESSION_KEY, JSON.stringify(updatedSession));
    return updatedSession;
  } catch (error) {
    console.error('Error updating last activity:', error);
    return null;
  }
}

/**
 * Cancella la sessione corrente
 */
export function clearCurrentSession(): boolean {
  try {
    if (typeof window === 'undefined') return false;
    
    localStorage.removeItem(USER_SESSION_KEY);
    return true;
  } catch (error) {
    console.error('Error clearing session:', error);
    return false;
  }
}

/**
 * Salva una conversazione nel localStorage
 */
export function saveConversation(conversation: ConversationData): boolean {
  if (!ENABLE_CONVERSATION_SAVE || typeof window === 'undefined') {
    return false;
  }
  
  try {
    // Recupera le conversazioni esistenti
    let conversations: ConversationData[] = [];
    const savedData = localStorage.getItem(CONVERSATIONS_KEY);
    
    if (savedData) {
      conversations = JSON.parse(savedData);
    }
    
    // Controlla se la conversazione esiste già
    const existingIndex = conversations.findIndex(c => c.id === conversation.id);
    
    if (existingIndex !== -1) {
      // Aggiorna la conversazione esistente
      conversations[existingIndex] = {
        ...conversation,
        updatedAt: Date.now()
      };
    } else {
      // Aggiungi una nuova conversazione
      conversations.push(conversation);
    }
    
    // Limita il numero di conversazioni salvate
    if (conversations.length > MAX_SAVED_CONVERSATIONS) {
      // Ordina per data di aggiornamento in modo che le più vecchie siano per prime
      conversations.sort((a, b) => a.updatedAt - b.updatedAt);
      // Rimuovi le conversazioni in eccesso
      conversations = conversations.slice(conversations.length - MAX_SAVED_CONVERSATIONS);
    }
    
    // Salva le conversazioni aggiornate
    localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));
    return true;
  } catch (error) {
    console.error('Error saving conversation:', error);
    return false;
  }
}

/**
 * Recupera tutte le conversazioni salvate
 */
export function getSavedConversations(): ConversationData[] {
  if (typeof window === 'undefined') {
    return [];
  }
  
  try {
    const savedData = localStorage.getItem(CONVERSATIONS_KEY);
    
    if (!savedData) {
      return [];
    }
    
    const conversations: ConversationData[] = JSON.parse(savedData);
    
    // Ordina per data di aggiornamento (più recenti prima)
    return conversations.sort((a, b) => b.updatedAt - a.updatedAt);
  } catch (error) {
    console.error('Error retrieving saved conversations:', error);
    return [];
  }
}

/**
 * Estrae un titolo dalla conversazione
 * Usa il primo messaggio dell'utente come base
 */
export function extractConversationTitle(messages: any[]): string {
  // Trova il primo messaggio dell'utente
  const firstUserMessage = messages.find(m => m.role === 'human');
  
  if (!firstUserMessage || !firstUserMessage.content) {
    return 'Nuova conversazione';
  }
  
  // Limita il titolo a 50 caratteri
  const content = firstUserMessage.content.trim();
  if (content.length <= 50) {
    return content;
  }
  
  // Tronca il titolo e aggiungi "..."
  return `${content.substring(0, 47)}...`;
}