
from civil_calc.nucleo import orquestrador

def test_silo_parede():
    df = orquestrador.executar("silo.parede", {"area": 1, "altura": 1})
    assert df["custo_total"].iloc[0] > 0
