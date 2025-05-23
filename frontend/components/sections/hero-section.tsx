// components/sections/HeroSection.tsx
import React from 'react';
import Link from 'next/link';
import GSEStatsWidget from '@/components/widgets/gse-stats-widget';

interface HeroSectionProps {
  // Potrebbe non servire props per ora
}

export default function HeroSection({}: HeroSectionProps) {
  return (
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
  );
}