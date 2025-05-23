import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Permettere richieste cross-origin per risorse Next.js durante lo sviluppo
  allowedDevOrigins: ['transizione5.info', '*.transizione5.info'],
  
  // Configurazione aggiornata per Turbopack
  // Sostituisce experimental.turbo con turbopack
  turbopack: {
    // Configurazioni per i loader di Turbopack usando la nuova sintassi
    rules: {
      "*.mdx": ["mdx-loader"]  // Esempio
    }
  },
  
  // Altri parametri di configurazione
  reactStrictMode: true
};

export default nextConfig;