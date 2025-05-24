// frontend/components/Chat/UserSessionManager.tsx
import React, { useState, useEffect } from 'react';
import { createOrUpdateUserSession, getCurrentUserSession, updateUsername, UserSession, clearCurrentSession } from '../../utils/session-manager';
import styles from './chat.module.css';

interface UserSessionManagerProps {
  onSessionUpdate: (session: UserSession) => void;
  onReset?: () => void;
}

const UserSessionManager: React.FC<UserSessionManagerProps> = ({ onSessionUpdate, onReset }) => {
  const [username, setUsername] = useState('');
  const [currentSession, setCurrentSession] = useState<UserSession | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  // Inizializza o carica la sessione utente
  useEffect(() => {
    const session = getCurrentUserSession() || createOrUpdateUserSession();
    setCurrentSession(session);
    setUsername(session.username || '');
    onSessionUpdate(session);
  }, [onSessionUpdate]);

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(e.target.value);
  };

  const handleUsernameSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (username.trim()) {
      const updatedSession = updateUsername(username.trim()) || createOrUpdateUserSession(username.trim());
      setCurrentSession(updatedSession);
      onSessionUpdate(updatedSession);
      setIsEditing(false);
    }
  };

  const startEditing = () => {
    setIsEditing(true);
    setShowMenu(false);
  };

  const toggleMenu = () => {
    setShowMenu(prev => !prev);
  };

  const handleResetSession = () => {
    if (window.confirm('Vuoi davvero iniziare una nuova sessione? La conversazione corrente verrà terminata.')) {
      clearCurrentSession();
      const newSession = createOrUpdateUserSession(currentSession?.username);
      setCurrentSession(newSession);
      onSessionUpdate(newSession);
      
      if (onReset) {
        onReset();
      }
    }
    setShowMenu(false);
  };

  return (
    <div className={styles.sessionManager}>
      <div className={styles.sessionLeft}>
        {isEditing ? (
          <form onSubmit={handleUsernameSubmit} className={styles.usernameForm}>
            <input
              type="text"
              value={username}
              onChange={handleUsernameChange}
              placeholder="Inserisci il tuo nome"
              className={styles.usernameInput}
              autoFocus
            />
            <button type="submit" className={styles.saveButton}>
              Salva
            </button>
          </form>
        ) : (
          <div className={styles.userInfo} onClick={startEditing}>
            <span className={styles.userIcon}>👤</span>
            <span className={styles.username}>
              {currentSession?.username || 'Utente Anonimo'}
            </span>
            <span className={styles.editIcon}>✏️</span>
          </div>
        )}
      </div>
      
      <div className={styles.sessionRight}>
        <div className={styles.sessionInfo}>
          <span className={styles.sessionLabel}>ID Sessione:</span>
          <span className={styles.sessionId}>{currentSession?.sessionId.substring(0, 8) || 'N/A'}</span>
        </div>
        
        <div className={styles.menuContainer}>
          <button className={styles.menuButton} onClick={toggleMenu}>
            ⋮
          </button>
          
          {showMenu && (
            <div className={styles.menuDropdown}>
              <button className={styles.menuItem} onClick={handleResetSession}>
                Nuova sessione
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserSessionManager;