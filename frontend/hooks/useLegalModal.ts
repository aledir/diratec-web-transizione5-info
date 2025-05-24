import { useState, useCallback } from 'react';

export type LegalType = 'termini-uso' | 'privacy-policy' | 'cookie-policy';

interface LegalModalState {
  isOpen: boolean;
  type: LegalType | null;
  content: string;
  title: string;
  lastUpdated: string;
}

export function useLegalModal() {
  const [modalState, setModalState] = useState<LegalModalState>({
    isOpen: false,
    type: null,
    content: '',
    title: '',
    lastUpdated: ''
  });

  const openModal = useCallback(async (type: LegalType) => {
    try {
      // Carica il contenuto markdown
      const response = await fetch(`/legal/${type}.md`);
      const content = await response.text();
      
      // Definisci titolo e data
      const titles = {
        'termini-uso': 'Termini d\'uso',
        'privacy-policy': 'Privacy Policy',
        'cookie-policy': 'Cookie Policy'
      };

      setModalState({
        isOpen: true,
        type,
        content,
        title: titles[type],
        lastUpdated: '23 maggio 2025'
      });
    } catch (error) {
      console.error('Errore nel caricamento del documento legale:', error);
    }
  }, []);

  const closeModal = useCallback(() => {
    setModalState(prev => ({ ...prev, isOpen: false }));
  }, []);

  return {
    ...modalState,
    openModal,
    closeModal
  };
}