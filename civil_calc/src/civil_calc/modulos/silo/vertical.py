import math
import pandas as pd


def calcular(entradas: dict) -> pd.DataFrame:
    """Calcula pressões e consumo de material para um silo vertical.

    Parâmetros
    ----------
    entradas: dict
        - ``r``: raio do silo (m)
        - ``h``: altura de projeto (m)
        - ``t``: espessura da parede (m)
        - ``gamma``: peso específico do grão em kN/m³ (opcional, padrão 8)
        - ``mu``: coeficiente de atrito grão-parede (opcional, padrão 0.4)
        - ``taxa_aco``: taxa global de armadura em kg/m³ (opcional, padrão 120)

    Retorna
    -------
    pandas.DataFrame
        Dados calculados de pressão Janssen, volume de concreto e massa de aço.
    """
    r = float(entradas.get("r", 0))
    h = float(entradas.get("h", 0))
    t = float(entradas.get("t", 0))
    gamma = float(entradas.get("gamma", 8))
    mu = float(entradas.get("mu", 0.4))
    taxa_aco = float(entradas.get("taxa_aco", 120))

    if r <= 0 or h <= 0 or t <= 0:
        raise ValueError("r, h e t devem ser positivos")

    # Pressão lateral de Janssen na profundidade h
    p_janssen = gamma * r / (2 * mu) * (1 - math.exp(-2 * mu * h / r))

    volume_concreto = 2 * math.pi * r * h * t
    massa_aco = volume_concreto * taxa_aco

    return pd.DataFrame([
        {
            "pressao_janssen_kN_m2": p_janssen,
            "volume_concreto_m3": volume_concreto,
            "massa_aco_kg": massa_aco,
        }
    ])
