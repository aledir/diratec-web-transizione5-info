"""Impostazioni configurabili per il plugin CAG Document Manager."""
from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field
import os

class CAGDocumentManagerSettings(BaseModel):
    documents_dir: str = Field(
        default="/app/cat/shared/documents",
        title="Directory documenti",
        description="Percorso della directory contenente i documenti"
    )
    
    context_dir: str = Field(
        default="/app/cat/shared/documents/context",
        title="Directory contesto",
        description="Percorso della directory per il contesto KV-cache"
    )
    
    context_file: str = Field(
        default="cag_context.md",
        title="Nome file contesto",
        description="Nome del file Markdown per il contesto KV-cache"
    )
    
    max_context_tokens: int = Field(
        default=180000,
        title="Dimensione massima contesto",
        description="Dimensione massima del contesto in token"
    )
    
    markdown_subdirectory: str = Field(
        default="markdown",
        title="Subdirectory Markdown",
        description="Subdirectory contenente i file Markdown convertiti"
    )

    mathpix_app_id: str = Field(
        default=os.environ.get("MATHPIX_APP_ID", ""),
        title="Mathpix App ID",
        description="ID applicazione per l'API Mathpix"
    )
    
    mathpix_app_key: str = Field(
        default=os.environ.get("MATHPIX_APP_KEY", ""),
        title="Mathpix App Key",
        description="Chiave API per Mathpix",
        extra={"secret": True}
    )

@plugin
def settings_model():
    return CAGDocumentManagerSettings