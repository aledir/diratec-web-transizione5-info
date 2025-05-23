// components/sections/ProcessSection.tsx
import React from 'react';

interface ProcessSectionProps {
  // Dati processo potrebbero essere props in futuro
}

export default function ProcessSection({}: ProcessSectionProps) {
  const processSteps = [
    {
      number: 1,
      title: "Verifica idoneità",
      description: "Analisi dei requisiti dell'azienda e valutazione della tipologia di investimento."
    },
    {
      number: 2,
      title: "Pianificazione",
      description: "Definizione del budget, delle tempistiche e dei risultati di risparmio energetico da ottenere."
    },
    {
      number: 3,
      title: "Implementazione",
      description: "Realizzazione dell'investimento e monitoraggio dei parametri di efficienza energetica."
    },
    {
      number: 4,
      title: "Certificazione",
      description: "Verifica e certificazione da parte di un ente accreditato del risparmio energetico ottenuto."
    }
  ];

  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Il processo di certificazione</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {processSteps.map((step) => (
          <div key={step.number} className="bg-white p-6 rounded-lg shadow-md">
            <div className="rounded-full w-10 h-10 flex items-center justify-center bg-emerald-100 text-emerald-600 font-semibold mb-4">
              {step.number}
            </div>
            <h3 className="text-lg font-medium text-gray-800 mb-2">{step.title}</h3>
            <p className="text-gray-600 text-sm">
              {step.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}