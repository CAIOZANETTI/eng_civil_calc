from civil_calc.nucleo import orquestrador


def test_silo_vertical_resultados_positivos():
    entradas = {"r": 15, "h": 48, "t": 0.30}
    df = orquestrador.executar("silo.vertical", entradas)
    assert df["pressao_janssen_kN_m2"].iloc[0] > 0
    assert df["volume_concreto_m3"].iloc[0] > 0
    assert df["massa_aco_kg"].iloc[0] > 0
