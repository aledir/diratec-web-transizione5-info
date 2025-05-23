from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field
import os

class LeadManagementSettings(BaseModel):
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

@plugin
def settings_model():
    return LeadManagementSettings