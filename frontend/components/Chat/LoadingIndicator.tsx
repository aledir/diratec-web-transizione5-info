// frontend/components/Chat/LoadingIndicator.tsx
import React from 'react';
import styles from './Chat.module.css';
import Image from 'next/image';

interface LoadingIndicatorProps {
  message?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ message = "Sto elaborando la risposta..." }) => {
  // Utilizzo dell'icona di caricamento SVG animata
  return (
    <div className={styles.loadingIndicator}>
      <Image src="/icons/loading.svg" alt="Loading..." width={24} height={24} priority />
      <span className={styles.loadingText}>{message}</span>
    </div>
  );
};

export default LoadingIndicator;