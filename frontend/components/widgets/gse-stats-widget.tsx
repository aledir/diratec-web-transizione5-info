"use client";

import React, { useState, useEffect, useRef } from 'react';

// Tipo per le statistiche GSE
interface GSEStats {
  risorse_disponibili: string;
  risorse_totali: string;
  risorse_prenotate: string;
  risorse_utilizzate: string;
  ultimo_aggiornamento: string;
}

const GSEStatsWidget: React.FC = () => {
  // Stati
  const [stats, setStats] = useState<GSEStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  
  // Ref per mantenere la posizione di scrolling
  const widgetRef = useRef<HTMLDivElement>(null);
  
  // Funzione per formattare i numeri come valuta
  const formatCurrency = (value: string): string => {
    try {
      // I valori arrivano già nel formato italiano con la virgola come separatore decimale
      // Es: "5.338.991.323,11"
      
      // Converti in numero per il formatter
      // Prima rimuovi i separatori delle migliaia (i punti)
      const cleanValue = value.replace(/\./g, '');
      // Poi sostituisci la virgola con il punto per il parsing in JavaScript
      const numericValue = cleanValue.replace(',', '.');
      const num = parseFloat(numericValue);
      
      if (isNaN(num)) {
        console.error(`Impossibile convertire "${value}" in numero`);
        return value;
      }
      
      // Formatta usando l'API Intl con localizzazione italiana
      return new Intl.NumberFormat('it-IT', {
        style: 'currency',
        currency: 'EUR',
        maximumFractionDigits: 0
      }).format(num);
    } catch (e) {
      console.error('Errore nella formattazione della valuta:', e);
      return value;
    }
  };

  // Funzione per recuperare i dati
  const fetchStats = async (forceUpdate = false): Promise<void> => {
    try {
      if (forceUpdate) setIsUpdating(true);
      if (!stats) setLoading(true); // Solo se non abbiamo ancora dati
      
      // Memorizza la posizione di scroll prima dell'aggiornamento
      const scrollPosition = window.scrollY;
      
      // Usa la nostra API route interna
      const endpoint = forceUpdate ? '/api/gse-stats?forceUpdate=true' : '/api/gse-stats';
      console.log(`Fetching GSE stats from: ${endpoint}`);
      
      const response = await fetch(endpoint, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(20000) // 20 secondi timeout
      });
      
      // Se la risposta non è OK, lancia un errore
      if (!response.ok) {
        throw new Error(`Errore nella risposta del server: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('GSE stats received:', data);
      
      // Gestione diversa a seconda dell'endpoint chiamato
      if (forceUpdate) {
        // Se stiamo chiamando l'endpoint /update
        if (data.status === "success" && data.data) {
          setStats(data.data);
          setError(null);
          console.log('Dati aggiornati con successo:', data.data);
        } else if (data.error) {
          throw new Error(data.error);
        } else {
          throw new Error("Formato risposta non valido dall'endpoint di aggiornamento");
        }
      } else {
        // Se stiamo chiamando l'endpoint normale
        if (data.risorse_disponibili) {
          setStats(data);
          setError(null);
          console.log('Dati ottenuti con successo:', data);
        } else if (data.error) {
          throw new Error(data.error);
        } else {
          throw new Error("Formato risposta non valido");
        }
      }
      
      // Ripristina la posizione di scrolling dopo l'aggiornamento dati
      setTimeout(() => {
        window.scrollTo({ top: scrollPosition });
      }, 0);
      
    } catch (err) {
      console.error('Errore nel recupero dei dati GSE:', err);
      const errorMessage = err instanceof Error ? err.message : 'Dati non disponibili. Riprova più tardi.';
      setError(errorMessage);
      // Se non abbiamo ancora dati, mantieni stats null per mostrare l'errore
      if (!stats) {
        setStats(null);
      }
    } finally {
      setLoading(false);
      setIsUpdating(false);
    }
  };

  // Effetto iniziale per caricare i dati
  useEffect(() => {
    fetchStats();
    
    // Aggiorna i dati ogni ora
    const intervalId = setInterval(() => fetchStats(), 60 * 60 * 1000);
    
    return () => clearInterval(intervalId);
  }, []);

  // Handler per il click sul pulsante di aggiornamento
  const handleRefresh = (e: React.MouseEvent): void => {
    e.preventDefault();
    fetchStats(true);
  };

  // Calcola percentuali per la visualizzazione grafica
  const numFromItalianFormat = (str: string): number => {
    return parseFloat(str.replace(/\./g, '').replace(',', '.'));
  };

  // 🔥 LOADING PRINCIPALE - Rendering durante caricamento iniziale
  if (loading && !stats) {
    return (
      <div ref={widgetRef} className="bg-white border border-gray-200 rounded-lg shadow-md overflow-hidden">
        <div className="bg-emerald-600 text-white font-medium px-4 py-2 flex justify-between items-center">
          <h3 className="text-lg">Risorse Transizione 5.0</h3>
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          </div>
        </div>
        
        <div className="p-4">
          <div className="animate-pulse space-y-4">
            {/* Skeleton per il valore principale */}
            <div className="space-y-2">
              <div className="h-6 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-full"></div>
            </div>
            
            {/* Skeleton per le voci dettaglio */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-200 rounded-sm"></div>
                <div className="h-4 bg-gray-200 rounded flex-1"></div>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-200 rounded-sm"></div>
                <div className="h-4 bg-gray-200 rounded flex-1"></div>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-200 rounded-sm"></div>
                <div className="h-4 bg-gray-200 rounded flex-1"></div>
              </div>
            </div>
            
            {/* Skeleton per la nota in fondo */}
            <div className="pt-3 border-t border-gray-100">
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Rendering errore (solo se non abbiamo dati)
  if (error && !stats) {
    return (
      <div ref={widgetRef} className="bg-white border border-gray-200 rounded-lg shadow-md">
        <div className="bg-emerald-600 text-white font-medium px-4 py-2 flex justify-between items-center">
          <h3 className="text-lg">Risorse Transizione 5.0</h3>
          <button 
            onClick={handleRefresh}
            disabled={isUpdating}
            className="p-1 hover:bg-emerald-700 rounded"
            title="Riprova"
          >
            <svg className={`h-4 w-4 text-white ${isUpdating ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        
        <div className="p-4">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            <div className="font-medium mb-1">Dati non disponibili</div>
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Se non abbiamo dati ma non c'è errore specifico, fallback
  if (!stats) {
    return (
      <div ref={widgetRef} className="bg-white border border-gray-200 rounded-lg shadow-md">
        <div className="bg-emerald-600 text-white font-medium px-4 py-2 flex justify-between items-center">
          <h3 className="text-lg">Risorse Transizione 5.0</h3>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
        </div>
        
        <div className="p-4">
          <div className="text-center text-gray-500">
            Caricamento dati in corso...
          </div>
        </div>
      </div>
    );
  }

  const totaleNum = numFromItalianFormat(stats.risorse_totali);
  const disponibiliNum = numFromItalianFormat(stats.risorse_disponibili);
  const prenotateNum = numFromItalianFormat(stats.risorse_prenotate);
  const utilizzateNum = numFromItalianFormat(stats.risorse_utilizzate);
  
  const disponibiliPercent = isNaN(totaleNum) || totaleNum === 0 ? 0 : (disponibiliNum / totaleNum) * 100;
  const prenotatePercent = isNaN(totaleNum) || totaleNum === 0 ? 0 : (prenotateNum / totaleNum) * 100;
  const utilizzatePercent = isNaN(totaleNum) || totaleNum === 0 ? 0 : (utilizzateNum / totaleNum) * 100;

  // Overlay per aggiornamento (mantiene i dati visibili)
  const updatingOverlay = isUpdating && (
    <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10 rounded-lg">
      <div className="flex flex-col items-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mb-2"></div>
        <p className="text-sm text-emerald-600">Aggiornamento in corso...</p>
      </div>
    </div>
  );

  // 🎯 RENDERING PRINCIPALE - Widget con dati
  return (
    <div ref={widgetRef} className="bg-white border border-gray-200 rounded-lg shadow-md overflow-hidden relative">
      {updatingOverlay}
      
      <div className="bg-emerald-600 text-white font-medium px-4 py-2 flex justify-between items-center">
        <h3 className="text-lg">Risorse Transizione 5.0</h3>
        <div className="flex items-center space-x-2">
          <span className="text-xs bg-white/20 px-2 py-1 rounded">
            {stats.ultimo_aggiornamento}
          </span>
          <button 
            onClick={handleRefresh} 
            className="p-1 hover:bg-emerald-700 rounded"
            title="Aggiorna dati"
            disabled={isUpdating}
          >
            <svg className={`h-4 w-4 text-white ${isUpdating ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>
      
      <div className="p-4">
        <div className="mb-4">
          <div className="text-xl font-bold mb-1">
            {formatCurrency(stats.risorse_disponibili)} <span className="text-sm font-normal text-gray-500">disponibili su {formatCurrency(stats.risorse_totali)}</span>
          </div>
          
          {/* Barra di progresso */}
          <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
            <div className="flex h-full">
              <div 
                className="bg-emerald-500 h-full" 
                style={{ width: `${disponibiliPercent}%` }}
              ></div>
              <div 
                className="bg-blue-500 h-full" 
                style={{ width: `${prenotatePercent}%` }}
              ></div>
              <div 
                className="bg-purple-500 h-full" 
                style={{ width: `${utilizzatePercent}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-emerald-500 mr-2 rounded-sm"></div>
              <span>Disponibili</span>
            </div>
            <span className="font-medium">{formatCurrency(stats.risorse_disponibili)}</span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-500 mr-2 rounded-sm"></div>
              <span>Prenotate</span>
            </div>
            <span className="font-medium">{formatCurrency(stats.risorse_prenotate)}</span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 mr-2 rounded-sm"></div>
              <span>Utilizzate</span>
            </div>
            <span className="font-medium">{formatCurrency(stats.risorse_utilizzate)}</span>
          </div>
        </div>
        
        <div className="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-500">
          I dati sono estratti direttamente dal portale GSE ufficiale.
        </div>
      </div>
    </div>
  );
};

export default GSEStatsWidget;