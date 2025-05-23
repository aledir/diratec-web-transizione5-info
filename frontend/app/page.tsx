// app/page.tsx
import GSEStatsWidget from '@/components/GSEStatsWidget';
import ChatBox from '@/components/ChatBox';
import Image from 'next/image';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="bg-gray-50 min-h-screen">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-emerald-600">Transizione 5.0</h1>
            <span className="text-sm text-gray-500">by DIRATEC SRL</span>
          </div>
          <nav className="hidden md:flex space-x-6">
            <Link href="/" className="text-gray-800 hover:text-emerald-600 font-medium">Home</Link>
            <Link href="/docs" className="text-gray-600 hover:text-emerald-600">Documenti</Link>
            <Link href="/admin" className="text-gray-600 hover:text-emerald-600">Area Riservata</Link>
          </nav>
          <div className="md:hidden">
            {/* Menu mobile */}
            <button className="p-2 rounded-md text-gray-600 hover:text-emerald-600 hover:bg-gray-100">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero section */}
        <section className="mb-12">
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
            <div className="lg:col-span-3 space-y-6">
              <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                Credito d'imposta Transizione 5.0
              </h2>
              <p className="text-lg text-gray-600">
                Ottieni fino al 45% di credito d'imposta per investimenti in tecnologie digitali e sostenibili grazie 
                al nuovo piano Transizione 5.0 del PNRR.
              </p>
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Principali benefici</h3>
                <ul className="space-y-2">
                  <li className="flex items-start">
                    <svg className="h-5 w-5 text-emerald-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Fino al 45% di credito d'imposta per investimenti in beni materiali 4.0</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="h-5 w-5 text-emerald-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>35% per investimenti in beni immateriali 4.0</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="h-5 w-5 text-emerald-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Formazione del personale con credito fino al 40%</span>
                  </li>
                  <li className="flex items-start">
                    <svg className="h-5 w-5 text-emerald-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Azioni per la riduzione dei consumi energetici</span>
                  </li>
                </ul>
              </div>
            </div>
            <div className="lg:col-span-2">
              {/* Widget GSE Statistics */}
              <GSEStatsWidget />
              
              <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Tempo limitato</h3>
                <p className="text-gray-600 mb-4">
                  Le risorse sono limitate e vengono assegnate in ordine cronologico fino ad esaurimento.
                </p>
                <Link 
                  href="#chat"
                  className="block w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg text-center transition duration-150 ease-in-out"
                >
                  Verifica subito la tua idoneità
                </Link>
              </div>
            </div>
          </div>
        </section>
        
        {/* Tabella percentuali */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Percentuali di credito d'imposta</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white rounded-lg shadow-md">
              <thead className="bg-emerald-50">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700 uppercase tracking-wider">
                    Tipologia investimento
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700 uppercase tracking-wider">
                    Credito d'imposta
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700 uppercase tracking-wider">
                    Requisiti
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                    Beni materiali 4.0
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-600 font-semibold">
                    35% - 45%
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    Riduzione consumi energetici almeno 3% (35%) o 5% (45%)
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                    Beni immateriali 4.0
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-600 font-semibold">
                    35%
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    Software, sistemi, piattaforme per i beni materiali 4.0
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                    Formazione 4.0
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-600 font-semibold">
                    40%
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    Formazione su tecnologie 4.0 e transizione ecologica
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                    Energia rinnovabile
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-600 font-semibold">
                    35% - 45%
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    Impianti di autoconsumo per riduzione consumi
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
        
        {/* Chat section */}
        <section id="chat" className="mb-12">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1 space-y-4">
              <h2 className="text-2xl font-bold text-gray-900">Assistente virtuale</h2>
              <p className="text-gray-600">
                Il nostro assistente specializzato può aiutarti a:
              </p>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-emerald-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Capire se la tua azienda è idonea</span>
                </li>
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-emerald-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Calcolare i possibili benefici fiscali</span>
                </li>
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-emerald-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Spiegare requisiti e procedure</span>
                </li>
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-emerald-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Rispondere a domande specifiche</span>
                </li>
              </ul>
              
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mt-6">
                <h3 className="text-lg font-medium text-blue-800">Nota importante</h3>
                <p className="text-sm text-blue-700 mt-1">
                  Per una valutazione personalizzata completa, un nostro esperto ti contatterà dopo la chat.
                </p>
              </div>
            </div>
            <div className="lg:col-span-2">
              <ChatBox />
            </div>
          </div>
        </section>
        
        {/* Processo section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Il processo di certificazione</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="rounded-full w-10 h-10 flex items-center justify-center bg-emerald-100 text-emerald-600 font-semibold mb-4">1</div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">Verifica idoneità</h3>
              <p className="text-gray-600 text-sm">
                Analisi dei requisiti dell'azienda e valutazione della tipologia di investimento.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="rounded-full w-10 h-10 flex items-center justify-center bg-emerald-100 text-emerald-600 font-semibold mb-4">2</div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">Pianificazione</h3>
              <p className="text-gray-600 text-sm">
                Definizione del budget, delle tempistiche e dei risultati di risparmio energetico da ottenere.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="rounded-full w-10 h-10 flex items-center justify-center bg-emerald-100 text-emerald-600 font-semibold mb-4">3</div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">Implementazione</h3>
              <p className="text-gray-600 text-sm">
                Realizzazione dell'investimento e monitoraggio dei parametri di efficienza energetica.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="rounded-full w-10 h-10 flex items-center justify-center bg-emerald-100 text-emerald-600 font-semibold mb-4">4</div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">Certificazione</h3>
              <p className="text-gray-600 text-sm">
                Verifica e certificazione da parte di un ente accreditato del risparmio energetico ottenuto.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-gray-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-medium mb-4">DIRATEC SRL</h3>
              <p className="text-gray-400 text-sm">
                Specialisti in consulenza per incentivi alle imprese e crediti d'imposta per l'innovazione tecnologica e sostenibile.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-medium mb-4">Link utili</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><Link href="/docs" className="hover:text-white">Documenti ufficiali</Link></li>
                <li><Link href="/faq" className="hover:text-white">Domande frequenti</Link></li>
                <li><Link href="/normativa" className="hover:text-white">Normativa</Link></li>
                <li><Link href="/contatti" className="hover:text-white">Contatti</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-medium mb-4">Contatti</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-gray-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span>info@diratec.it</span>
                </li>
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-gray-500 mt-0.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <span>+39 030 123 4567</span>
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
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-white">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.866-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
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
    </div>
  );
}