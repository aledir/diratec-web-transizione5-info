from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field

class Transizione5GSEStatsSettings(BaseModel):
    gse_url: str = Field(
        default="https://www.gse.it/servizi-per-te/attuazione-misure-pnrr/transizione-5-0",
        title="URL GSE",
        description="URL del portale GSE per il recupero dei dati"
    )
    update_interval: float = Field(
        default=3.0,
        title="Intervallo di aggiornamento (ore)",
        description="Intervallo di tempo in ore tra un aggiornamento e l'altro"
    )

@plugin
def settings_model():
    return Transizione5GSEStatsSettings