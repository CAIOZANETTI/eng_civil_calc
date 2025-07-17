import math
from dataclasses import dataclass
from typing import List

import pandas as pd

@dataclass
class EntradasSilo:
    r: float
    h: float
    t_inicial: float
    gamma_grao: float = 8.0
    mu: float = 0.4
    fck: float = 40.0  # MPa
    taxa_aco_passivo: float = 80.0  # kg/m3
    taxa_aco_ativo: float = 15.0  # kg/m3
    gamma_c: float = 1.4
    sigma_precompressao: float = 2.0  # MPa
    custo_concreto: float = 800.0
    custo_aco_passivo: float = 12.0
    custo_aco_ativo: float = 15.0

def _pressao_janssen(z: float, r: float, gamma: float, mu: float) -> float:
    return gamma * r / (2 * mu) * (1 - math.exp(-2 * mu * z / r))


def _pressao_airy(z: float, h: float, gamma: float) -> float:
    return gamma * max(h - z, 0)


def calcular_silo_vertical(entr: EntradasSilo) -> pd.DataFrame:
    """Cálculo simplificado do silo vertical seguindo o roteiro.

    Parameters
    ----------
    entr : EntradasSilo
        Dados de entrada do silo.

    Returns
    -------
    pandas.DataFrame
        Resumo das principais grandezas calculadas.
    """
    if entr.r <= 0 or entr.h <= 0 or entr.t_inicial <= 0:
        raise ValueError("dimensoes invalidas")

    # 1. Pressões laterais (Janssen e Airy)
    n = 20
    zs = [i * entr.h / (n - 1) for i in range(n)]
    p_j = [_pressao_janssen(z, entr.r, entr.gamma_grao, entr.mu) for z in zs]
    p_a = [_pressao_airy(z, entr.h, entr.gamma_grao) for z in zs]
    p_total = [max(pj, pa) for pj, pa in zip(p_j, p_a)]
    p_design = [entr.gamma_c * p for p in p_total]
    p_max = max(p_design)

    # 2. Espessura preliminar (Bresler simplificado)
    fcd = entr.fck / entr.gamma_c
    t_min = p_max * entr.r / (0.6 * fcd * 1e3)  # MPa -> kN/m2
    t_final = max(entr.t_inicial, t_min)

    # 3. Protensão circunferencial necessária
    sigma_theta = p_max * entr.r / t_final
    p_force = entr.sigma_precompressao * 1e3 * 2 * math.pi * entr.r * t_final

    # 4. Consumo de materiais
    volume_concreto = 2 * math.pi * entr.r * entr.h * t_final
    massa_passiva = volume_concreto * entr.taxa_aco_passivo
    massa_ativa = volume_concreto * entr.taxa_aco_ativo

    custo_concreto = volume_concreto * entr.custo_concreto
    custo_aco_passivo = massa_passiva * entr.custo_aco_passivo
    custo_aco_ativo = massa_ativa * entr.custo_aco_ativo
    custo_total = custo_concreto + custo_aco_passivo + custo_aco_ativo

    return pd.DataFrame([
        {
            "p_max_kN_m2": p_max,
            "t_final_m": t_final,
            "forca_protensao_kN": p_force / 1e3,
            "volume_concreto_m3": volume_concreto,
            "massa_aco_passivo_kg": massa_passiva,
            "massa_aco_ativo_kg": massa_ativa,
            "custo_total_R$": custo_total,
        }
    ])

if __name__ == "__main__":
    e = EntradasSilo(r=15, h=48, t_inicial=0.3)
    df = calcular_silo_vertical(e)
    print(df)
