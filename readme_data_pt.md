# readme_data_pt.md — Guia de Dados

Este documento consolida as orientações de **tratamento de dados** mencionadas em `readme_dev_pt.md` e `readme_eng_pt.md`. O objetivo é explicar onde ficam os datasets, como são versionados e de que forma ocorrem a ingestão e a rastreabilidade.

## 1. Estrutura do diretório `data/`

```
data/
  custos.yaml                  # preços unitários (R$/m³, R$/kg, R$/m²)
  premissas_iniciais.yaml      # densidades e resistências típicas
  premissas_normativas.yaml    # normas e coeficientes adotados
  normas/*.yaml                # parametrização de normas (quando houver)
  custos/*.csv                 # custos por região (quando houver)
  materiais_armazenados/*.csv  # cargas armazenadas (opcional)
  geotech/*.csv                # perfis de solo e ensaios
  geotech/calibrations/*.json  # ajustes de correlações de estacas
  vento/                       # valores padrão da NBR 6123:2023
  sismo/                       # classes e espectros da NBR 15421
  estanques.yaml               # limites de wk por uso (ACI 350 / fib)
  targets.yaml                 # metas de β, FS e wk para testes
  compat_matrix.json           # mapeia versão do pacote ↔ datasets
```

Nem todos os arquivos acima estão presentes neste repositório de exemplo, mas a organização segue a recomendação do `readme_dev_pt.md`.

## 2. Versionamento e rastreabilidade

* Cada dataset possui **versão** e **data‑base**.
* O arquivo `compat_matrix.json` registra a compatibilidade entre a versão do pacote e as versões dos datasets.
* Toda execução grava `hash_inputs` — SHA‑256 das premissas combinadas às versões dos dados.
* Os relatórios emitidos exibem essas informações para garantir **reprodutibilidade**.

Trecho de referência no guia do desenvolvedor:

```
* `compat_matrix.json` mapeia versão do pacote ↔ versões dos datasets.
* Cada execução grava `hash_inputs` (sha256 das premissas + versões dos dados).
```

## 3. Ingestão de dados externos

Os parsers localizados em `utils/io_csv.py` e `utils/io_xlsx.py` validam arquivos de entrada com **Pydantic**. Exemplos citados em `readme_dev_pt.md`:

```
prof_top;prof_bot;solo;gamma_nat;gamma_sat;N_SPT;N_corr;cu;phi;E;nu;OCR;k;NA_flag;obs
```

Para provas de carga de estacas:

```
Aba `estacas`: id;tipo;D;L;fck;aco;NA_ini;NA_proj;carga_servico;observacoes
Aba `provas` : id;etapa;kN;mm;tempo(s)
```

Após o parse, correlações podem ser calibradas e salvas em `data/geotech/calibrations/*.json`.

## 4. Valores padrão

Alguns conjuntos trazem valores documentados que podem ser sobrescritos pelo usuário:

* `vento/` — categorias de terreno e fatores topográficos da NBR 6123:2023.
* `sismo/` — espectros‑tipo e classes de importância da NBR 15421.
* `estanques.yaml` — mapeia limites de fissuração `wk` por tipo de uso.
* `targets.yaml` — define metas de β, FS e `wk` usadas em testes automatizados.

## 5. Boas práticas

* Verifique sempre a **data‑base** dos arquivos de custo e norma.
* Mantenha controles de versão atualizados no `compat_matrix.json`.
* Qualquer alteração nos datasets requer atualizar o `hash_inputs` e registrar a nova versão no relatório.
* Para dúvidas específicas de dados, consulte a seção "Suporte" do `readme_eng_pt.md`.

