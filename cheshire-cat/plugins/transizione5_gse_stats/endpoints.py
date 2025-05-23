from cat.mad_hatter.decorators import endpoint
from cat.log import log
from cat.auth.permissions import check_permissions  # Importa il controllo permessi
from fastapi import Request

@endpoint.get("/api/gse-stats")
def get_gse_stats(request: Request, cat=check_permissions("CONVERSATION", "READ")):
    """Endpoint che restituisce i dati aggiornati delle statistiche GSE"""
    log.info("Chiamata all'endpoint /api/gse-stats")
    from .gse_stats_operations import get_gse_stats_data
    return get_gse_stats_data()

@endpoint.get("/api/gse-stats/update")
async def update_gse_stats(request: Request, cat=check_permissions("CONVERSATION", "WRITE")):
    """Endpoint per forzare l'aggiornamento manuale dei dati GSE"""
    log.info("Chiamata all'endpoint /api/gse-stats/update")
    from .gse_stats_operations import update_gse_stats_data
    return await update_gse_stats_data()