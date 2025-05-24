import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { AuthProvider } from '@/contexts/AuthContext';
import GoogleAnalytics from '@/components/analytics/GoogleAnalytics';
import KlaroWrapper from '@/components/analytics/KlaroWrapper';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Transizione 5.0 | DIRATEC SRL',
  description: 'Assistente virtuale per la Transizione 5.0 e crediti d\'imposta per l\'innovazione sostenibile',
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const measurementId = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;
  
  return (
    <html lang="it">
      <body className={inter.className}>
        {/* Klaro GDPR Banner - caricato sempre */}
        <KlaroWrapper />
        
        {/* Google Analytics - solo se c'è consenso e siamo in produzione */}
        {measurementId && process.env.NODE_ENV === 'production' && (
          <GoogleAnalytics measurementId={measurementId} />
        )}
        
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}