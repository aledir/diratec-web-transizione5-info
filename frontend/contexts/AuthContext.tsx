// contexts/AuthContext.tsx
"use client"
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  authToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  autoLogin: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Effetto di inizializzazione - verifica se esiste un token salvato
  useEffect(() => {
    const checkToken = async () => {
      setIsLoading(true);
      try {
        // Controlla prima se c'è un token nel localStorage
        const savedToken = localStorage.getItem('auth_token');
        
        if (savedToken) {
          console.log('Token trovato nel localStorage, verifica validità...');
          // Valida il token esistente per verificare che sia ancora valido
          try {
            const isValid = await validateToken(savedToken);
            if (isValid) {
              console.log('Token salvato validato con successo');
              setAuthToken(savedToken);
              setIsAuthenticated(true);
            } else {
              console.log('Token salvato non valido, rimosso');
              localStorage.removeItem('auth_token');
              // Tenta auto-login con l'API key
              await autoLogin();
            }
          } catch (error) {
            console.error('Errore nella validazione del token:', error);
            if (error instanceof Response && error.status === 404) {
              console.log('Endpoint di validazione non disponibile, consideriamo il token valido');
              setAuthToken(savedToken);
              setIsAuthenticated(true);
            } else {
              localStorage.removeItem('auth_token');
              // Tenta auto-login se la validazione fallisce
              await autoLogin();
            }
          }
        } else {
          // Se non c'è token salvato, tenta l'auto-login
          await autoLogin();
        }
      } catch (err) {
        console.error('Errore durante l\'inizializzazione dell\'autenticazione:', err);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkToken();
  }, []);
  
  // Validate token function (verifica con un endpoint sicuro)
  const validateToken = async (token: string): Promise<boolean> => {
    try {
      // Utilizziamo l'API route interna per validare il token
      const response = await fetch('/api/validate-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });
      
      // Gestione errore 404 (endpoint non trovato)
      if (response.status === 404) {
        console.warn('Endpoint validate-token non trovato');
        throw response; // Lancia la risposta per gestirla nel catch
      }
      
      if (!response.ok) {
        console.error(`Errore nella validazione (${response.status}): ${await response.text()}`);
        return false;
      }
      
      const data = await response.json();
      return data.valid === true;
    } catch (error) {
      // Rilanciamo l'errore per gestirlo altrove
      throw error;
    }
  };
  
  // Auto-login using API key (senza credenziali utente)
  const autoLogin = async (): Promise<boolean> => {
    try {
      console.log('Tentativo di auto-login...');
      setIsLoading(true);
      
      // Usa l'API route interna che utilizza CCAT_API_KEY_WS dal server
      const response = await fetch('/api/chat-token');
      
      if (!response.ok) {
        console.error('Errore nell\'auto-login:', await response.text());
        return false;
      }
      
      const data = await response.json();
      
      if (data.token) {
        // Salva e imposta il token ricevuto
        localStorage.setItem('auth_token', data.token);
        setAuthToken(data.token);
        setIsAuthenticated(true);
        console.log('Auto-login completato con successo');
        return true;
      } else {
        console.error('Token non ricevuto nell\'auto-login:', data);
        return false;
      }
    } catch (error) {
      console.error('Errore durante l\'auto-login:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };
  
  const login = async (username: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    
    try {
      // Utilizziamo l'API route interna per proteggere le credenziali
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username,
          password
        })
      });
      
      if (!response.ok) {
        throw new Error('Errore di autenticazione');
      }
      
      const data = await response.json();
      
      // Verifica che ci sia un token nella risposta
      const token = data.token || data.access_token;
      
      if (!token) {
        throw new Error('Token non trovato nella risposta');
      }
      
      // Salva il token in localStorage
      localStorage.setItem('auth_token', token);
      setAuthToken(token);
      setIsAuthenticated(true);
      
      return true;
    } catch (error) {
      console.error('Errore di login:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };
  
  const logout = () => {
    localStorage.removeItem('auth_token');
    setAuthToken(null);
    setIsAuthenticated(false);
  };
  
  return (
    <AuthContext.Provider value={{ 
      authToken, 
      isAuthenticated, 
      isLoading,
      login, 
      logout,
      autoLogin
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext deve essere usato all\'interno di un AuthProvider');
  }
  return context;
}