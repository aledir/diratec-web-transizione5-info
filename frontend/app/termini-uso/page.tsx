// app/termini-uso/page.tsx
import { Metadata } from 'next';
import LegalDocument from '@/components/legal/legal-document';
import fs from 'fs';
import path from 'path';

export const metadata: Metadata = {
  title: 'Termini d\'uso - Transizione 5.0 | DIRATEC SRL',
  description: 'Termini e condizioni d\'uso dell\'assistente virtuale per la Transizione 5.0 di DIRATEC SRL',
  robots: 'index, follow',
  openGraph: {
    title: 'Termini d\'uso - Assistente Virtuale Transizione 5.0',
    description: 'Termini e condizioni d\'uso dell\'assistente virtuale specializzato per la Transizione 5.0',
    type: 'website',
    locale: 'it_IT',
  },
};

async function getTerminiContent() {
  try {
    const filePath = path.join(process.cwd(), 'public', 'legal', 'termini-uso.md');
    const content = fs.readFileSync(filePath, 'utf8');
    return content;
  } catch (error) {
    console.error('Errore nel caricamento dei termini d\'uso:', error);
    return `# Errore nel caricamento
    
I termini d'uso non sono attualmente disponibili. Per informazioni, contattare info@diratec.it`;
  }
}

export default async function TerminiUsoPage() {
  const content = await getTerminiContent();
  
  return (
    <LegalDocument
      title="Termini d'uso"
      content={content}
      lastUpdated="23 maggio 2025"
    />
  );
}