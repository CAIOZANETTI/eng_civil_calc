
import pandas as pd

def calcular(entradas: dict) -> pd.DataFrame:
    """Cálculo simplificado da parede do silo."""
    altura = entradas.get("altura", 0)
    area = entradas.get("area", 0)
    volume = area * altura
    massa_aco = volume * 80
    return pd.DataFrame([{"volume_concreto_m3": volume, "massa_aco_kg": massa_aco}])
