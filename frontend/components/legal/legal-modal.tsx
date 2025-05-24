// components/legal/legal-modal.tsx
import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import LegalContent from './legal-content';

interface LegalModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'termini-uso' | 'privacy-policy' | 'cookie-policy';
  content: string;
  title: string;
  lastUpdated: string;
}

export default function LegalModal({ 
  isOpen, 
  onClose, 
  type, 
  content, 
  title, 
  lastUpdated 
}: LegalModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
    >
      {/* Backdrop */}
      <div 
        className="absolute inset-0" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="p-6">
          <LegalContent
            title={title}
            content={content}
            lastUpdated={lastUpdated}
            mode="modal"
            onClose={onClose}
          />
        </div>
      </div>
    </div>,
    document.body
  );
}