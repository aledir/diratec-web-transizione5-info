// app/docs/page.tsx
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

// Tipo per i documenti
interface Document {
  id: string;
  path: string;
  titolo: string;
  categoria: string;
  tipo: string;
  data: string;
  stato: 'attivo' | 'obsoleto';
  descrizione?: string;
  tags?: string[];
}

export default function DocumentsPage() {
  // Stati
  const [documents, setDocuments] = useState<Document[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [types, setTypes] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('tutte');
  const [typeFilter, setTypeFilter] = useState<string>('tutti');
  const [statusFilter, setStatusFilter] = useState<string>('attivi');
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  // Effetto per caricare i documenti
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('https://api.transizione5.info/api/documents');
        
        if (!response.ok) {
          throw new Error(`Errore API (${response.status})`);
        }
        
        const data = await response.json();
        
        if (data.error) {
          setError(data.error);
        } else {
          setDocuments(data.files || []);
          
          // Estrai categorie uniche
          const uniqueCategories = Array.from(
            new Set(data.files.map((doc: Document) => doc.categoria))
          ).filter((category): category is string => typeof category === 'string');
          setCategories(uniqueCategories);
          
          // Estrai tipi unici
          const uniqueTypes = Array.from(
            new Set(data.files.map((doc: Document) => doc.tipo))
          ).filter((type): type is string => typeof type === 'string');
          setTypes(uniqueTypes);
          
          setError(null);
        }
      } catch (err) {
        setError('Impossibile recuperare i documenti. Riprova più tardi.');
        console.error('Errore nel recupero dei documenti:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocuments();
  }, []);
  
  // Filtra i documenti in base ai filtri attivi
  const filteredDocuments = documents.filter(doc => {
    const matchesCategory = categoryFilter === 'tutte' || doc.categoria === categoryFilter;
    const matchesType = typeFilter === 'tutti' || doc.tipo === typeFilter;
    const matchesStatus = statusFilter === 'tutti' || 
                         (statusFilter === 'attivi' && doc.stato === 'attivo') ||
                         (statusFilter === 'obsoleti' && doc.stato === 'obsoleto');
    const matchesSearch = !searchQuery || 
                          doc.titolo.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (doc.descrizione && doc.descrizione.toLowerCase().includes(searchQuery.toLowerCase())) ||
                          (doc.tags && doc.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())));
    
    return matchesCategory && matchesType && matchesStatus && matchesSearch;
  });
  
  // Formatta la data
  const formatDate = (dateString: string) => {
    try {
      const [year, month, day] = dateString.split('-');
      return `${day}/${month}/${year}`;
    } catch (e) {
      return dateString;
    }
  };
  
  // Ottieni l'URL completo di un documento
  const getDocumentUrl = (path: string) => {
    return `https://api.transizione5.info/static/documents/${path}`;
  };
  
  // Ottieni l'icona del tipo di documento
  const getDocumentTypeIcon = (tipo: string) => {
    switch (tipo.toLowerCase()) {
      case 'normativa':
        return (
          <svg className="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
        );
      case 'circolare':
        return (
          <svg className="h-5 w-5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'faq':
        return (
          <svg className="h-5 w-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'guida':
        return (
          <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        );
      case 'modello':
        return (
          <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      default:
        return (
          <svg className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-emerald-600">Documenti</h1>
            <span className="text-sm text-gray-500">Transizione 5.0</span>
          </div>
          <nav className="hidden md:flex space-x-6">
            <Link href="/" className="text-gray-600 hover:text-emerald-600">Home</Link>
            <Link href="/docs" className="text-gray-800 hover:text-emerald-600 font-medium">Documenti</Link>
            <Link href="/admin" className="text-gray-600 hover:text-emerald-600">Area Riservata</Link>
          </nav>
          <div className="md:hidden">
            <button className="p-2 rounded-md text-gray-600 hover:text-emerald-600 hover:bg-gray-100">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Documenti ufficiali Transizione 5.0</h2>
          <p className="text-lg text-gray-600">
            Consulta e scarica la documentazione ufficiale relativa al credito d'imposta Transizione 5.0:
            normative, circolari, guide e modelli.
          </p>
        </div>
        
        {/* Filtri */}
        <div className="bg-white p-4 rounded-lg shadow-md mb-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="lg:col-span-2">
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">Cerca</label>
              <input
                type="text"
                id="search"
                placeholder="Cerca per titolo o tag..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
              <select
                id="category"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="tutte">Tutte le categorie</option>
                {categories.map((category) => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
              <select
                id="type"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="tutti">Tutti i tipi</option>
                {types.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">Stato</label>
              <select
                id="status"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="attivi">Solo documenti in vigore</option>
                <option value="obsoleti">Solo documenti obsoleti</option>
                <option value="tutti">Tutti i documenti</option>
              </select>
            </div>
          </div>
        </div>
        
        {/* Lista documenti */}
        {isLoading ? (
          <div className="animate-pulse">
            <div className="h-10 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="p-6 bg-red-50 rounded-lg border border-red-200 text-red-800">
            <h3 className="font-medium text-lg mb-2">Errore</h3>
            <p>{error}</p>
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  Nessun documento trovato con i filtri selezionati.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredDocuments.map((doc) => (
              <div
                key={doc.id}
                className={`bg-white overflow-hidden shadow rounded-lg transition-all hover:shadow-md ${
                  doc.stato === 'obsoleto' ? 'opacity-70' : ''
                }`}
              >
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center">
                    {getDocumentTypeIcon(doc.tipo)}
                    <span className={`ml-2 text-xs font-medium px-2 py-1 rounded-full ${
                      doc.stato === 'attivo' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {doc.stato === 'attivo' ? 'In vigore' : 'Non in vigore'}
                    </span>
                  </div>
                  <h3 className="mt-3 text-lg leading-6 font-medium text-gray-900">
                    {doc.titolo}
                  </h3>
                  <div className="mt-2 flex justify-between text-sm text-gray-500">
                    <span>{doc.categoria}</span>
                    <span>{formatDate(doc.data)}</span>
                  </div>
                  {doc.descrizione && (
                    <p className="mt-3 text-sm text-gray-600 line-clamp-3">
                      {doc.descrizione}
                    </p>
                  )}
                  {doc.tags && doc.tags.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {doc.tags.map((tag, index) => (
                        <span key={index} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="bg-gray-50 px-4 py-4 sm:px-6 flex justify-between items-center">
                  <span className="text-xs text-gray-500">
                    {doc.tipo}
                  </span>
                  <a
                    href={getDocumentUrl(doc.path)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-emerald-700 bg-emerald-100 hover:bg-emerald-200"
                  >
                    <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Scarica
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Nota legale */}
        <div className="mt-12 bg-blue-50 p-6 rounded-lg">
          <h3 className="text-xl font-semibold text-blue-800 mb-4">Nota legale</h3>
          <p className="text-blue-700 mb-4">
            I documenti riportati in questa sezione sono pubblicati a scopo informativo. 
            Fanno fede i testi normativi pubblicati nelle fonti ufficiali (Gazzetta Ufficiale, 
            siti istituzionali del MIMIT e del GSE).
          </p>
          <p className="text-blue-700">
            I documenti sono aggiornati periodicamente, ma è sempre consigliabile verificare 
            l'ultima versione disponibile sui siti istituzionali.
          </p>
        </div>
      </main>
      
      <footer className="bg-gray-800 text-white mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-gray-400">
              © {new Date().getFullYear()} DIRATEC SRL. Tutti i diritti riservati.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}