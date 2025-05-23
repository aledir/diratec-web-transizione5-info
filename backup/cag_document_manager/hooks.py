"""Hook per integrare la KV-cache in Cheshire Cat."""
import os
from cat.log import log
from cat.mad_hatter.decorators import hook

# Cache del contesto per evitare ricaricamenti inutili
_context_cache = None
_context_builder = None

def _get_context_builder(cat):
    """Ottiene un'istanza di ContextBuilder."""
    global _context_builder
    
    if _context_builder is None:
        try:
            # Import delayed to avoid circular imports
            from .context_builder import ContextBuilder
            
            # Ottieni le impostazioni
            settings = cat.mad_hatter.get_plugin_settings("CAG Document Manager")
            
            if not settings:
                log.warning("⚠️ Impostazioni non trovate per CAG Document Manager, utilizzo valori predefiniti")
                settings = {
                    "documents_dir": "/app/cat/shared/documents",
                    "context_dir": "/app/cat/shared/documents/context",
                    "context_file": "cag_context.md",
                    "max_context_tokens": 180000
                }
            
            documents_dir = settings.get("documents_dir")
            context_dir = settings.get("context_dir")
            context_file = settings.get("context_file")
            
            if not documents_dir or not context_dir or not context_file:
                log.warning("⚠️ Impostazioni incomplete, utilizzo valori predefiniti")
                documents_dir = "/app/cat/shared/documents"
                context_dir = "/app/cat/shared/documents/context"
                context_file = "cag_context.md"
            
            context_path = os.path.join(context_dir, context_file)
            
            # Crea le directory se non esistono
            os.makedirs(documents_dir, exist_ok=True)
            os.makedirs(context_dir, exist_ok=True)
            
            # Crea l'istanza
            _context_builder = ContextBuilder(documents_dir, context_path)
            log.info(f"✅ ContextBuilder inizializzato")
            
        except Exception as e:
            log.error(f"❌ Errore nell'inizializzazione di ContextBuilder: {str(e)}")
            return None
    
    return _context_builder

def _get_or_build_context(cat, force=False):
    """Ottiene il contesto KV-cache, ricostruendolo se necessario."""
    global _context_cache
    
    # Se il contesto è già in cache e non è forzata la rigenerazione, usalo
    if _context_cache is not None and not force:
        log.info("✅ Usando contesto KV-cache dalla memoria")
        return _context_cache
    
    # Ottieni le impostazioni
    settings = cat.mad_hatter.get_plugin_settings("CAG Document Manager")
    ttl_hours = settings.get("context_ttl_hours", 24) if settings else 24
    
    # Ottieni o costruisci il contesto
    context_builder = _get_context_builder(cat)
    if context_builder is None:
        log.error("❌ ContextBuilder non inizializzato, impossibile ottenere contesto")
        return "Errore: contesto non disponibile. Contattare il supporto."
        
    context = context_builder.build_full_context(force=force, ttl_hours=ttl_hours)
    
    # Salva in cache
    _context_cache = context
    
    # Log con stima token
    context_length = len(context)
    estimated_tokens = context_length // 4  # Stima approssimativa ~4 caratteri per token
    log.info(f"✅ Contesto KV-cache {'rigenerato' if force else 'caricato'}: {context_length} caratteri / ~{estimated_tokens} token stimati")
    
    return context

def disable_vector_rag(cat):
    """Disabilita temporaneamente la ricerca vettoriale."""
    try:
        # Verifica se l'oggetto cat ha working_memory
        if hasattr(cat, 'working_memory'):
            # Disabilita la ricerca vettoriale
            cat.working_memory["vector_search_enabled"] = False
            log.info("🔄 Ricerca vettoriale RAG disabilitata - Modalità CAG attiva")
        else:
            log.warning("⚠️ Impossibile disabilitare ricerca vettoriale: working_memory non disponibile")
        
        return True
    except Exception as e:
        log.error(f"❌ Errore nella disabilitazione della ricerca vettoriale: {str(e)}")
        return False

@hook
def after_cat_bootstrap(cat):
    """Inizializza la KV-cache all'avvio del plugin."""
    try:
        # Prepara il context builder in modo ritardato
        # Non chiamiamo _get_context_builder qui per evitare problemi di inizializzazione
        log.info("✅ Plugin CAG Document Manager inizializzato (contesto sarà caricato alla prima richiesta)")
    except Exception as e:
        log.error(f"❌ Errore nell'inizializzazione del plugin CAG: {str(e)}")

@hook(priority=10)  # Alta priorità per intercettare prima di altri hook
def before_chat_completion(params, cat):
    """Aggiunge la KV-cache alle richieste dell'LLM."""
    try:
        # Se è già impostato un override della risposta, non interferire
        if "llm_response" in params and params["llm_response"]:
            return params
        
        # Ottieni la query dell'utente
        user_message = params.get("user_message", "")
        
        # Se la query è vuota, salta
        if not user_message.strip():
            return params
        
        # Ottieni il contesto KV-cache
        kv_cache = _get_or_build_context(cat)
        
        # Formatta il prompt con la KV-cache
        if "prompt" in params:
            # Se c'è già un prompt, aggiungi la KV-cache all'inizio
            original_prompt = params["prompt"]
            params["prompt"] = f"{kv_cache}\n\n# QUERY UTENTE\n{user_message}\n\n{original_prompt}"
        else:
            # Altrimenti, crea un nuovo prompt con la KV-cache
            params["prompt"] = f"{kv_cache}\n\n# QUERY UTENTE\n{user_message}"
        
        log.info(f"✅ KV-cache aggiunta al prompt: {len(kv_cache)} caratteri di contesto, {len(params['prompt'])} caratteri totali")
        
        return params
    except Exception as e:
        log.error(f"❌ Errore nell'aggiunta della KV-cache: {str(e)}")
        return params

@hook
def before_memory_search(search_query, cat):
    """Intercetta la ricerca nella memoria se non necessaria grazie alla KV-cache."""
    try:
        # Verifica se l'oggetto cat ha working_memory e se la ricerca vettoriale è disabilitata
        vector_search_enabled = True
        if hasattr(cat, 'working_memory'):
            vector_search_enabled = cat.working_memory.get("vector_search_enabled", True)
        
        if not vector_search_enabled:
            log.info("✅ Ricerca RAG bypassata (usando KV-cache)")
            return None
        
        # Altrimenti, torna alla ricerca normale
        return search_query
    except Exception as e:
        log.error(f"❌ Errore nel bypass della ricerca memoria: {str(e)}")
        # In caso di errore, meglio procedere con la ricerca standard
        return search_query