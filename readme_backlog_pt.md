# readme_backlog_pt.md — Roteiro inicial

Este documento resume uma **sequência sugerida** para desenvolver o framework descrito nos guias de engenheiro e de desenvolvedor.

1. **Preparar o repositório**
   - Estruture pastas conforme `readme_dev_pt.md` (`src/estruturas/`, `data/`, `apps/`, `tests/`).
   - Defina um arquivo `pyproject.toml` com dependências básicas (`pydantic`, `pytest`, `streamlit`, `plotly`).

2. **Modelos de entrada e premissas**
   - Crie modelos **Pydantic** para validar premissas (materiais, geometria, solo). Baseie‑se em `premissas_iniciais.yaml` e `premissas_normativas.yaml`.
   - Guarde valores padrão em `data/` e versionados conforme orientações de `readme_data_pt.md`.

3. **Funções de cálculo (core)**
   - Implemente funções puras em `src/estruturas/core/` seguindo o padrão `@dataclass(slots=True, frozen=True)`.
   - Cada função deve retornar dicionário com resultados e referências de cláusulas normativas.

4. **Testes automatizados**
   - Escreva testes **pytest** em `tests/unit/` para cada função do núcleo.
   - Utilize `tests/validation/` para checar exemplos completos (snapshot ou tolerância numérica).

5. **Notebooks Colab para experimentos**
   - Crie notebooks em `apps/colab/` demonstrando o uso das funções e a validação das premissas.
   - Use gráficos Plotly para visualizar resultados (cargas, tensões, verificações).

6. **Interface Streamlit**
   - Transfira os experimentos validados para `apps/streamlit/`.
   - Cada elemento (viga, pilar, sapata etc.) deve ter uma página dedicada em `pages/`.

7. **Validação e publicação**
   - Gere relatórios Markdown a partir dos resultados e compare com valores de referência.
   - Inclua uma matriz de compatibilidade dos datasets (`compat_matrix.json`).
   - Só depois de validado em Colab e nos testes unitários publique a interface Streamlit final.

Este roteiro serve como ponto de partida e deve ser refinado de acordo com as metas de cada sprint.
