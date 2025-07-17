
from pathlib import Path
import importlib
import pandas as pd
from . import custos

SAIDAS = Path(__file__).resolve().parents[3] / "saidas"

def executar(modulo: str, entradas: dict) -> pd.DataFrame:
    """Executa o cálculo do módulo informado."""
    mod = importlib.import_module(f"civil_calc.modulos.{modulo}")
    df = mod.calcular(entradas)
    preco_concreto = custos.preco("concreto_C40")
    preco_aco = custos.preco("aco_CA50")
    df["custo_concreto"] = df["volume_concreto_m3"] * preco_concreto
    df["custo_aco"] = df["massa_aco_kg"] * preco_aco
    df["custo_total"] = df["custo_concreto"] + df["custo_aco"]
    SAIDAS.mkdir(exist_ok=True)
    caminho = SAIDAS / f"{modulo.replace('.', '_')}.xlsx"
    df.to_excel(caminho, index=False)
    return df
