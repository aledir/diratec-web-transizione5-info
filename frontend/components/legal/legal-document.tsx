// components/legal/legal-document.tsx (aggiornato per pagine)
import React from 'react';
import Link from 'next/link';
import LegalContent from './legal-content';

interface LegalDocumentProps {
  title: string;
  content: string;
  lastUpdated: string;
}

export default function LegalDocument({ title, content, lastUpdated }: LegalDocumentProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header con breadcrumb */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <nav className="flex" aria-label="Breadcrumb">
            <ol className="flex items-center space-x-4">
              <li>
                <Link href="/" className="text-gray-500 hover:text-gray-700">
                  Home
                </Link>
              </li>
              <li>
                <svg className="flex-shrink-0 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
              </li>
              <li>
                <span className="text-gray-900 font-medium">{title}</span>
              </li>
            </ol>
          </nav>
        </div>
      </div>

      {/* Contenuto principale */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
            <div className="flex items-center text-sm text-gray-500">
              <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Ultimo aggiornamento: {lastUpdated}
            </div>
          </div>
          
          <LegalContent
            title={title}
            content={content}
            lastUpdated={lastUpdated}
            mode="page"
          />
          
          {/* Sezione contatti */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="bg-emerald-50 border-l-4 border-emerald-500 p-6 rounded-r-lg">
              <div className="flex items-start">
                <svg className="h-6 w-6 text-emerald-600 mt-1 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="text-lg font-medium text-emerald-800 mb-2">Hai domande?</h3>
                  <p className="text-emerald-700 mb-3">
                    Per chiarimenti sui presenti termini o per assistenza specifica sulla Transizione 5.0, contatta il nostro team.
                  </p>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center">
                      <svg className="h-4 w-4 text-emerald-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <a href="mailto:info@diratec.it" className="text-emerald-700 hover:text-emerald-800 underline">
                        info@diratec.it
                      </a>
                    </div>
                    <div className="flex items-center">
                      <svg className="h-4 w-4 text-emerald-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      <a href="tel:+390308088065" className="text-emerald-700 hover:text-emerald-800">
                        +39 030 808 8065
                      </a>
                    </div>
                    <div className="flex items-center">
                      <svg className="h-4 w-4 text-emerald-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      <a href="https://www.diratec.it" target="_blank" rel="noopener noreferrer" className="text-emerald-700 hover:text-emerald-800 underline">
                        www.diratec.it
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Pulsante per tornare alla homepage */}
          <div className="mt-8 text-center">
            <Link 
              href="/"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 transition-colors"
            >
              <svg className="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Torna alla Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}