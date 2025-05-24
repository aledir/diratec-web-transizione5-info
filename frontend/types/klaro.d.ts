// frontend/types/klaro.d.ts
declare module 'klaro' {
    export interface KlaroService {
      name: string;
      title: string;
      description: string;
      purposes: string[];
      cookies?: string[];
      required?: boolean;
      optOut?: boolean;
      onlyOnce?: boolean;
      default?: boolean;
    }
  
    export interface KlaroPurpose {
      name: string;
      title: string;
      description: string;
    }
  
    export interface KlaroTranslations {
      [key: string]: {
        consentModal?: {
          title?: string;
          description?: string;
          privacyPolicy?: {
            name?: string;
            text?: string;
          };
        };
        consentNotice?: {
          changeDescription?: string;
          description?: string;
          learnMore?: string;
          acceptAll?: string;
          decline?: string;
        };
        purposes?: {
          [key: string]: string;
        };
        ok?: string;
        save?: string;
        decline?: string;
        close?: string;
        acceptAll?: string;
        acceptSelected?: string;
        service?: {
          disableAll?: {
            title?: string;
            description?: string;
          };
          optOut?: {
            title?: string;
            description?: string;
          };
          purpose?: string;
          purposes?: string;
          required?: {
            title?: string;
            description?: string;
          };
        };
        poweredBy?: string;
      };
    }
  
    export interface KlaroConfig {
      version?: number;
      elementID?: string;
      styling?: {
        theme?: string[];
      };
      noAutoLoad?: boolean;
      htmlTexts?: boolean;
      embedded?: boolean;
      groupByPurpose?: boolean;
      storageMethod?: string;
      storageName?: string;
      cookieName?: string;
      cookieExpiresAfterDays?: number;
      default?: boolean;
      mustConsent?: boolean;
      acceptAll?: boolean;
      hideDeclineAll?: boolean;
      hideLearnMore?: boolean;
      noticeAsModal?: boolean;
      lang?: string;
      services?: KlaroService[];
      purposes?: KlaroPurpose[];
      translations?: KlaroTranslations;
    }
  
    export interface KlaroInstance {
      show(): void;
      hide(): void;
      getConsent(serviceName: string): boolean;
      updateConsent(serviceName: string, consent: boolean): void;
    }
  
    declare global {
      interface Window {
        klaro?: KlaroInstance;
        klaroConfig?: KlaroConfig;
      }
    }
  }