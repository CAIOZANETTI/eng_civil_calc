# readme\_eng.md — Guia do Engenheiro

Este documento orienta o **uso técnico** do framework para **dimensionamento de estruturas de concreto armado**, **contenções** e **fundações**, com **relatórios didáticos** e, quando necessário, **análise de risco (Monte Carlo)**. O foco é mostrar **hipóteses, entradas, verificações normativas, saídas e limites de aplicação**.

> Regra de ouro: **primeiro conformidade normativa (ELU/ELS)**. Depois, **otimização de custo**. Por fim, **avaliação probabilística** quando o risco e a incerteza justificarem.

---

## 0. Objetivo — 5W2H

**What (o quê):** dimensionar, verificar e detalhar **estruturas de concreto armado, contenções, silos/tanques e fundações**, gerando **relatórios normativos didáticos** e, quando necessário, **análise de risco (Monte Carlo/β)** e **otimização de custo**.

**Why (por quê):** reduzir retrabalho, padronizar critérios de norma, **aumentar transparência técnica** (passo a passo com cláusulas) e **tomar decisões de custo × risco** com base em dados, não em achismo.

**Who (quem usa):** engenheiros estruturais/geotécnicos e coordenadores de projeto. Pode ser usado por orçamentistas para comparar soluções e por gestores para decidir mitigação de risco.

**Where (onde aplica):** projetos de edificações, obras industriais, armazenagem agro, saneamento e infraestrutura leve. Integra com planilhas, Colab e app Streamlit.

**When (quando):** em **pré-dimensionamento** (comparar alternativas), **projeto executivo** (relatório normativo) e **value engineering** (otimização/risco). É útil também em revisões independentes.

**How (como):**

1. Informar **premissas** (geometria, materiais, ações, solo, ambiente, normas, custos).
2. Rodar o **solver normativo** (ELU/ELS) → obter **checks com cláusulas**.
3. (Opcional) Rodar **otimização** para custo mínimo entre soluções viáveis.
4. (Opcional) Rodar **Monte Carlo/LHS** → calcular **Pf, β, IC** e **sensibilidade (Sobol)**.
5. Exportar **relatório Markdown** com fórmulas LaTeX e substituições numéricas.

**How much (quanto):** custo computacional baixo para o núcleo (milissegundos a segundos por elemento). Monte Carlo típico: **N=1.000** cenários em **minutos** em notebook comum; com LHS/Sobol ou FORM, reduz-se o tempo. Custos de materiais são lidos de CSV (R\$/m³, R\$/kg, R\$/m²) e compõem o **custo total da solução**.

---

## 1. Escopo coberto

### 1.1 Superestrutura — concreto armado

* **Vigas**: flexão, cisalhamento, torção (quando aplicável), ELS (flechas e fissuração), detalhamento (cobrimento, bitola, espaçamentos, ancoragens/emendas).
* **Lajes**: unidirecionais e maciças; flechas imediatas e diferidas; fissuração; verificação de punção em apoios/pilares.
* **Pilares**: N–M–M, esbeltez, 2ª ordem aproximada (amplificação), ELS de deslocamentos e detalhamento.
* **Cascas/Paredes**: casca cilíndrica de silo/tanque; esforços de membrana, tração anular, flambagem local e fissuração.

### 1.2 Armazenamento

* **Silos de grãos (casco de concreto)**: casos de carregamento de **enchimento**, **fluxo** e **descarga excêntrica**; perfis de pressão; tensões de membrana; anéis de tração; flambagem; fissuração; deslocamentos; **envelope normativo**.
* **Tanques de água/esgoto**: pressão hidrostática; anéis de tração; fissuração para estanqueidade; deslocamentos.

### 1.3 Contenções

* **Muros de arrimo** em concreto: empuxos ativo/passivo; sobrecargas; estabilidade (deslizamento, tombamento, capacidade de apoio); dimensionamento; fissuração; detalhamento.

### 1.4 Fundações e interação solo–estrutura

* **Sapatas** (isoladas/corridas): capacidade de carga (métodos clássicos), punção, pressões de contato, recalques (elástico/consolidação) e verificação contra flutuação/subpressão.
* **Radier** (placa sobre fundação elástica): modelo de Winkler (fase 1) e Pasternak (fase 2); pressões de contato, recalques e compatibilização com a superestrutura.
* **Estacas**: capacidade de carga por correlações usuais (SPT), prova de carga, **atrito negativo (NSF)**, eficiência de grupo e verificação estrutural do fuste.
* **Blocos sobre estacas**: bielas e tirantes, esmagamento, ancoragens e cisalhamento.
* **Melhoria de solos (paramétrico)**: **jet grouting** (famílias, diâmetros e ganhos), drenos verticais (tempo de consolidação) e compactação (ganhos típicos).

---

## 2. Normas e referências utilizadas

* **Ações e combinações**: NBR 6120 (pesos e sobrecargas), **NBR 6123:2023** (vento), NBR 8681 (combinações; γ e ψ).
* **Concreto armado**: **NBR 6118** — dimensionamento (ELU/ELS), durabilidade (classes de agressividade, a/c mínima, fck mínimo), cobrimentos, detalhamento, taxas mín./máx., fissuração e deslocamentos.
* **Fundações**: **NBR 6122** — critérios para sapatas, estacas, blocos, atrito negativo, provas de carga, segurança à ruptura e recalques.
* **Materiais e execução**: **NBR 7480** (aço para armaduras), **NBR 12655** (concreto — preparo/controle), **NBR 14931** (execução de estruturas de concreto).
* **Silos e tanques**: **EN 1991‑4** (ações em silos e tanques) e **ACI 313‑16** (projeto de silos de concreto) como referências complementares; dimensionamento em concreto conforme NBR 6118. Quando as prescrições diferirem, adota‑se o **envelope mais desfavorável** justificado em relatório.

> Todas as cláusulas usadas são **citadas no relatório** (seção “Referências normativas”), com **ano/versão** e **seção/tabela** correspondente.

---

## 3. Hipóteses de modelo (por família de elemento)

### 3.1 Vigas e lajes

* Concreto **normal** (massa específica típica) e aço CA‑50/CA‑60.
* Estados limites: **ELU** (flexão, cisalhamento e torção quando previsto) e **ELS** (flecha total/ativa, fissuração com limites por classe de agressividade).
* Efeitos de fluência e retração tratados conforme NBR 6118 para deslocamentos de longo prazo.
* Ligações viga–pilar consideradas rígidas no cálculo manual; quando necessário, considerar redistribuições compatíveis com a norma.

### 3.2 Pilares

* Análise N–M–M com **2ª ordem aproximada** (amplificação) para pilares esbeltos; limites de esbeltez conforme NBR 6118.
* Diagramas de interação coerentes com o domínio de deformações da norma.
* Critérios de confinamento, taxa mínima e ancoragens compatíveis com durabilidade e detalhamento.

### 3.3 Muros de arrimo

* Empuxo **ativo** (condição usual) ou **em repouso** quando não é possível alívio lateral; passivo mobilizado apenas quando justificável.
* Sobre cargas superficiais incluídas como linhas/equipamentos/aterros.
* Estabilidade global verificada, com critério de **capacidade de apoio** e **punção** na base.

### 3.4 Silos e tanques (cascas)

* Silos: pressão lateral conforme **situações de enchimento, fluxo e descarga excêntrica**. Consideram‑se **coeficiente de Janssen (k)**, **atrito parede (μ)**, densidade aparente e coeficientes de modelo.
* Tensões membranares **σ\_h (anel)** e **σ\_v (meridiano)** avaliadas ao longo da altura; verificação de **anel de tração**, **flambagem local** e **fissuração** (estanques quando requerido).
* Tanques: pressão hidrostática, ações térmicas/vento quando pertinentes, fissuração limitada para estanqueidade.

### 3.5 Fundações

* **Sapatas**: capacidade por métodos clássicos (Terzaghi/Meyerhof/Vesic) e **recalques** (Schmertmann/elástico).
* **Estacas**: capacidade axial por **Aoki‑Velloso**, **Décourt‑Quaresma** (e outros, quando aplicável); consideração explícita de **atrito negativo** quando houver possibilidade de adensamento/rebaixamento.
* **Radier**: placa sobre **fundação elástica** (Winkler, fase 1; Pasternak na fase 2). Interação com superestrutura por iteração de rigidezes.
* **Blocos sobre estacas**: modelo de **bielas e tirantes** (compressão no concreto, tração nas armaduras), verificação de ancoragens e esmagamentos.

---

## 4. Entradas necessárias

### 4.1 Geometria

* Dimensões principais do elemento (ex.: viga: b, h, L; casca de silo: diâmetro **D**, altura **H**, espessura **t** por faixas).
* Posições de aplicação de cargas/restrições, quando relevantes.

### 4.2 Materiais

* Concreto: **fck** (e idade de verificação), módulo, classe de consistência se pertinente.
* Aço: **fyk** (CA‑50/CA‑60), módulo.
* Protensão (se usada futuramente): fptk, perdas, traçado.

### 4.3 Ambiente e durabilidade

* **Classe de agressividade ambiental** e **vida útil de projeto**.
* O sistema calcula **cobrimento nominal c\_nom** a partir das tabelas normativas (inclui ∆c\_exec).

### 4.4 Ações e combinações

* Pesos próprios, sobrecargas (categorias de uso), vento (parâmetros da 6123:2023), empuxos/pressões específicas (silos/tanques), temperatura quando aplicável.
* O sistema gera **combinações ELU/ELS** com **γ/ψ** conforme norma e monta o **envelope**.

### 4.5 Solo (quando houver fundação)

* **Perfil estratigráfico** com propriedades por camada: γ\_nat/γ\_sat, N\_SPT e correções, **φ**, **cu**, **E**, **ν**, permeabilidade **k**, **nível d’água**.
* Observações de obra (adensamento esperado, sobrecargas permanentes, rebaixamento do NA).

### 4.6 Custos (para otimização)

* R\$/m³ de concreto (por fck), R\$/kg de aço (CA‑50/CA‑60), R\$/m² de forma e fatores de produtividade.
* Para **análise probabilística**, custos podem ser definidos com **distribuições** e **correlação**.

---

## 5. Saídas e critérios de aprovação

### 5.1 Saídas principais

* **KPIs**: status geral (aprovado/reprovado), razões de utilização, quantidades de aço/concreto, custo estimado.
* **Checks normativos**: lista com `valor`, `limite`, `status`, `margem` e **cláusula/tabela**.
* **Tabelas auxiliares**: combinações ELU/ELS, perfis de pressão, tensões por altura, pressões de contato (radier/sapata), recalques.
* **Gráficos Plotly**: perfis, envelopes, histogramas/ECDF (quando Monte Carlo), Pareto custo×aço×deslocamento.
* **Relatório Markdown**: cabeçalho, dados de entrada, fórmulas em LaTeX, **substituições numéricas passo a passo**, verificações, detalhamento, custo e referência às cláusulas.

### 5.2 Aprovação

* **ELU**: todas as verificações resistentes devem atender `E_d ≤ R_d` com os **fatores parciais** aplicáveis.
* **ELS**: deslocamentos e abertura de fissuras dentro dos **limites por classe de agressividade/uso**.
* **Durabilidade**: cobrimentos, a/c, fck mínimo e detalhamento compatíveis com a classe de agressividade e vida útil.
* **Fundações**: segurança à ruptura (capacidade), **recalques admissíveis**, **NSF** considerado quando aplicável, estabilidade global e subpressão.
* **Silos/tanques**: todos os **casos de carregamento** verificados; adota‑se o **envelope** entre normas quando houver divergência.

---

## 6. Exemplo resumido de fluxo — viga retangular (Md conhecido)

1. Informar `b, h, L`, `fck`, `fyk`, classe de agressividade, `Md`, `Vd` e custos.
2. Sistema calcula `fcd`, `fyd`, `c_nom` e limites de fissuração.
3. Dimensiona **As\_req** (flexão) e verifica **corte** (estribos) e **flecha**/fissuração.
4. Propõe detalhamento (bitola e espaçamentos), checa cobrimento e emendas.
5. Gera relatório `.md` com passos, fórmulas e substituições numéricas.
6. Se habilitado, varre alternativas de bitola/espessura/fck e apresenta **Top 3** por custo.

---

## 7. Exemplo resumido — silo de soja (D, H, t)

1. Informar `D`, `H` e **faixas de espessura t**; materiais (fck/fyk), ambiente, propriedades do grão (γ, k, μ).
2. Sistema gera **pressões** para **enchimento**, **fluxo** e **excêntrico** (para ambos os referenciais) e produz o **envelope**.
3. Calcula **σ\_h, σ\_v**, verifica **anel de tração**, **flambagem local** e **fissuração** por faixas de altura.
4. Monta detalhamento horizontal/vertical por anéis; consolida consumo de aço e concreto.
5. Se habilitado, roda **otimização** (custo mínimo) e/ou **Monte Carlo** (Pf, β, Sobol), reportando gráficos Plotly e impactos de mitigação.

---

## 8. Limites de aplicação e boas práticas

* Aplicável a **concreto normal**; concretos especiais (leve, pesado, alta resistência, fibras) exigem validação específica.
* Em **situações não usuais** (sismo relevante, temperatura diferencial crítica, impacto/choque, fadiga, efeitos dinâmicos de fluxo), consultar especialista e validar hipóteses.
* Em **solos moles** espessos (camadas compressíveis > 6–7 m), priorizar avaliação de recalques (imediatos e de consolidação) e **NSF** nas estacas.
* **Silos muito altos**: atenção a flambagem, tolerâncias geométricas e ao controle de fissuração/estanques.
* **Dados de entrada mandam no resultado**: use SPT/provas de carga sempre que possível; evite extrapolações sem justificativa.

---

## 9. Checklist antes da emissão

1. **Normas e versões** confirmadas nas premissas.
2. **Classe de agressividade** correta e **cobrimento nominal** coerente.
3. **Combinações** revisadas (ELU/ELS) e casos de carregamento especiais listados.
4. **Relatório .md** revisado: fórmulas, substituições, cláusulas citadas e conclusões.
5. **Fundações**: capacidade, recalques, NSF, estabilidade global e subpressão checadas.
6. **Silos/tanques**: envelope entre referenciais registrado e justificado.
7. **Custos**: data-base, fonte e eventuais correções regionais anotadas.
8. **Assinatura e responsabilidade técnica**: revisão por engenheiro responsável.

---

## 10. Sobre análise probabilística (quando usar)

* Use **Monte Carlo** quando:

  * variáveis chave têm grande variabilidade (ex.: `k`, `μ`, pressão de fluxo);
  * a consequência da falha é alta;
  * você precisa **hierarquizar mitigadores** (qual variável mais influencia o risco);
  * deseja reportar **β** (alvo de confiabilidade) ou **intervalos de confiança** de um KPI.
* **Critério de falha**: qualquer verificação crítica reprovada (ELU/ELS/detalhamento/NSF), definido explicitamente no relatório.
* **Saída**: `Pf`, `β`, IC 95% (Clopper–Pearson), índices de Sobol, curva custo×β.
* **Importante**: a análise probabilística **não substitui** a conformidade normativa; ela **complementa** a decisão de projeto.

---

## 11. Versionamento e rastreabilidade

* Cada resultado grava **hash das entradas**, **versão do pacote** e **versões dos datasets** (normas/custos/solos).
* O relatório lista as **cláusulas usadas**. Alterações de norma/dataset devem gerar **nova versão** do estudo.

---

## 12. Suporte e dúvidas

* Dúvidas de **modelo estrutural ou geotécnico**: revisar hipóteses na seção 3 e as cláusulas citadas no relatório.
* Dúvidas de **dados**: conferir arquivos CSV/YAML em `data/` (normas, custos, materiais armazenados, solos) e a data-base.
* Para casos fora do escopo ou com dinâmica complexa, recomenda-se revisão independente por especialista.
