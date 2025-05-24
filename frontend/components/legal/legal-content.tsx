// components/legal/legal-content.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';

interface LegalContentProps {
  title: string;
  content: string;
  lastUpdated: string;
  mode?: 'page' | 'modal';
  onClose?: () => void;
}

export default function LegalContent({ 
  title, 
  content, 
  lastUpdated, 
  mode = 'page',
  onClose 
}: LegalContentProps) {
  const isModal = mode === 'modal';

  const markdownComponents = {
    h1: ({ children }: any) => (
      <h1 className={`${isModal ? 'text-xl' : 'text-2xl'} font-bold mt-6 mb-4 text-gray-900 border-b border-gray-200 pb-2`}>
        {children}
      </h1>
    ),
    h2: ({ children }: any) => (
      <h2 className={`${isModal ? 'text-lg' : 'text-xl'} font-bold mt-5 mb-3 text-gray-800`}>
        {children}
      </h2>
    ),
    h3: ({ children }: any) => (
      <h3 className={`${isModal ? 'text-base' : 'text-lg'} font-semibold mt-4 mb-2 text-gray-700`}>
        {children}
      </h3>
    ),
    p: ({ children }: any) => (
      <p className={`mb-3 text-gray-600 ${isModal ? 'text-sm' : ''} leading-relaxed`}>
        {children}
      </p>
    ),
    ul: ({ children }: any) => (
      <ul className={`list-disc ml-6 mb-3 space-y-1 ${isModal ? 'text-sm' : ''}`}>
        {children}
      </ul>
    ),
    ol: ({ children }: any) => (
      <ol className={`list-decimal ml-6 mb-3 space-y-1 ${isModal ? 'text-sm' : ''}`}>
        {children}
      </ol>
    ),
    li: ({ children }: any) => (
      <li className="text-gray-600">{children}</li>
    ),
    strong: ({ children }: any) => (
      <strong className="font-semibold text-gray-800">{children}</strong>
    ),
    a: ({ href, children }: any) => (
      <a 
        href={href} 
        className="text-emerald-600 hover:text-emerald-700 underline"
        target={href?.startsWith('http') ? '_blank' : '_self'}
        rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
      >
        {children}
      </a>
    ),
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-emerald-500 pl-4 py-2 my-3 bg-emerald-50 text-gray-700 italic">
        {children}
      </blockquote>
    ),
    code: ({ children }: any) => (
      <code className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm font-mono">
        {children}
      </code>
    ),
    hr: () => <hr className="my-6 border-gray-300" />
  };

  if (isModal) {
    return (
      <div className="max-h-[70vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 pb-4 mb-4 z-10">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-xl font-bold text-gray-900">{title}</h1>
              <div className="flex items-center text-xs text-gray-500 mt-1">
                <svg className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Ultimo aggiornamento: {lastUpdated}
              </div>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="ml-4 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>
        
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown components={markdownComponents}>
            {content}
          </ReactMarkdown>
        </div>

        {/* Footer contatti per modal */}
        <div className="mt-8 pt-6 border-t border-gray-200 bg-gray-50 -mx-6 px-6 pb-6">
          <div className="text-center">
            <h3 className="text-sm font-medium text-gray-800 mb-2">Hai domande?</h3>
            <div className="space-y-1 text-xs text-gray-600">
              <div>
                <a href="mailto:info@diratec.it" className="text-emerald-600 hover:text-emerald-700">
                  info@diratec.it
                </a>
              </div>
              <div>
                <a href="tel:+390308088065" className="text-emerald-600 hover:text-emerald-700">
                  +39 030 808 8065
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Rendering per pagina completa (esistente)
  return (
    <div className="prose prose-lg max-w-none">
      <ReactMarkdown components={markdownComponents}>
        {content}
      </ReactMarkdown>
    </div>
  );
}