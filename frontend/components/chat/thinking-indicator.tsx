// components/chat/thinking-indicator.tsx - IMPORT CORRETTI
import React, { useState, useEffect } from 'react';
import styles from './chat.module.css';
import useSharedConfig from '../../hooks/useSharedConfig';

// Icone disponibili - scegli quella che preferisci
const ICONS = {
  // 1. Icona Robot
  ROBOT: (
    <svg className={styles.thinkingIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM17 13C16.45 13 16 12.55 16 12C16 11.45 16.45 11 17 11C17.55 11 18 11.45 18 12C18 12.55 17.55 13 17 13ZM7 13C6.45 13 6 12.55 6 12C6 11.45 6.45 11 7 11C7.55 11 8 11.45 8 12C8 12.55 7.55 13 7 13ZM7 17H17V14.5C17 13.12 15.88 12 14.5 12H9.5C8.12 12 7 13.12 7 14.5V17Z" fill="currentColor"/>
    </svg>
  ),
  
  // 2. Icona Chat / Assistente
  CHAT: (
    <svg className={styles.thinkingIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM8 9H16C16.55 9 17 9.45 17 10C17 10.55 16.55 11 16 11H8C7.45 11 7 10.55 7 10C7 9.45 7.45 9 8 9ZM13 14H8C7.45 14 7 13.55 7 13C7 12.45 7.45 12 8 12H13C13.55 12 14 12.45 14 13C14 13.55 13.55 14 13 14ZM16 8H8C7.45 8 7 7.55 7 7C7 6.45 7.45 6 8 6H16C16.55 6 17 6.45 17 7C17 7.55 16.55 8 16 8Z" fill="currentColor"/>
    </svg>
  ),
  
  // 3. Icona Smart Assistant / Utente
  USER: (
    <svg className={styles.thinkingIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
    </svg>
  ),
  
  // 4. Icona Foglia (per il tema verde/sostenibilità)
  LEAF: (
    <svg className={styles.thinkingIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M6.05 8.05C4.93 9.17 4.24 10.62 4.05 12.27L9.13 17.35C10.78 17.16 12.23 16.47 13.34 15.34C17.46 11.23 12.81 4.66 8.59 4.06C7.43 3.9 6.25 4.16 5.3 5.1C5.29 5.11 5.29 5.12 5.28 5.13L15.59 15.45L13.5 17.55L7.44 11.5L6.05 8.05Z" fill="currentColor"/>
    </svg>
  ),
  
  // 5. Icona Semplice Cerchio con Freccia (tipo messaggio)
  CIRCLE_ARROW: (
    <svg className={styles.thinkingIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 18.5L6 12.5H9V9H15V12.5H18L12 18.5Z" fill="currentColor"/>
    </svg>
  ),
  
  // 6. Icona Lampadina (suggerimenti/idee)
  LIGHTBULB: (
    <svg className={styles.thinkingIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 19C11.45 19 11 18.55 11 18H13C13 18.55 12.55 19 12 19ZM15 16.59L14.59 17H9.41L9 16.59V16H15V16.59ZM15 15H9C9 11.86 7.73 10.85 7.73 8.71C7.73 6.71 9.7 5 12 5C14.3 5 16.27 6.71 16.27 8.71C16.27 10.85 15 11.86 15 15Z" fill="currentColor"/>
    </svg>
  ),
  
  // 7. Icona Sostenibilità/Eco (smiley)
  ECO: (
    <svg className={styles.thinkingIcon} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM15.5 8C16.33 8 17 8.67 17 9.5C17 10.33 16.33 11 15.5 11C14.67 11 14 10.33 14 9.5C14 8.67 14.67 8 15.5 8ZM8.5 8C9.33 8 10 8.67 10 9.5C10 10.33 9.33 11 8.5 11C7.67 11 7 10.33 7 9.5C7 8.67 7.67 8 8.5 8ZM12 17.5C9.67 17.5 7.69 16.04 6.89 14H17.11C16.31 16.04 14.33 17.5 12 17.5Z" fill="currentColor"/>
    </svg>
  )
};

// IMPORTANTE: Scegli qui l'icona che preferisci
// Opzioni: ROBOT, CHAT, USER, LEAF, CIRCLE_ARROW, LIGHTBULB, ECO
const SELECTED_ICON = ICONS.ROBOT;

// Componente principale
const ThinkingIndicator: React.FC = () => {
  const { config } = useSharedConfig();
  
  // Prendiamo il nome dell'assistente dalla configurazione, con fallback
  const assistantName = config?.assistant?.displayName || "Assistente";
  
  // Messaggi migliorati per Transizione 5.0
  const thinkingMessages = [
    "Analisi dei requisiti in corso...",
    "Valutazione degli incentivi applicabili...",
    "Consultazione normative Transizione 5.0...",
    "Personalizzazione della risposta...",
    "Elaborazione dati specifici del settore..."
  ];

  const [messageIndex, setMessageIndex] = useState(0);
  const [progressWidth, setProgressWidth] = useState(0);
  
  // Rotazione messaggi (ogni 2.5 secondi)
  useEffect(() => {
    const messageInterval = setInterval(() => {
      setMessageIndex((prevIndex) => (prevIndex + 1) % thinkingMessages.length);
    }, 2500);
    
    return () => clearInterval(messageInterval);
  }, []);
  
  // Progresso animato
  useEffect(() => {
    setProgressWidth(0);
    
    const progressInterval = setInterval(() => {
      setProgressWidth(prev => {
        if (prev < 98) {
          return prev + Math.max(1, (98 - prev) / 12);
        }
        return prev;
      });
    }, 100);
    
    return () => clearInterval(progressInterval);
  }, [messageIndex]);

  return (
    <div className={styles.thinkingIndicatorEnhanced}>
      <div className={styles.thinkingContent}>
        <div className={styles.thinkingIconContainer}>
          {/* Usa l'icona selezionata */}
          {SELECTED_ICON}
        </div>
        <div className={styles.thinkingMessageContainer}>
          <div className={styles.assistantNameLabel}>{assistantName}</div>
          <div className={styles.thinkingMessage}>
            {thinkingMessages[messageIndex]}
          </div>
        </div>
      </div>
      
      {/* Barra di progresso */}
      <div className={styles.thinkingProgressBar}>
        <div 
          className={styles.thinkingProgressFill} 
          style={{ width: `${progressWidth}%` }}
        ></div>
      </div>
      
      {/* Indicatore pulsante */}
      <div className={styles.thinkingPulsingDots}>
        <div className={styles.thinkingPulsingDot}></div>
        <div className={styles.thinkingPulsingDot}></div>
        <div className={styles.thinkingPulsingDot}></div>
      </div>
    </div>
  );
};

export default ThinkingIndicator;