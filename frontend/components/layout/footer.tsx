// components/layout/Footer.tsx
import React from 'react';
import Link from 'next/link';

interface FooterProps {
  // Nessuna prop necessaria
}

export default function Footer({}: FooterProps) {
  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-lg font-medium mb-4">DIRATEC SRL</h3>
            <p className="text-gray-400 text-sm mb-4">
              Specialisti in consulenza per incentivi alle imprese e crediti d'imposta per l'innovazione tecnologica e sostenibile.
            </p>
            <div className="text-gray-400 text-sm">
              <p>Via Brescia 108 G/H</p>
              <p>25018 Montichiari (BS)</p>
              <p className="mt-2">P.IVA 04274200981</p>
              <p>REA BS-601891</p>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-4">Link utili</h3>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>
                <a 
                  href="https://www.gse.it/servizi-per-te/attuazione-misure-pnrr/transizione-5-0" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white"
                >
                  Portale GSE
                </a>
              </li>
              <li>
                <a 
                  href="https://www.mimit.gov.it/index.php/it/incentivi/transizione-5-0" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white"
                >
                  MIMIT Transizione 5.0
                </a>
              </li>
              <li><Link href="/docs" className="hover:text-white">Documenti ufficiali</Link></li>
              <li><Link href="#faq" className="hover:text-white">Domande frequenti</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-4">Contatti</h3>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li className="flex items-start">
                <svg className="h-5 w-5 text-gray-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <a href="mailto:info@diratec.it" className="hover:text-white">info@diratec.it</a>
              </li>
              <li className="flex items-start">
                <svg className="h-5 w-5 text-gray-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <a href="tel:+390308088065" className="hover:text-white">+39 030 808 8065</a>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-4">Newsletter</h3>
            <p className="text-gray-400 text-sm mb-4">
              Iscriviti per ricevere aggiornamenti sulla Transizione 5.0
            </p>
            <form className="flex">
              <input 
                type="email" 
                placeholder="La tua email" 
                className="flex-1 py-2 px-3 rounded-l-lg text-gray-900 text-sm"
              />
              <button 
                type="submit"
                className="bg-emerald-600 hover:bg-emerald-700 text-white py-2 px-4 rounded-r-lg text-sm transition duration-150 ease-in-out"
              >
                Iscriviti
              </button>
            </form>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="text-gray-400 text-sm">
            © {new Date().getFullYear()} DIRATEC SRL. Tutti i diritti riservati.
          </div>
          <div className="flex space-x-4 mt-4 md:mt-0">
            <a href="#" className="text-gray-400 hover:text-white">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" />
              </svg>
            </a>
            <a href="#" className="text-gray-400 hover:text-white">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}