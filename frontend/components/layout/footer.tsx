// components/layout/footer.tsx - Versione con Modal Intelligenti
"use client"
import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useLegalModalContext } from '@/contexts/legal-modal-context';

export default function Footer() {
  const pathname = usePathname();
  const { openModal } = useLegalModalContext();
  
  // Determina se siamo sulla homepage o su pagine di contenuto
  const isHomepage = pathname === '/';
  const isContentPage = pathname.includes('/docs') || pathname.includes('/chi-siamo') || pathname.includes('/certificazioni');
  
  // Logica intelligente per link legali
  const handleLegalClick = (type: 'termini-uso' | 'privacy-policy' | 'cookie-policy', e: React.MouseEvent) => {
    // Su homepage e pagine di contenuto, usa modal per UX fluida
    if (isHomepage || isContentPage) {
      e.preventDefault();
      openModal(type);
    }
    // Su altre pagine (es. già su pagine legali), lascia il comportamento normale del Link
  };

  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          
          {/* Colonna 1 - Transizione 5.0 e DIRATEC */}
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <a 
                href="/" 
                className="hover:opacity-80 transition-opacity"
              >
                <Image
                  src="/logos/transizione5-logo.svg"
                  alt="Transizione 5.0"
                  width={51}
                  height={60}
                  className="h-12 w-auto"
                />
              </a>
              <div>
                <h3 className="text-lg font-medium text-emerald-400">Transizione 5.0</h3>
                <div className="text-xs text-gray-400">powered by DIRATEC SRL</div>
              </div>
            </div>
            
            <div className="space-y-1">
              <h3 className="text-lg font-medium text-white mb-3">DIRATEC S.R.L.</h3>
              <div className="text-gray-400 text-sm space-y-1">
                <p>Via Brescia 108 G/H – 25018 Montichiari (BS)</p>
                <p>Cod. Fisc. Iscrizione CCIAA e P. IVA 04274200981</p>
                <p>Numero REA: BS - 601891</p>
                <p>Codice SDI: W7YVJK9</p>
                <p>Capitale sociale: € 10.000,00 i.v.</p>
              </div>
            </div>
          </div>
          
          {/* Colonna 2 - Fonti Ufficiali */}
          <div>
            <h3 className="text-lg font-medium mb-4">Fonti Ufficiali</h3>
            <ul className="space-y-3 text-gray-400 text-sm">
              <li>
                <a 
                  href="https://www.gse.it/servizi-per-te/attuazione-misure-pnrr/transizione-5-0" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white flex items-center group"
                >
                  <svg className="h-4 w-4 mr-2 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  <span className="group-hover:underline">Portale GSE Ufficiale</span>
                </a>
              </li>
              <li>
                <a 
                  href="https://www.mimit.gov.it/it/incentivi/piano-transizione-5-0" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white flex items-center group"
                >
                  <svg className="h-4 w-4 mr-2 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  <span className="group-hover:underline">MIMIT - Ministero</span>
                </a>
              </li>
              <li>
                <Link href="/docs" className="hover:text-white flex items-center group">
                  <svg className="h-4 w-4 mr-2 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="group-hover:underline">Documenti Normativi</span>
                </Link>
              </li>
            </ul>
            
            {/* Assistente AI */}
            <div className="mt-6 pt-4 border-t border-gray-700">
              <h4 className="text-sm font-medium text-gray-300 mb-2">Assistente AI</h4>
              <p className="text-sm text-gray-400">
                Assistente virtuale specializzato per la Transizione 5.0, sviluppato e offerto da DIRATEC SRL.
              </p>
            </div>
          </div>
          
          {/* Colonna 3 - Contatti */}
          <div>
            <h3 className="text-lg font-medium mb-4">Contatti</h3>
            <ul className="space-y-3 text-gray-400 text-sm">
              <li>
                <a href="mailto:info@diratec.it" className="hover:text-white flex items-center group">
                  <svg className="h-4 w-4 mr-2 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span className="group-hover:underline">info@diratec.it</span>
                </a>
              </li>
              <li>
                <a href="tel:+390308088065" className="hover:text-white flex items-center group">
                  <svg className="h-4 w-4 mr-2 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <span className="group-hover:underline">+39 030 808 8065</span>
                </a>
              </li>
            </ul>
            
            {/* Altri servizi */}
            <div className="mt-6 pt-4 border-t border-gray-700">
              <h4 className="text-sm font-medium text-gray-300 mb-3">Altri nostri servizi</h4>
              <div className="space-y-2">
                <div>
                  <a href="https://www.diratec.it" target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:text-emerald-300 text-sm font-medium">
                    DIRATEC - www.diratec.it
                  </a>
                  <p className="text-sm text-gray-500 mt-1">L'ingegneria al servizio delle imprese</p>
                </div>
                <div>
                  <a href="https://www.rocket4.it" target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:text-emerald-300 text-sm font-medium">
                    ROCKET4 - www.rocket4.it
                  </a>
                  <p className="text-sm text-gray-500 mt-1">L'integrazione 4.0 semplice e flessibile</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Footer bottom - VERSIONE CON MODAL INTELLIGENTI */}
        <div className="border-t border-gray-700 mt-10 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-gray-400 text-sm">
              © {new Date().getFullYear()} DIRATEC SRL. Tutti i diritti riservati.
              <br className="md:hidden" />
              <span className="md:ml-2">Servizio di consulenza per la Transizione 5.0</span>
            </div>
            <div className="flex space-x-4 text-sm">
              {/* Link intelligenti che decidono modal vs pagina */}
              <Link 
                href="/termini-uso" 
                onClick={(e) => handleLegalClick('termini-uso', e)}
                className="text-gray-400 hover:text-white"
              >
                Termini d'Uso
              </Link>
              <span className="text-gray-600">•</span>
              <Link 
                href="/privacy-policy" 
                onClick={(e) => handleLegalClick('privacy-policy', e)}
                className="text-gray-400 hover:text-white"
              >
                Privacy Policy
              </Link>
              <span className="text-gray-600">•</span>
              <Link 
                href="/cookie-policy" 
                onClick={(e) => handleLegalClick('cookie-policy', e)}
                className="text-gray-400 hover:text-white"
              >
                Cookie Policy
              </Link>
              <span className="text-gray-600">•</span>
              <button 
                onClick={() => {
                  if (typeof window !== 'undefined' && (window as any).klaro) {
                    (window as any).klaro.show();
                  }
                }}
                className="text-gray-400 hover:text-white cursor-pointer"
              >
                Preferenze Cookie
              </button>
            </div>
          </div>

          {/* Indicatore modalità (solo in development) */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-4 text-center">
              <span className="text-xs text-gray-500">
                {isHomepage || isContentPage ? '🪟 Modal Mode' : '📄 Page Mode'} | Current: {pathname}
              </span>
            </div>
          )}
        </div>
      </div>
    </footer>
  );
}