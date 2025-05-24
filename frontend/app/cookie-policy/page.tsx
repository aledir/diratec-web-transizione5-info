// app/cookie-policy/page.tsx
import { Metadata } from 'next';
import LegalDocument from '@/components/legal/legal-document';
import fs from 'fs';
import path from 'path';

export const metadata: Metadata = {
  title: 'Cookie Policy - Transizione 5.0 | DIRATEC SRL',
  description: 'Informativa sui cookie per l\'assistente virtuale Transizione 5.0 di DIRATEC SRL',
  robots: 'index, follow',
  openGraph: {
    title: 'Cookie Policy - Assistente Virtuale Transizione 5.0',
    description: 'Informativa sui cookie per l\'assistente virtuale specializzato per la Transizione 5.0',
    type: 'website',
    locale: 'it_IT',
  },
};

async function getCookieContent() {
  try {
    const filePath = path.join(process.cwd(), 'public', 'legal', 'cookie-policy.md');
    const content = fs.readFileSync(filePath, 'utf8');
    return content;
  } catch (error) {
    console.error('Errore nel caricamento della cookie policy:', error);
    return `# Errore nel caricamento
    
La cookie policy non è attualmente disponibile. Per informazioni, contattare info@diratec.it`;
  }
}

export default async function CookiePolicyPage() {
  const content = await getCookieContent();
  
  return (
    <LegalDocument
      title="Cookie Policy"
      content={content}
      lastUpdated="23 maggio 2025"
    />
  );
}