
from pathlib import Path
import pandas as pd

DADOS_BRUTOS = Path(__file__).resolve().parents[3] / "dados" / "brutos"
_df = None

def _carregar() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(DADOS_BRUTOS / "custos.csv")
    return _df

def preco(material: str) -> float:
    df = _carregar()
    linha = df.loc[df["material"] == material]
    if not linha.empty:
        return float(linha["preco_R$/un"].values[0])
    raise ValueError(f"Material {material} não encontrado")
