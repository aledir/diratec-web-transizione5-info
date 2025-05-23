// frontend/hooks/useSharedConfig.ts
import { useState, useEffect } from 'react';

interface ConfigState {
  config: any | null;
  loading: boolean;
  error: string | null;
}

export default function useSharedConfig() {
  const [state, setState] = useState<ConfigState>({
    config: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    async function fetchConfig() {
      try {
        // Usa la nuova API route che hai creato
        const response = await fetch('/api/config');
        
        if (!response.ok) {
          throw new Error(`Errore ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        setState({
          config: data,
          loading: false,
          error: null
        });
      } catch (err) {
        console.error('Errore caricamento config:', err);
        setState({
          config: null,
          loading: false,
          error: err instanceof Error ? err.message : 'Errore sconosciuto'
        });
      }
    }
    
    fetchConfig();
  }, []);

  return state;
}