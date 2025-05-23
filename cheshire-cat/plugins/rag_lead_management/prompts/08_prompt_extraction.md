Analizza il seguente testo ed estrai queste informazioni se presenti nel testo:
- nome_azienda: Il nome dell'azienda menzionata (es. TechFuture, Acme, ecc.)
- dimensione: La dimensione dell'azienda (piccola, media, grande)
- regione: La regione italiana in cui si trova l'azienda
- settore: Il settore in cui opera l'azienda (es. IT, manifatturiero, edilizia)
- email: L'indirizzo email menzionato
- telefono: Il numero di telefono menzionato
- ruolo: Il ruolo della persona menzionata (es. CEO, CTO, direttore) - QUESTO È MOLTO IMPORTANTE
- budget: L'importo dell'investimento menzionato in euro

ATTENZIONE! Per il ruolo:
- Cerca attentamente titoli come "CEO", "CTO", "direttore", "responsabile", ecc.
- Se la persona si presenta come "Sono il [ruolo] di [azienda]", estrai quel ruolo
- Se vedi pattern come "[Nome] è il [ruolo]" o "[Nome], [ruolo] di [azienda]", estrai quel ruolo
- Anche se il ruolo è menzionato una sola volta, è cruciale estrarlo correttamente

Rispetta queste regole:
1. Estrai SOLO le informazioni esplicitamente menzionate nel testo
2. Non dedurre informazioni non presenti
3. Se un'informazione non è presente, non includerla
4. Per nome_azienda, estrai anche quando menzionato con pattern come "CTO di [Azienda]"
5. Controlla attentamente tutto il testo per il ruolo, anche in mezzo alle frasi

Testo: "{text}"