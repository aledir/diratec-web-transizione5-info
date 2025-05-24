// frontend/components/analytics/KlaroWrapper.tsx
"use client"
import { useEffect } from 'react';
import { klaroConfig } from '@/lib/klaro-config';

export default function KlaroWrapper() {
  useEffect(() => {
    // Imposta la configurazione globale
    window.klaroConfig = klaroConfig;
    
    // Carica Klaro dinamicamente
    const script = document.createElement('script');
    script.src = 'https://cdn.kiprotect.com/klaro/v0.7/klaro.js';
    script.defer = true;
    script.onload = () => {
      // Klaro è stato caricato
      console.log('Klaro caricato con successo');
    };
    
    document.head.appendChild(script);
    
    // Cleanup
    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);

  return (
    <>
      {/* Elemento dove Klaro inserirà il banner */}
      <div id="klaro"></div>
      
      {/* CSS personalizzato per Klaro */}
      <style jsx global>{`
        /* Personalizzazione banner Klaro per Transizione 5.0 */
        .klaro .cookie-notice {
          background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
          border-top: 3px solid #10b981 !important;
          color: white !important;
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        .klaro .cookie-notice .cn-body {
          color: #f3f4f6 !important;
        }
        
        .klaro .cookie-notice .cn-buttons .cm-btn {
          background: #ffffff !important;
          color: #059669 !important;
          border: 2px solid #ffffff !important;
          border-radius: 6px !important;
          font-weight: 600 !important;
          transition: all 0.2s ease !important;
        }
        
        .klaro .cookie-notice .cn-buttons .cm-btn:hover {
          background: #f3f4f6 !important;
          transform: translateY(-1px) !important;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        }
        
        .klaro .cookie-notice .cn-buttons .cm-btn.cm-btn-success {
          background: #ffffff !important;
          color: #059669 !important;
        }
        
        .klaro .cookie-notice .cn-buttons .cm-btn.cm-btn-info {
          background: transparent !important;
          color: #ffffff !important;
          border-color: #ffffff !important;
        }
        
        .klaro .cookie-notice .cn-buttons .cm-btn.cm-btn-info:hover {
          background: rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Modal delle preferenze */
        .klaro .cookie-modal {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        .klaro .cookie-modal .cm-header {
          border-bottom: 2px solid #e5e7eb !important;
        }
        
        .klaro .cookie-modal .cm-header h1 {
          color: #059669 !important;
          font-weight: 700 !important;
        }
        
        .klaro .cookie-modal .cm-footer .cm-btn {
          border-radius: 6px !important;
          font-weight: 600 !important;
          transition: all 0.2s ease !important;
        }
        
        .klaro .cookie-modal .cm-footer .cm-btn.cm-btn-success {
          background: #059669 !important;
          border-color: #059669 !important;
        }
        
        .klaro .cookie-modal .cm-footer .cm-btn.cm-btn-success:hover {
          background: #047857 !important;
          border-color: #047857 !important;
        }
        
        /* Toggle switches */
        .klaro .cookie-modal .cm-list-item .cm-list-input input[type="checkbox"]:checked + .slider {
          background-color: #059669 !important;
        }
        
        /* Link privacy policy */
        .klaro .cm-link {
          color: #059669 !important;
          font-weight: 600 !important;
        }
        
        .klaro .cm-link:hover {
          color: #047857 !important;
          text-decoration: underline !important;
        }
      `}</style>
    </>
  );
}