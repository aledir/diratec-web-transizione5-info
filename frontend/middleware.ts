// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Esporta funzione middleware per Next.js
export function middleware(request: NextRequest) {
  // Ignora le richieste per risorse statiche e webpack-hmr
  if (
    request.nextUrl.pathname.startsWith('/_next/') ||
    request.nextUrl.pathname.includes('webpack-hmr') ||
    request.nextUrl.pathname.startsWith('/static/') ||
    request.headers.get('upgrade') === 'websocket'
  ) {
    return NextResponse.next();
  }
  
  // Per tutte le altre richieste, procedi normalmente
  const response = NextResponse.next();
  
  // Aggiungi intestazioni CORS per i WebSocket
  if (request.headers.get('upgrade') === 'websocket') {
    response.headers.set('Access-Control-Allow-Origin', '*');
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  }
  
  return response;
}

// Limita l'esecuzione del middleware solo alle API
// Escludi esplicitamente le risorse di webpack e statiche
export const config = {
  matcher: [
    // Includi solo le API
    '/api/:path*',
    '/custom/:path*',
    
    // Includi i WebSocket
    '/_next/webpack-hmr',
    
    // Escludi HMR, static e altre risorse interne
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};