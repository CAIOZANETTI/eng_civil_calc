
from pathlib import Path
import pandas as pd

DADOS_BRUTOS = Path(__file__).resolve().parents[3] / "dados" / "brutos"

def carregar_premissas() -> pd.DataFrame:
    """Carrega o arquivo de premissas em um DataFrame."""
    return pd.read_csv(DADOS_BRUTOS / "premissas.csv")
