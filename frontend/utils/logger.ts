// frontend/utils/logger.ts
/**
 * Utility per logging avanzato con colori e categorie
 */

// Definizione dei livelli di log
type LogLevel = 'debug' | 'info' | 'warn' | 'error';

// Configurazione colori per console
const LOG_COLORS = {
  debug: '#8a8a8a', // grigio
  info: '#2563eb',  // blu
  warn: '#d97706',  // arancione
  error: '#dc2626', // rosso
  auth: '#7c3aed',  // viola (auth)
  ws: '#059669',    // verde (websocket)
  chat: '#0891b2'   // azzurro (chat)
};

// Configurazione per abilitare/disabilitare i log
const LOG_CONFIG = {
  enabled: true,
  minLevel: 'debug' as LogLevel,
  enableCategories: {
    auth: true,
    ws: true,
    chat: true,
    http: true,
    ui: true,
    default: true
  }
};

// Flag per ambiente di produzione
const isProduction = process.env.NODE_ENV === 'production';

// Utility per formattare il timestamp
const timestamp = () => {
  return new Date().toISOString().slice(11, 23); // HH:MM:SS.mmm
};

/**
 * Logger base con supporto per categorie e livelli
 */
export const logger = {
  debug: (message: string, category = 'default', data?: any) => {
    logWithLevel('debug', message, category, data);
  },
  
  info: (message: string, category = 'default', data?: any) => {
    logWithLevel('info', message, category, data);
  },
  
  warn: (message: string, category = 'default', data?: any) => {
    logWithLevel('warn', message, category, data);
  },
  
  error: (message: string, category = 'default', data?: any) => {
    logWithLevel('error', message, category, data);
  },
  
  // Loggers specializzati per categorie comuni
  auth: {
    debug: (message: string, data?: any) => logWithLevel('debug', message, 'auth', data),
    info: (message: string, data?: any) => logWithLevel('info', message, 'auth', data),
    warn: (message: string, data?: any) => logWithLevel('warn', message, 'auth', data),
    error: (message: string, data?: any) => logWithLevel('error', message, 'auth', data),
  },
  
  ws: {
    debug: (message: string, data?: any) => logWithLevel('debug', message, 'ws', data),
    info: (message: string, data?: any) => logWithLevel('info', message, 'ws', data),
    warn: (message: string, data?: any) => logWithLevel('warn', message, 'ws', data),
    error: (message: string, data?: any) => logWithLevel('error', message, 'ws', data),
  },
  
  chat: {
    debug: (message: string, data?: any) => logWithLevel('debug', message, 'chat', data),
    info: (message: string, data?: any) => logWithLevel('info', message, 'chat', data),
    warn: (message: string, data?: any) => logWithLevel('warn', message, 'chat', data),
    error: (message: string, data?: any) => logWithLevel('error', message, 'chat', data),
  }
};

/**
 * Funzione interna per gestire il logging effettivo
 */
function logWithLevel(level: LogLevel, message: string, category = 'default', data?: any) {
  // In produzione, loghiamo solo warn ed error
  if (isProduction && (level === 'debug' || level === 'info')) {
    return;
  }

  // Verifica se il logging è abilitato
  if (!LOG_CONFIG.enabled) return;
  
  // Verifica il livello minimo
  const levels: LogLevel[] = ['debug', 'info', 'warn', 'error'];
  const minLevelIndex = levels.indexOf(LOG_CONFIG.minLevel);
  const currentLevelIndex = levels.indexOf(level);
  
  if (currentLevelIndex < minLevelIndex) return;
  
  // Verifica categoria abilitata
  if (!LOG_CONFIG.enableCategories[category as keyof typeof LOG_CONFIG.enableCategories]) return;
  
  // Colore per la categoria, fallback su default per categorie non definite
  const categoryColor = LOG_COLORS[category as keyof typeof LOG_COLORS] || LOG_COLORS.debug;
  const levelColor = LOG_COLORS[level];
  
  // Formatta il prefisso con timestamp, livello e categoria
  const prefix = `%c[${timestamp()}]%c [${level.toUpperCase()}] %c[${category}]`;
  
  // Stili CSS per i vari componenti del log
  const timestampStyle = 'color: gray; font-weight: normal';
  const levelStyle = `color: ${levelColor}; font-weight: bold`;
  const categoryStyle = `color: ${categoryColor}; font-weight: bold`;
  
  // Log base con prefisso formattato
  console[level](prefix, timestampStyle, levelStyle, categoryStyle, message);
  
  // Log dati aggiuntivi se presenti
  if (data !== undefined) {
    console[level]('%cData:', 'color: gray', data);
  }
}

export default logger;