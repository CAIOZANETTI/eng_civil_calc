
from civil_calc.nucleo.custos import preco

def test_preco_concreto():
    assert preco("concreto_C40") == 800
