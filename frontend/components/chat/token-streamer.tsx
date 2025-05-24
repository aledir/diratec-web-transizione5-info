"use client"
import { useEffect, useRef } from 'react';
import { useAuthContext } from '../../contexts/auth-context';

interface TokenStreamerProps {
  onToken: (token: string) => void;
  onComplete: () => void;
  onError: (error: string) => void;
  userMessage: string;
  sessionId: string;
}

export default function TokenStreamer({ 
  onToken, 
  onComplete, 
  onError, 
  userMessage,
  sessionId
}: TokenStreamerProps) {
  const { authToken } = useAuthContext();
  const eventSourceRef = useRef<EventSource | null>(null);
  const hasStartedRef = useRef<boolean>(false);
  
  useEffect(() => {
    // Evitiamo di avviare più volte
    if (hasStartedRef.current || !userMessage || !authToken || !sessionId) return;
    
    hasStartedRef.current = true;
    console.log('[TokenStreamer] Avvio streaming risposta...');
    
    const apiUrl = '/api/chat-stream';
    const queryParams = new URLSearchParams({
      message: userMessage,
      sessionId: sessionId
    });
    
    try {
      // Creiamo una connessione SSE
      const eventSource = new EventSource(`${apiUrl}?${queryParams.toString()}`);
      eventSourceRef.current = eventSource;
      
      // Gestione degli eventi
      eventSource.onopen = () => {
        console.log('[TokenStreamer] Connessione streaming aperta');
      };
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.token) {
            // Streaming di token
            onToken(data.token);
          } else if (data.event === 'complete') {
            // Completamento risposta
            console.log('[TokenStreamer] Streaming completato');
            onComplete();
            eventSource.close();
          }
        } catch (err) {
          console.error('[TokenStreamer] Errore nel parsing dei dati:', event.data, err);
          onError('Errore nel format dei dati ricevuti');
          eventSource.close();
        }
      };
      
      eventSource.onerror = (err) => {
        console.error('[TokenStreamer] Errore nella connessione SSE:', err);
        onError('Errore nella connessione al server. Riprova più tardi.');
        eventSource.close();
      };
      
    } catch (error) {
      console.error('[TokenStreamer] Errore nell\'inizializzazione dello streaming:', error);
      onError(`Errore di connessione: ${error instanceof Error ? error.message : 'Errore sconosciuto'}`);
    }
    
    // Pulizia alla dismissione
    return () => {
      if (eventSourceRef.current) {
        console.log('[TokenStreamer] Chiusura connessione streaming');
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      hasStartedRef.current = false;
    };
  }, [userMessage, authToken, sessionId, onToken, onComplete, onError]);
  
  // Questo componente non renderizza nulla visibile
  return null;
} 