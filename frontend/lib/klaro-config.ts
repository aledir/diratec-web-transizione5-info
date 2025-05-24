// frontend/lib/klaro-config.ts
import { KlaroConfig } from 'klaro';

export const klaroConfig: KlaroConfig = {
  // Versione configurazione (incrementa per forzare rimostra banner)
  version: 1,
  
  // Elemento dove inserire Klaro (di default body)
  elementID: 'klaro',
  
  // Stile del banner - MANTENUTO ORIGINALE
  styling: {
    theme: ['light', 'bottom'],
  },
  
  // Non mostrare il banner subito
  noAutoLoad: false,
  
  // HTML personalizzabile
  htmlTexts: true,
  
  // Configurazione globale
  embedded: false,
  
  // Configurazione gruppi di servizi
  groupByPurpose: true,
  
  // Configurazione storage
  storageMethod: 'localStorage',
  storageName: 'klaro',
  
  // Configurazione cookie
  cookieName: 'klaro',
  cookieExpiresAfterDays: 120,
  
  // Configurazione per servizi esterni
  default: false,
  mustConsent: true,
  acceptAll: true,
  hideDeclineAll: false,
  hideLearnMore: false,
  
  // Notifica quando cambiano le impostazioni
  noticeAsModal: false,
  
  // Lingue supportate
  lang: 'it',

  // ✨ AGGIUNTA MINIMA: Link privacy policy per modal
  privacyPolicy: {
    it: '/privacy-policy'
  },
  
  // Configurazione dei servizi - MANTENUTA ORIGINALE
  services: [
    {
      // Google Analytics 4
      name: 'google-analytics',
      title: 'Google Analytics',
      description: 'Utilizziamo Google Analytics per analizzare come gli utenti interagiscono con il sito e migliorare l\'esperienza di navigazione. I dati sono anonimi e aggregati.',
      purposes: ['analytics'],
      cookies: [
        '_ga',
        '_ga_*',
        '_gid',
        '_gat',
        '_gtag_*',
        '__utma',
        '__utmb',
        '__utmc',
        '__utmt',
        '__utmz'
      ],
      required: false,
      optOut: false,
      onlyOnce: true,
      default: false, // ← GDPR compliance: deve rimanere false
    },
    
    {
      // Cookie tecnici necessari - DESCRIZIONE CORRETTA MANTENUTA
      name: 'required',
      title: 'Cookie Tecnici',
      description: 'Utilizziamo i Cookie Tecnici per il funzionamento dell\'assistente virtuale AI. Sono essenziali per mantenere la continuità della conversazione e associare le risposte dell\'AI alla tua sessione di chat.',
      purposes: ['functional'],
      required: true,
      optOut: false,
      onlyOnce: true,
      default: true,
      cookies: [
        'klaro',              // ← Preferenze cookie (Klaro)
        'chat_session_id',    // ← ID sessione chat AI
        'auth_token'          // ← Token autenticazione con Cheshire Cat
      ]
    }
  ],
  
  // Definizione degli scopi - MANTENUTA ORIGINALE
  purposes: [
    {
      name: 'functional',
      title: 'Funzionalità Essenziali',
      description: 'Cookie necessari per garantire il funzionamento dell\'assistente AI e la continuità delle conversazioni.'
    },
    {
      name: 'analytics',
      title: 'Analisi e Miglioramento', 
      description: 'Cookie per comprendere come migliorare il servizio attraverso l\'analisi anonima del comportamento degli utenti.'
    }
  ],

  // Traduzioni in italiano - MANTENUTE ORIGINALI
  translations: {
    it: {
      consentModal: {
        title: 'Gestione Cookie e Privacy',
        description: 'Utilizziamo cookie per migliorare la tua esperienza di navigazione. Puoi scegliere quali categorie di cookie accettare.',
        privacyPolicy: {
          name: 'Privacy Policy',
          text: 'Per maggiori informazioni consulta la nostra {privacyPolicy}.'
        }
      },
      consentNotice: {
        changeDescription: 'Sono state apportate modifiche alla nostra politica sui cookie. Aggiorna le tue preferenze.',
        description: 'Utilizziamo cookie per personalizzare contenuti e annunci, fornire funzioni social e analizzare il traffico. {purposes}.',
        learnMore: 'Personalizza',
        acceptAll: 'Accetta tutti',
        decline: 'Rifiuta tutti'
      },
      purposes: {
        functional: 'Funzionalità',
        analytics: 'Analisi e Statistiche'
      },
      ok: 'Accetta',
      save: 'Salva',
      decline: 'Rifiuta',
      close: 'Chiudi',
      acceptAll: 'Accetta tutti',
      acceptSelected: 'Accetta selezionati',
      service: {
        disableAll: {
          title: 'Disabilita tutti i servizi',
          description: 'Utilizza questo interruttore per abilitare/disabilitare tutti i servizi.'
        },
        optOut: {
          title: '(opt-out)',
          description: 'Questo servizio è caricato di default (ma puoi disattivarlo)'
        },
        purpose: 'Scopo',
        purposes: 'Scopi',
        required: {
          title: '(sempre richiesto)',
          description: 'Questo servizio è sempre richiesto'
        }
      },
      poweredBy: 'Sviluppato da DIRATEC SRL'
    }
  }
};