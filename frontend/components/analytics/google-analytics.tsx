// frontend/components/analytics/GoogleAnalytics.tsx
"use client"
import Script from 'next/script';
import { useEffect, useState } from 'react';

interface GoogleAnalyticsProps {
  measurementId: string;
}

export default function GoogleAnalytics({ measurementId }: GoogleAnalyticsProps) {
  const [consentGiven, setConsentGiven] = useState(false);

  useEffect(() => {
    // Funzione per controllare il consenso Klaro
    const checkConsent = () => {
      if (typeof window !== 'undefined' && window.klaro) {
        const consent = window.klaro.getConsent('google-analytics');
        setConsentGiven(consent || false);
      }
    };

    // Controlla il consenso iniziale
    checkConsent();

    // Listener per cambiamenti di consenso
    const consentHandler = () => {
      checkConsent();
    };

    // Aggiungi listener per eventi Klaro
    if (typeof window !== 'undefined') {
      window.addEventListener('klaro-consent-changed', consentHandler);
    }

    // Cleanup
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('klaro-consent-changed', consentHandler);
      }
    };
  }, []);

  // Non renderizzare nulla se non c'è consenso
  if (!consentGiven) {
    return null;
  }

  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${measurementId}`}
        strategy="afterInteractive"
        data-name="google-analytics"
      />
      <Script id="google-analytics" strategy="afterInteractive" data-name="google-analytics">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${measurementId}', {
            page_title: document.title,
            page_location: window.location.href,
            anonymize_ip: true,
            cookie_flags: 'SameSite=None;Secure'
          });
        `}
      </Script>
    </>
  );
}