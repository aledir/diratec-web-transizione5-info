// app/privacy-policy/page.tsx
import { Metadata } from 'next';
import LegalDocument from '@/components/legal/legal-document';
import fs from 'fs';
import path from 'path';

export const metadata: Metadata = {
  title: 'Privacy Policy - Transizione 5.0 | DIRATEC SRL',
  description: 'Informativa sulla privacy per l\'assistente virtuale Transizione 5.0 di DIRATEC SRL',
  robots: 'index, follow',
  openGraph: {
    title: 'Privacy Policy - Assistente Virtuale Transizione 5.0',
    description: 'Informativa sulla privacy per l\'assistente virtuale specializzato per la Transizione 5.0',
    type: 'website',
    locale: 'it_IT',
  },
};

async function getPrivacyContent() {
  try {
    const filePath = path.join(process.cwd(), 'public', 'legal', 'privacy-policy.md');
    const content = fs.readFileSync(filePath, 'utf8');
    return content;
  } catch (error) {
    console.error('Errore nel caricamento della privacy policy:', error);
    return `# Errore nel caricamento
    
La privacy policy non è attualmente disponibile. Per informazioni, contattare info@diratec.it`;
  }
}

export default async function PrivacyPolicyPage() {
  const content = await getPrivacyContent();
  
  return (
    <LegalDocument
      title="Privacy Policy"
      content={content}
      lastUpdated="23 maggio 2025"
    />
  );
}