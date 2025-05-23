-- Schema per il database di gestione lead
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    azienda_data JSONB NOT NULL,
    investimenti_data JSONB NOT NULL,
    contatto_data JSONB NOT NULL,
    fonte VARCHAR(255) NOT NULL DEFAULT 'transizione5.info',
    data_creazione TIMESTAMP NOT NULL DEFAULT NOW(),
    score INTEGER,
    stato VARCHAR(50) NOT NULL DEFAULT 'nuovo',
    assegnato_a VARCHAR(255),
    note TEXT
);
CREATE TABLE IF NOT EXISTS conversazioni (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    session_id VARCHAR(255) NOT NULL,
    inizio_conversazione TIMESTAMP NOT NULL DEFAULT NOW(),
    fine_conversazione TIMESTAMP,
    completato_form BOOLEAN DEFAULT FALSE,
    data JSONB NOT NULL
);
-- Indici per migliorare le performance
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score);
CREATE INDEX IF NOT EXISTS idx_leads_stato ON leads(stato);
CREATE INDEX IF NOT EXISTS idx_leads_data_creazione ON leads(data_creazione);
CREATE INDEX IF NOT EXISTS idx_conversazioni_lead_id ON conversazioni(lead_id);
CREATE INDEX IF NOT EXISTS idx_conversazioni_session_id ON conversazioni(session_id);
-- Tabella per analytics
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    evento VARCHAR(100) NOT NULL,
    session_id VARCHAR(255),
    lead_id INTEGER REFERENCES leads(id),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    dati JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_analytics_evento ON analytics(evento);
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp);
-- Vista per report riassuntivi
CREATE OR REPLACE VIEW lead_summary AS
SELECT
    date_trunc('day', data_creazione) AS giorno,
    COUNT(*) AS totale_lead,  -- Corretto COUNT() -> COUNT(*)
    COUNT(CASE WHEN score >= 70 THEN 1 END) AS lead_qualificati,
    COUNT(CASE WHEN stato = 'convertito' THEN 1 END) AS lead_convertiti,
    ROUND(COUNT(CASE WHEN stato = 'convertito' THEN 1 END)::numeric / COUNT(*) * 100, 2) AS tasso_conversione,  -- Corretto COUNT() -> COUNT(*)
    ROUND(AVG(score), 2) AS score_medio
FROM
    leads
GROUP BY
    giorno
ORDER BY
    giorno DESC;
-- Tabella audit_log
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    user_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
