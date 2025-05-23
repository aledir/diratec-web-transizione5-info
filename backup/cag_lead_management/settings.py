"""Impostazioni configurabili per il plugin CAG Lead Management."""
from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field
import os

class CAGLeadManagementSettings(BaseModel):
    db_host: str = Field(
        default=os.environ.get("POSTGRES_HOST", "postgres"),
        title="Host database",
        description="Host del database PostgreSQL"
    )
    db_port: str = Field(
        default=os.environ.get("POSTGRES_PORT", "5432"),
        title="Porta database",
        description="Porta del database PostgreSQL"
    )
    db_name: str = Field(
        default=os.environ.get("POSTGRES_DB", "diratec_leads"),
        title="Nome database",
        description="Nome del database PostgreSQL"
    )
    db_user: str = Field(
        default=os.environ.get("POSTGRES_USER", "diratec_user"),
        title="Utente database",
        description="Utente del database PostgreSQL"
    )
    db_password: str = Field(
        default=os.environ.get("POSTGRES_PASSWORD", "securepassword"),
        title="Password database",
        description="Password del database PostgreSQL",
        extra={"secret": True}
    )
    
    safety_enabled: bool = Field(
        default=True,
        title="Abilita controlli di sicurezza",
        description="Attiva i controlli di sicurezza sui messaggi"
    )
    
    off_topic_detection: bool = Field(
        default=True, 
        title="Rilevamento fuori tema",
        description="Abilita il rilevamento dei messaggi fuori tema"
    )
    
    offensive_content_filter: bool = Field(
        default=True,
        title="Filtro contenuti offensivi",
        description="Abilita il filtro per contenuti offensivi"
    )
    
    rate_limit_enabled: bool = Field(
        default=True,
        title="Rate limiting",
        description="Abilita la limitazione delle richieste"
    )
    
    session_timeout_minutes: int = Field(
        default=30,
        title="Timeout sessione (minuti)",
        description="Durata massima di inattività di una sessione"
    )

@plugin
def settings_model():
    return CAGLeadManagementSettings