// frontend/app/api/chat-token/route.ts
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    // Usa l'URL interno Docker e HTTP invece dell'URL esterno HTTPS
    const wsToken = process.env.CCAT_API_KEY_WS;
    console.log(`[API Debug] Richiesta token WebSocket`);
    
    if (!wsToken) {
      console.error('[API Debug] Token WebSocket non trovato nelle variabili di ambiente');
      // Verifica quali variabili sono disponibili per debug
      console.log('[API Debug] Variabili disponibili:', {
        CCAT_INTERNAL_URL: process.env.CCAT_INTERNAL_URL ? 'Presente' : 'Assente',
        CCAT_API_KEY: process.env.CCAT_API_KEY ? 'Presente' : 'Assente',
        CCAT_API_KEY_WS: process.env.CCAT_API_KEY_WS ? 'Presente' : 'Assente'
      });
      return NextResponse.json(
        { error: 'Token di configurazione non disponibile' },
        { status: 500 }
      );
    }
    
    console.log(`[API Debug] Token WebSocket trovato, lunghezza: ${wsToken.length}`);
    // Restituisci il token come risposta JSON
    return NextResponse.json({ token: wsToken });
  } catch (error) {
    console.error('Errore nel generare il token chat:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Errore nel recupero dei dati' },
      { status: 500 }
    );
  }
}