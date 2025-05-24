'use client';
import React, { createContext, useContext, ReactNode } from 'react';
import { useLegalModal, LegalType } from '@/hooks/use-legal-modal';
import LegalModal from '@/components/legal/legal-modal';

interface LegalModalContextType {
  openModal: (type: LegalType) => void;
  closeModal: () => void;
}

const LegalModalContext = createContext<LegalModalContextType | undefined>(undefined);

export function LegalModalProvider({ children }: { children: ReactNode }) {
  const {
    isOpen,
    type,
    content,
    title,
    lastUpdated,
    openModal,
    closeModal
  } = useLegalModal();

  return (
    <LegalModalContext.Provider value={{ openModal, closeModal }}>
      {children}
      {type && (
        <LegalModal
          isOpen={isOpen}
          onClose={closeModal}
          type={type}
          content={content}
          title={title}
          lastUpdated={lastUpdated}
        />
      )}
    </LegalModalContext.Provider>
  );
}

export function useLegalModalContext() {
  const context = useContext(LegalModalContext);
  if (context === undefined) {
    throw new Error('useLegalModalContext must be used within a LegalModalProvider');
  }
  return context;
}