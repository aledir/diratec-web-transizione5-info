from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field
import os

class DocumentManagerSettings(BaseModel):
    documents_dir: str = Field(
        default="/app/cat/shared",
        title="Directory documenti",
        description="Percorso della directory contenente i documenti"
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
    return DocumentManagerSettings