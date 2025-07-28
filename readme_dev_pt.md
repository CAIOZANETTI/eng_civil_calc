# readme_dev.md — Guia do Desenvolvedor (corrigido)

Este documento descreve **arquitetura**, **APIs**, **contratos de dados**, **padrões de código**, **testes**, **versionamento de datasets**, **performance** e **publicação** do framework. O objetivo é permitir manutenção e evolução do sistema **sem perder rastreabilidade normativa** nem reprodutibilidade.

> Mantra: **determinístico primeiro**, **observável sempre**, **extensível por design**, **dados versionados**.

---

## 1. Arquitetura

```
estruturas/
  pyproject.toml
  README.md
  docs/
    readme_eng.md
    readme_dev.md
    readme_cliente.md
  src/estruturas/
    core/
      actions/            # NBR 6120, 6123:2023, 8681 → geradores de ações e combinações
        seismic.py        # NBR 15421 (sísmica) e ACI 350.3-20 (tanques - Housner)
      materials/          # concreto, aço, durabilidade, detalhamento
        watertight.py     # estanqueidade (wk limites – ACI 350 / ACI 224R / fib)
      fire/               # NBR 15200 — situação de incêndio (tabular/cálculo)
      elements/           # viga, laje, pilar, sapata, estaca, bloco, muro, casca
      silos/              # EN 1991-4 / ACI 313 → pressões e casos de carregamento
      geotech/            # solos, SPT, capacidade, recalques, NSF, radier
        slope_stability.py# NBR 11682 — estabilidade global (FS)
      report/             # Jinja2 → Markdown/HTML
      optimize/           # custo, buscas, Pareto
      uql/                # Monte Carlo, LHS, Sobol, FORM (opcional)
      orchestration/      # fluxo de cargas: laje→viga→pilar→fundação→solo
      utils/              # unidades (pint), validadores, E/S CSV/XLSX, hashing, log_step
  data/
    normas/{br,intl}/*.yaml
    vento/                # parâmetros auxiliares 6123:2023 (defaults, documentados)
    sismo/                # classes de importância/zonas (defaults)
    estanques.yaml        # limites wk recomendados por uso (ACI 350 / fib)
    targets.yaml          # metas (β alvo CC2 50a = 3.8, FS muros, wk_tanque,...)
    custos/*.csv
    materiais_armazenados/*.csv
    geotech/*.csv
    geotech/calibrations/*.json
    compat_matrix.json
  apps/                   # **Aplicações**
    colab/                # **Notebooks Colab**
      01_viga_Md_conhecido.ipynb
      02_pilar_N_M_Mx.ipynb
      03_sapata_solo_areia.ipynb
      10_silo_soja_D30_H48.ipynb
      20_estacas_AV_DQ.ipynb
      30_radier_winkler.ipynb
      90_monte_carlo_silo.ipynb
    streamlit/
      Home.py             # página inicial
      pages/
        01_Viga.py
        02_Pilar.py
        03_Sapata.py
        10_Silo.py
        14_Subpressao.py  # balanço de empuxo/subpressão e piping
        20_Estacas.py
        30_Radier.py
        40_Muros.py
        90_Confiabilidade.py
  tests/
    unit/
    validation/
    golden/
    snapshots/
```

* `core/*`: **sem estatística** — cálculo normativo puro.
* `uql/*`: incertezas, Pf/β, Sobol.
* `optimize/*`: custo e buscas.
* `report/*`: transformação `Result/trace` → `.md`.
* `apps/colab/`: **notebooks em português**, prontos para rodar no Colab.
* `apps/streamlit/pages/`: **páginas do Streamlit** (uma por elemento/módulo).

---

## 2. Modelagem de dados — **Pydantic na borda, `@dataclass` no núcleo**

> Versões de norma explicitadas: **NBR 6122:2022** (com EM1), **NBR 6123:2023**, **NBR 16903:2020**. Estes anos devem aparecer nos relatórios e nos datasets YAML. **Metas de confiabilidade e limites de fissuração** ficam em `data/targets.yaml` e `data/estanques.yaml`.
>
> **Padrão adotado**: entrada do usuário (CSV/XLSX/Streamlit/Colab) com **Pydantic** para validação; núcleo de cálculo com **`@dataclass(slots=True, frozen=True)`** para performance, imutabilidade e hash. A serialização para relatório usa `dataclasses.asdict`.

### 2.1 Modelos de entrada (validação) — Pydantic

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional

ClasseAgress = Literal["I","II","III","IV"]

class MateriaisIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fck: float = Field(ge=10, le=90)
    fyk: float = Field(ge=400, le=700)
    aco: Literal["CA50","CA60"] = "CA50"

class PremissasIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    geo: dict
    materiais: MateriaisIn
    ambiente: dict
    acoes: dict
    normas: dict
    custos: Optional[dict] = None
    otimizacao: Optional[dict] = None
    solo: Optional[dict] = None
    meta: Optional[dict] = None
```

### 2.2 Núcleo determinístico — `@dataclass`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True, frozen=True)
class Materiais:
    fck: float
    fyk: float
    aco: str  # CA50/CA60

@dataclass(slots=True, frozen=True)
class Premissas:
    geo: dict
    materiais: Materiais
    ambiente: dict
    acoes: dict
    normas: dict
    custos: Optional[dict] = None
    otimizacao: Optional[dict] = None
    solo: Optional[dict] = None
    meta: Optional[dict] = None
```

#### 2.2.1 Conversores Pydantic → Dataclass

```python
from dataclasses import asdict

def to_dc(p: PremissasIn) -> Premissas:
    return Premissas(
        geo=p.geo,
        materiais=Materiais(**p.materiais.model_dump()),
        ambiente=p.ambiente,
        acoes=p.acoes,
        normas=p.normas,
        custos=p.custos,
        otimizacao=p.otimizacao,
        solo=p.solo,
        meta=p.meta,
    )
```

### 2.3 Cláusulas, checks e trace — dataclasses

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True, frozen=True)
class Clause:
    norma: str
    ano: int
    secao: str
    tabela: Optional[str] = None

@dataclass(slots=True, frozen=True)
class Check:
    id: str
    descricao: str
    clause: Clause
    value: float
    limit: float
    status: str        # "OK" | "FAIL"
    margin: float
    units: Optional[str] = None

@dataclass(slots=True, frozen=True)
class Step:
    id: str
    clause: Optional[Clause]
    formula_tex: Optional[str]
    vars: dict
    result: float | dict
    units: Optional[str]
    notes: Optional[str]
    dt: float
```

### 2.4 Resultados e Relatório — dataclasses

```python
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class Result:
    kpis: dict
    checks: tuple[Check, ...]
    tables: dict
    plots: dict[str, bytes]
    trace: tuple[Step, ...]
    warnings: tuple[str, ...]
    hash_inputs: str
    meta: dict

@dataclass(slots=True, frozen=True)
class Report:
    markdown: str
    citations: tuple[dict, ...]
    assets: dict[str, bytes]
    summary: dict
```

**`check` serializado** (para snapshot)

```python
{
  "id": "6118-17.3-fissuracao",
  "descricao": "Abertura de fissura - viga",
  "clause": {"norma": "NBR6118", "ano": 2014, "secao": "17.3", "tabela": "T7.2"},
  "value": 0.32, "limit": 0.30, "status": "FAIL", "margin": -0.02, "units": "mm"
}
```

## 4. `@log_step` — com `Step` dataclass

Registrar fórmula LaTeX, variáveis, resultado, unidades, cláusula e tempo. O *trace* armazena objetos `Step`; para o relatório, convertemos com `asdict`.

```python
from dataclasses import asdict
from functools import wraps
from time import perf_counter

TRACE: list[Step] = []  # injetado pelo solver via context manager

def log_step(step_id: str, clause: Clause | None = None, formula_tex: str | None = None):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            t0 = perf_counter(); val, meta = fn(*args, **kwargs); t1 = perf_counter()
            st = Step(
                id=step_id,
                clause=clause,
                formula_tex=formula_tex or meta.get("formula_tex"),
                vars=meta.get("vars", {}),
                result=meta.get("result", val),
                units=meta.get("units"),
                notes=meta.get("notes"),
                dt=t1 - t0,
            )
            TRACE.append(st)
            return val, meta
        return wrapper
    return deco
```

## 5. Report Builder (Jinja2)

O *builder* recebe `Result` (dataclass). Para o template Jinja2, convertemos `checks` e `trace` para `list[dict]` via `asdict`.

```python
from dataclasses import asdict, is_dataclass

def _to_dict(obj):
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, (list, tuple)):
        return [_to_dict(x) for x in obj]
    return obj

def build_report(result: Result, template: str, meta: dict) -> Report:
    env = _get_env()
    payload = _to_dict(result)
    md = env.get_template(template).render(
        result=payload,
        steps=payload["trace"],
        meta=meta,
        citations=_collect_citations(payload),
    )
    return Report(
        markdown=md,
        citations=tuple(_collect_citations(payload)),
        assets={},
        summary=_make_summary(payload),
    )
```

## 6. Dados versionados & ingestão externa

### 6.1 Conjuntos internos

* `data/normas/*.yaml`, `data/custos/*.csv`, `data/materiais_armazenados/*.csv`, `data/geotech/*.csv`.
* `data/vento/` e `data/sismo/` com **valores padrão documentados** (usuário pode sobrescrever).
* `data/estanques.yaml` com limites de `wk` por uso (tanques/ambiental).
* `data/targets.yaml` com metas de projeto/teste (β, FS, wk).
* `compat_matrix.json` mapeia versão do pacote ↔ versões dos datasets.
* Cada execução grava `hash_inputs` (sha256 das premissas + versões dos dados).

### 6.2 **Ingestão de dados externos**

Parsers em `utils/io_csv.py` e `utils/io_xlsx.py` com validação Pydantic.

**SPT / perfil de solo** (`soil_profile.csv`):

```
prof_top;prof_bot;solo;gamma_nat;gamma_sat;N_SPT;N_corr;cu;phi;E;nu;OCR;k;NA_flag;obs
```

* Unidades SI: kN/m³, kPa, MPa, m/s.
* `NA_flag` (0/1) indica presença de NA na camada.

**Boletim de fundação / provas de carga** (`piles_tests.xlsx`):

* Aba `estacas`: `id;tipo;D;L;fck;aco;NA_ini;NA_proj;carga_servico;observacoes`.
* Aba `provas`: `id;etapa;kN;mm;tempo(s)` — curva carga×recalque (NBR 16903:2020).
  Parsers retornam objetos:

```python
class SoilProfile(TypedDict):
    layers: list[dict]
    water_table: float | None

class PileTest(TypedDict):
    id: str; tipo: str; D: float; L: float; curva: list[tuple[float,float]]
```

### 6.3 Correlações e calibração

`calibrate_pile_methods(tests: list[PileTest]) -> dict` ajusta coeficientes dos métodos empíricos e salva em `data/geotech/calibrations/*.json` com metadados (obra, data, autor, erro RMS).

### 6.4 Defaults de vento, sismo e estanqueidade

* `vento/` — parâmetros auxiliares da **NBR 6123:2023**: categorias de terreno, fatores topográficos, notas de cálculo de `V_ref`.
* `sismo/` — classes de importância e espectros‑tipo conforme **NBR 15421** (valores de referência).
* `estanques.yaml` — limites de **wk** por uso (ACI 350 / fib MC2010) com mapeamento para classes.

---

## 7. Testes

### 7.0 IDs de *checks* canônicos

Para aderência ao `readme_eng.md`, padronizar os IDs abaixo (mínimo inicial):

* **Concreto**: `6118-flexao`, `6118-cisalhamento`, `6118-torcao`, `6118-fissuracao`, `6118-flecha`, `6118-cobrimento`.
* **Pilar**: `6118-interacao-NMM`, `6118-segunda-ordem`.
* **Muro**: `muro-FS-deslizamento`, `muro-FS-tombamento`, `muro-sigma-adm`.
* **Silos/Tanques**: `EN1991-4-pressao-enchimento`, `EN1991-4-pressao-fluxo`, `excêntrico-envelope`, `anel-tracao`, `flambagem-local`, `wk-estenqueidade`.
* **Fundações diretas**: `sapata-capacidade-terzaghi`, `sapata-capacidade-meyerhof`, `sapata-capacidade-vesic`, `sapata-puncao`, `sapata-pressao-contato`, `sapata-recalque`.
* **Estacas**: `estaca-AV-capacidade`, `estaca-DQ-capacidade`, `estaca-NSF`, `estaca-prova-carga-NBR16903`.
* **Radier**: `radier-pressao-contato`, `radier-recalque`.
* **Uplift/Subpressão**: `uplift-flutuacao-fs`, `uplift-flutuacao-margin`, `piping-exit-gradient`.
* **Sismo/Incêndio**: `15421-espectro`, `350.3-PiPc`, `15200-TRRF`.

### 7.1 Unit

* Cobertura ≥ 90% no `core`.
* Parsers (`io_csv`, `io_xlsx`) com casos de erro/sucesso.

### 7.2 Golden

* Viga/Pilar/Sapata — exemplos numéricos de referência.
* Silo — perfis de pressão e σ_h/σ_v; anel de tração.
* Estacas — Aoki‑Velloso/Décourt‑Quaresma; confronto com prova de carga exemplo.

### 7.3 Property-based

* Domínios: `t ∈ [0.12,0.60]`, `fck ∈ [20,50]`, `k ∈ [0.3,0.7]`, `μ ∈ [0.2,0.5]`, `φ ∈ [20,40]°`, `cu ∈ [10,120] kPa`.
* Garantias: capacidade ↑ com `φ/cu`; pressão de contato média ≈ `N/A`.

### 7.4 Snapshot `.md`

* Relatórios em `tests/snapshots/`; alterações exigem update intencional + nota no `CHANGELOG`.

### 7.5 Confiabilidade

* `N=1_000` → **IC95%(Pf)** com erro ≤ 20% em casos de validação.

### 7.6 Integração (end‑to‑end)

* **Fluxo completo**: laje→viga→pilar→fundação→solo; verificar equilíbrio de cargas, pressões e recalques.
* **Streamlit smoke**: cada página executa caso mínimo e exporta `.md` sem erro.

## 8. Performance

* Vetorização (`numpy`); `numba` onde dói.
* Cache de pressões (silos) e combinações.
* Meta: **≤ 5 s** por elemento no core; **N=1.000** MC em minutos.

---

## 9. Otimização

* Penalização forte para violações.
* Grid com poda → gulosa local.
* Pareto: custo × aço × deslocamento (ou custo × β).

---

## 10. UQ — Monte Carlo / LHS / Sobol

```python
def run_monte_carlo_silo(premissas: Premissas, N: int, sampler: str = "lhs", dists: dict | None = None) -> dict:
    """Retorna {pf, beta, stats_df, plots, sobol(optional)}"""
```

* Distribuições em `scipy.stats`; seed registrada.
* Correlações via Cholesky.
* Métricas: `Pf`, `β=-Φ⁻¹(Pf)`, IC95% (Clopper–Pearson).
* Sobol (SALib) para KPIs.
* **Metas sugeridas (`data/targets.yaml`)**: `beta_target_cc2_50a = 3.8`; `wk_tanque = 0.10 mm`; `fs_muro_desl = 1.5`; `fs_muro_tomb = 2.0`; `fs_uplift = 1.00` (mínimo); `i_max/i_adm ≤ 1.00`.

---

## 11. Colab, Streamlit Pages & Plotly

### 11.1 Google Colab

* Instalação editável e execução de exemplos em `apps/colab/`.
* Notebooks devem importar apenas APIs públicas de `src/estruturas/*`.
* Salvar artefatos: `.md`, `.html` (se convertido), `.csv` de resultados, figuras Plotly (`fig.write_html`/`write_image`).

### 11.2 Streamlit **Pages** (multi‑página)

Estrutura sugerida:

```
apps/streamlit/
  Home.py                 # visão geral
  pages/
    01_Viga.py
    02_Pilar.py
    03_Sapata.py
    10_Silo.py
    14_Subpressao.py
    20_Estacas.py
    30_Radier.py
    40_Muros.py
    90_Confiabilidade.py
```

Boilerplate de página:

```python
import streamlit as st
from estruturas.core.elements.viga import solve_viga
from estruturas.ui.helpers import collect_viga_inputs
from estruturas.ui.plots import plot_pareto

st.title("Viga — Dimensionamento")
premissas = collect_viga_inputs()
if st.button("Calcular"):
    result, report = solve_viga(premissas)
    st.markdown(report["markdown"])  # ou viewer próprio
    st.download_button("Relatório .md", report["markdown"].encode(), "relatorio_viga.md")
```

### 11.3 Página de **Subpressão/Empuxo**

Boilerplate:

```python
import streamlit as st
from estruturas.core.geotech.uplift import check_uplift
from estruturas.ui.plots import plot_hist_ecdf

st.title("Subpressão e Empuxo de Água no Subsolo")
params = collect_uplift_inputs()
if st.button("Verificar"):
    res = check_uplift(**params)
    st.metric("FS", f"{res['FS']:.2f}")
    st.write(res["table"])  # tabela padrão
    st.markdown(render_uplift(res, params))
```

### 11.4 Plotly — helpers

Criar módulo `estruturas/ui/plots.py` com:

* `plot_press_profile(result)` — perfil de pressões (silos).
* `plot_stress_profile(result)` — σ_h/σ_v × altura.
* `plot_hist_ecdf(samples, name)` — histograma + ECDF.
* `plot_pareto(points)` — custo × aço × deslocamento (ou custo × β).
  Todos retornam `plotly.graph_objects.Figure`.

---

## 12. CI/CD

* GitHub Actions: lint (`ruff`), formatação (`black`), **tests** (unit/golden/property/snapshot/integracao), coverage, build.
* Publicação: releases semânticas; PyPI opcional.
* **Matriz de validação**: toda release executa os **casos ouro** e compara **KPIs‑alvo** de `data/targets.yaml` (ex.: `β_CC2_50a=3.8`, `wk_tanque=0.10 mm`, `FS_muro_desl=1.5`, `FS_muro_tomb=2.0`, `FS_uplift≥1.0`).

---

## 13. Segurança e conformidade

* Validação estrita de entradas.
* Relatórios com limites de aplicação e cláusulas.
* Sem dados sensíveis.

---

## 14. Roadmap técnico

> **Marco de início:** 28/07/2025 (D0). Prazos indicados em **D+X** e data estimada.

### 14.1 Tabela de entregáveis (Fase 1 — *fundação do core* e UI mínima)

| ID     | Entregável                              | Descrição                                                                                    | Responsável     | Prazo                 | Critério de aceite                                                                                | Dependências                  | Status             |
| ------ | --------------------------------------- | -------------------------------------------------------------------------------------------- | --------------- | --------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------- | ------------------ |
| **R1** | **Radier Pasternak v1**                 | Implementar fundação elástica **Pasternak** com calibração `k, Gp` e validação em caso‑teste | Eng. Estruturas | **D+21 (18/08/2025)** | Caso‑teste bate KPIs do `targets.yaml`; plots de pressão e recalque; snapshot `.md` aprovado      | Geotecnia libs; ReportBuilder | 🔄 Em planejamento |
| **R2** | **`check_uplift()` + testes**           | Empuxo/subpressão, `FS`, margem Δ, **piping**; bloco `uplift.md`; IDs de check padronizados  | Geotecnia       | **D+7 (04/08/2025)**  | `uplift-flutuacao-fs`, `uplift-flutuacao-margin`, `piping-exit-gradient` presentes; testes passam | ReportBuilder, plots          | 🔧 Em execução     |
| **R3** | **Core Lote 1**                         | `solve_viga`, `solve_pilar`, `solve_sapata` com `@log_step`, `Result`, `Report`              | Eng. Estruturas | **D+21 (18/08/2025)** | Golden tests batem; relatório `.md` com cláusulas                                                 | Seção 2 (dataclasses)         | 🗓️ Planejado      |
| **R4** | **Combinações NBR 6120/6123:2023/8681** | Gerador de **ELU/ELS** com `γ/ψ` via YAML, envelope automático                               | Ações/Loads     | **D+25 (22/08/2025)** | Tabelas de combinações replicadas; unit tests com exemplos                                        | R3                            | 🗓️ Planejado      |
| **R5** | **ReportBuilder estável**               | Jinja2, `asdict`, snapshots, bibliografia automática                                         | Dev             | **D+14 (11/08/2025)** | Snapshots ok; deltas exigem `CHANGELOG`                                                           | —                             | ✅ Concluir         |
| **R6** | **Streamlit Lote 1**                    | Páginas `01_Viga`, `02_Pilar`, `03_Sapata`, `14_Subpressao` com download `.md`               | Dev/UI          | **D+28 (25/08/2025)** | Cada página roda caso mínimo; smoke test passa                                                    | R3, R5                        | 🗓️ Planejado      |
| **R7** | **Validação Ouro**                      | Casos de referência: viga, pilar, sapata, subpressão                                         | QA/Eng          | **D+30 (27/08/2025)** | KPIs dentro dos limites do `targets.yaml`                                                         | R3–R6                         | 🗓️ Planejado      |

### 14.2 Tabela de entregáveis (Fase 2 — *escopo ampliado e risco*)

| ID      | Entregável                           | Descrição                                                                               | Responsável          | Prazo                 | Critério de aceite                                            | Dependências          | Status        |
| ------- | ------------------------------------ | --------------------------------------------------------------------------------------- | -------------------- | --------------------- | ------------------------------------------------------------- | --------------------- | ------------- |
| **R8**  | **Silos 1**                          | EN 1991‑4 (enchimento/fluxo), σ_h/σ_v, anel de tração, flambagem local básica, Plotly | Estruturas           | **D+35 (01/09/2025)** | Perfis e envelopes ok; checks normativos presentes            | R5                    | 🗓️ Planejado |
| **R9**  | **Otimização 1**                     | Grid + poda + gulosa; função custo; Pareto custo×aço×deslocamento                       | Dev/Opt              | **D+35 (01/09/2025)** | Top‑3 soluções e gráfico Pareto disponíveis                   | R3                    | 🗓️ Planejado |
| **R10** | **Estacas**                          | Aoki‑Velloso, Décourt‑Quaresma, **NSF**, grupo; blocos (bielas e tirantes)              | Geotecnia            | **D+40 (06/09/2025)** | Confronto com prova de carga exemplo (NBR 16903)              | Parsers `piles_tests` | 🗓️ Planejado |
| **R11** | **Radier Winkler/Pasternak**         | Winkler completo; Pasternak (fase 2) acoplado com rigidez                               | Geotecnia/Estruturas | **D+40 (06/09/2025)** | Convergência de iteração laje–solo; mapas de pressão/recalque | R1, R3                | 🗓️ Planejado |
| **R12** | **Sísmica/Tanques**                  | `actions/seismic.py` + ACI 350.3‑20 (Pi/Pc, Housner)                                    | Estruturas           | **D+40 (06/09/2025)** | Checks `15421-espectro`, `350.3-PiPc`                         | R5                    | 🗓️ Planejado |
| **R13** | **Incêndio NBR 15200**               | Verificação tabular/cálculo e bloco de relatório                                        | Estruturas           | **D+40 (06/09/2025)** | Check `15200-TRRF` e notas de cálculo                         | R5                    | 🗓️ Planejado |
| **R14** | **Monte Carlo / LHS / Sobol / FORM** | Módulo `uql`; Pf, β, IC95%, Sobol S1/ST; hooks de custo×β                               | Risco/Dev            | **D+40 (06/09/2025)** | `N=1000` com IC95%(Pf) ≤ 20%; gráficos Plotly                 | R3, R5                | 🗓️ Planejado |
| **R15** | **Streamlit 2**                      | Abas Confiabilidade e Otimização; relatórios com anexos                                 | Dev/UI               | **D+40 (06/09/2025)** | Smoke tests; downloads `.md`                                  | R8–R14                | 🗓️ Planejado |
| **R16** | **CI/CD Targets**                    | Actions completas com matriz de KPIs (β, wk, FS)                                        | DevOps               | **D+30 (27/08/2025)** | Pipeline bloqueia regressões                                  | R5, R7                | 🗓️ Planejado |

### 14.3 Observações

* Datas são **estimativas** assumindo início em **28/07/2025**; ajuste conforme capacidade.
* **Priorizar R2 → R5 → R3/R4 → R6 → R7** para liberar um MVP auditável.
* `data/targets.yaml` deve ser fechado em conjunto com Engenharia antes de R7.

## 15. Exemplos de uso (dev). Exemplos de uso (dev)

### 15.1 Viga

```python
from estruturas.core.elements.viga import solve_viga
from estruturas.report.builder import build_report
result, report = solve_viga(premissas)
open("relatorio_viga.md","w",encoding="utf8").write(report["markdown"])
```

### 15.2 Monte Carlo em silo

```python
from estruturas.uql.montecarlo import run_monte_carlo_silo
mc = run_monte_carlo_silo(premissas, N=1000, sampler="lhs")
print(mc["pf"], mc["beta"])
```

---

## 16. Orquestração de estrutura (elementos → solo)

Implementada em `orchestration/`.

### 16.1 API

```python
def solve_structure(model: dict) -> dict:
    """Resolve a estrutura inteira, propagando cargas até o solo.
    model = {
      "lajes": [...], "vigas": [...], "pilares": [...],
      "fundacoes": {"sapatas": [...], "radier": {...}, "estacas": [...]},
      "solo": SoilProfile
    }
    return {
      "elements": {...},           # Results por elemento
      "reactions": {...},          # reações por apoio
      "soil": {"pressures": ..., "settlements": ..., "uplift": ...},
      "report": Report             # relatório consolidado
    }
    """
```

### 16.2 Passos

1. Combinações globais.
2. Lajes → Vigas (tributação).
3. Vigas → Pilares (reações).
4. Pilares → Fundações (sapatas/blocos/estacas/radier).
5. Fundações → Solo (pressões, recalques, **subpressão/empuxo** e **NSF**, estabilidade).
6. Consolidação de relatório/plots.

### 16.3 Plots globais (Plotly)

* Barras de reações por pilar.
* Mapa de pressões do radier (`imshow`/`surface`).
* Recalques por apoio.
* Pareto custo × β da estrutura.
* **FS de flutuação** por elemento e **margem Δ = R_d − U_d**.

---

## 17. API de Subpressão/Empuxo (aderente ao Eng v1.1)

```python
def check_uplift(
    A_b: float,
    hw: float,
    gamma_w: float = 9.81,
    Wc: float = 0.0,
    Gperm: float = 0.0,
    Wl: float = 0.0,
    Ta: float = 0.0,
    gamma_G: float = 1.4,
    gamma_U: float = 1.4,
    gamma_T: float = 1.0,
    i_max: float | None = None,
    i_cr: float | None = None,
) -> dict:
    """Retorna {'U_d','R_d','FS','delta','status','piping':{'ratio','status'},'table':...}."""
```

IDs de *checks* associados:

* `uplift-flutuacao-fs` — FS = R_d / U_d ≥ 1,00 (ou meta do projeto).
* `uplift-flutuacao-margin` — Δ = R_d − U_d ≥ 0.
* `piping-exit-gradient` — i_max ≤ i_adm.

O **template padrão** do relatório segue o item 14 do `readme_eng.md` (Tabela de balanço, veredictos e mitigações).

---

## 18. Contato

* **Código / API:** issue com rótulo `dev`.
* **Modelos, normas e hipóteses:** rótulo `eng`.
* **Dados (CSV/YAML, SPT, custos):** rótulo `data`.
* Dúvidas rápidas: referencie o notebook correspondente em `apps/colab/` que reproduz o caso.
