import { NextResponse } from 'next/server';

// Modifica il file route.ts aggiungendo più logging e gestione degli errori
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const forceUpdate = searchParams.get('forceUpdate') === 'true';
  
  try {
    // Usa l'URL interno Docker e HTTP invece dell'URL esterno HTTPS
    const apiUrl = process.env.CCAT_INTERNAL_URL;
    const apiKey = process.env.CCAT_API_KEY;
    
    console.log(`[API Debug] URL API configurato: ${apiUrl}`);
    
    const endpoint = forceUpdate ? '/custom/api/gse-stats/update' : '/custom/api/gse-stats';
    const fullUrl = `${apiUrl}${endpoint}`;
    
    console.log(`[API Debug] URL completo per chiamata fetch: ${fullUrl}`);
    
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      next: { revalidate: 3600 }
    });
    
    if (!response.ok) {
      throw new Error(`Errore nella risposta del server: ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Errore nel recupero dei dati GSE:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Errore nel recupero dei dati' },
      { status: 500 }
    );
  }
}