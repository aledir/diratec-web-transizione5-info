// frontend/app/api/validate-token/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    // Estrai il token dal corpo della richiesta
    const { token } = await request.json();
    
    if (!token) {
      return NextResponse.json(
        { valid: false, error: 'Token mancante' },
        { status: 400 }
      );
    }
    
    // In produzione, qui verificheresti il token contro Cheshire Cat API
    // Ma per semplicità, controlliamo solo che il token abbia una lunghezza valida
    // e che corrisponda all'API key websocket
    
    const wsToken = process.env.CCAT_API_KEY_WS;
    
    if (!wsToken) {
      console.error('[API] CCAT_API_KEY_WS non configurata');
      return NextResponse.json(
        { valid: false, error: 'Configurazione server incompleta' },
        { status: 500 }
      );
    }
    
    // Controlla se il token è valido (in questo caso, se corrisponde alla chiave WS)
    const isValid = token === wsToken;
    
    return NextResponse.json({ valid: isValid });
  } catch (error) {
    console.error('Errore nella validazione del token:', error);
    return NextResponse.json(
      { valid: false, error: 'Errore interno del server' },
      { status: 500 }
    );
  }
}