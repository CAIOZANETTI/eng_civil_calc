from pathlib import Path
import textwrap

ROOT = Path('civil_calc')

# Diretórios a serem criados
DIRS = [
    ROOT / 'dados' / 'brutos',
    ROOT / 'src' / 'civil_calc' / 'nucleo',
    ROOT / 'src' / 'civil_calc' / 'modulos' / 'silo',
    ROOT / 'testes' / 'nucleo',
    ROOT / 'testes' / 'modulos',
    ROOT / 'saidas',
    ROOT / 'docs',
    ROOT / '.github' / 'workflows',
]


def make_dirs():
    for d in DIRS:
        d.mkdir(parents=True, exist_ok=True)


CUSTOS = """material,unidade,preco_R$/un
concreto_C40,m3,800
aco_CA50,kg,12
aco_EHT,kg,15
"""

PREMISSAS = """variavel,valor
gamma_solo,8
k,0.4
"""

MATERIAIS_PY = textwrap.dedent('''
    from pathlib import Path
    import pandas as pd

    DADOS_BRUTOS = Path(__file__).resolve().parents[3] / "dados" / "brutos"

    def carregar_premissas() -> pd.DataFrame:
        """Carrega o arquivo de premissas em um DataFrame."""
        return pd.read_csv(DADOS_BRUTOS / "premissas.csv")
''')

CUSTOS_PY = textwrap.dedent('''
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
''')

UNIDADES_PY = """# Placeholder para funções de conversão de unidades"""

ORQUESTRADOR_PY = textwrap.dedent('''
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
''')

SILO_INIT = """"""

PAREDE_PY = textwrap.dedent('''
    import pandas as pd

    def calcular(entradas: dict) -> pd.DataFrame:
        """Cálculo simplificado da parede do silo."""
        altura = entradas.get("altura", 0)
        area = entradas.get("area", 0)
        volume = area * altura
        massa_aco = volume * 80
        return pd.DataFrame([{"volume_concreto_m3": volume, "massa_aco_kg": massa_aco}])
''')

CLI_PY = textwrap.dedent('''
    import json
    import sys
    from civil_calc.nucleo import orquestrador

    def main() -> None:
        if len(sys.argv) != 3:
            print("uso: cli.py <modulo> '<json>'")
            sys.exit(1)
        modulo = sys.argv[1]
        entradas = json.loads(sys.argv[2])
        df = orquestrador.executar(modulo, entradas)
        print(df)

    if __name__ == "__main__":
        main()
''')

TEST_CUSTOS = textwrap.dedent('''
    from civil_calc.nucleo.custos import preco

    def test_preco_concreto():
        assert preco("concreto_C40") == 800
''')

TEST_SILO_PAREDE = textwrap.dedent('''
    from civil_calc.nucleo import orquestrador

    def test_silo_parede():
        df = orquestrador.executar("silo.parede", {"area": 1, "altura": 1})
        assert df["custo_total"].iloc[0] > 0
''')

CI_YML = textwrap.dedent('''
    name: CI
    on: [push, pull_request]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          - uses: actions/setup-python@v4
            with:
              python-version: '3.12'
          - run: pip install -e .[dev]
          - run: pytest -q
''')

PYPROJECT = textwrap.dedent('''
    [project]
    name = "civil_calc"
    version = "0.1.0"
    dependencies = [
        "pandas",
        "openpyxl"
    ]

    [project.optional-dependencies]
    dev = [
        "pytest"
    ]

    [build-system]
    requires = ["setuptools>=61"]
    build-backend = "setuptools.build_meta"
''')

README = textwrap.dedent('''
    # civil_calc

    Ferramentas de cálculo estrutural.

    ## Instruções rápidas

    1. Crie um ambiente virtual
    2. `pip install -e .[dev]`
    3. `pytest`
    4. `python src/cli.py silo.parede '{"area": 1, "altura": 1}'`
''')


def write_file(path: Path, content: str):
    path.write_text(content, encoding='utf-8')


def main():
    make_dirs()
    write_file(ROOT / 'dados' / 'brutos' / 'custos.csv', CUSTOS)
    write_file(ROOT / 'dados' / 'brutos' / 'premissas.csv', PREMISSAS)
    write_file(ROOT / 'src' / 'civil_calc' / 'nucleo' / '__init__.py', '')
    write_file(ROOT / 'src' / 'civil_calc' / 'nucleo' / 'materiais.py', MATERIAIS_PY)
    write_file(ROOT / 'src' / 'civil_calc' / 'nucleo' / 'custos.py', CUSTOS_PY)
    write_file(ROOT / 'src' / 'civil_calc' / 'nucleo' / 'unidades.py', UNIDADES_PY)
    write_file(ROOT / 'src' / 'civil_calc' / 'nucleo' / 'orquestrador.py', ORQUESTRADOR_PY)
    write_file(ROOT / 'src' / 'civil_calc' / 'modulos' / 'silo' / '__init__.py', SILO_INIT)
    write_file(ROOT / 'src' / 'civil_calc' / 'modulos' / 'silo' / 'parede.py', PAREDE_PY)
    write_file(ROOT / 'src' / 'cli.py', CLI_PY)
    write_file(ROOT / 'testes' / 'nucleo' / 'test_custos.py', TEST_CUSTOS)
    write_file(ROOT / 'testes' / 'modulos' / 'test_silo_parede.py', TEST_SILO_PAREDE)
    write_file(ROOT / '.github' / 'workflows' / 'ci.yml', CI_YML)
    write_file(ROOT / 'pyproject.toml', PYPROJECT)
    write_file(ROOT / 'README.md', README)
    print(f"Estrutura criada em {ROOT.resolve()}")


if __name__ == '__main__':
    main()
