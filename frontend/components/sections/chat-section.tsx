import React from 'react';
import ChatBox from '@/components/chat/chat-box';

interface ChatSectionProps {
  // Potrebbe non servire props
}

export default function ChatSection({}: ChatSectionProps) {
  return (
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
  );
}