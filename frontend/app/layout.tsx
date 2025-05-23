import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { AuthProvider } from '@/contexts/AuthContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Transizione 5.0 | DIRATEC SRL',
  description: 'Assistente virtuale per la Transizione 5.0 e crediti d\'imposta per l\'innovazione sostenibile',
  robots: {
    index: true,
    follow: true,
  },
  // Rimuovi la proprietà viewport da qui
};

// Aggiungi questa esportazione separata per la viewport
export const viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="it">
      <body className={inter.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}