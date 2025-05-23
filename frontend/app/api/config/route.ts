import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const configPath = path.join(process.cwd(), 'public', 'shared-documents', 'config.json');
    
    // Verifica che il file esista
    if (!fs.existsSync(configPath)) {
      console.error(`File non trovato: ${configPath}`);
      return NextResponse.json(
        { error: 'File di configurazione non trovato' },
        { status: 404 }
      );
    }

    // Leggi e analizza il file JSON
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    
    // Risposta con i dati
    return NextResponse.json(configData);
  } catch (error) {
    console.error('Errore lettura config.json:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Errore lettura configurazione' },
      { status: 500 }
    );
  }
}