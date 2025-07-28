# readme\_eng.md — Guia do Engenheiro (v1.1)

Este documento orienta o **uso técnico** do framework para **dimensionamento de estruturas de concreto armado**, **contenções** e **fundações**, com **relatórios didáticos** e, quando necessário, **análise de risco (Monte Carlo)**. O foco é mostrar **hipóteses, entradas, verificações normativas, saídas e limites de aplicação**.

> **Regra de ouro**: **primeiro conformidade normativa (ELU/ELS)**. Depois, **otimização de custo**. Por fim, **avaliação probabilística** quando o risco e a incerteza justificarem.

---

## 0. Objetivo — 5W2H

**What (o quê):** dimensionar, verificar e detalhar **estruturas de concreto armado, contenções, silos/tanques e fundações**, gerando **relatórios normativos didáticos** e, quando necessário, **análise de risco (Monte Carlo/β)** e **otimização de custo**.

**Why (por quê):** reduzir retrabalho, padronizar critérios de norma, **aumentar transparência técnica** (passo a passo com cláusulas) e **tomar decisões de custo × risco** com base em dados.

**Who (quem usa):** engenheiros estruturais/geotécnicos e coordenadores de projeto. Pode ser usado por orçamentistas para comparar soluções e por gestores para decidir mitigação de risco.

**Where (onde aplica):** edificações, obras industriais, armazenagem agro, saneamento e infraestrutura leve. Integra com planilhas CSV/Excel, Google Colab e app Streamlit.

**When (quando):** **pré-dimensionamento** (comparar alternativas), **projeto executivo** (relatório normativo) e **value engineering** (otimização/risco). Útil em revisões independentes.

**How (como):**

1. Informar **premissas** (geometria, materiais, ações, solo, ambiente, normas, custos).
2. Rodar o **solver normativo** (ELU/ELS) → obter **checks com cláusulas**.
3. (Opcional) Rodar **otimização** para custo mínimo entre soluções viáveis.
4. (Opcional) Rodar **Monte Carlo/LHS/FORM** → calcular **Pf, β, IC** e **sensibilidade (Sobol)**.
5. Exportar **relatório Markdown** com fórmulas LaTeX e substituições numéricas.

**How much (quanto):** núcleo determinístico em **ms–s por elemento**. Monte Carlo típico: **N = 1.000** cenários em **minutos** em notebook comum; com **LHS/Sobol/FORM** reduz-se o tempo. Custos lidos de CSV (R\$/m³, R\$/kg, R\$/m²) compõem o **custo total** da solução.

---

## 0.1 Arquitetura do framework

**Camadas:**

1. **Core normativo (`core/`)** — funções puras com verificações de ELU/ELS e **cláusulas citadas**.
2. **Modelos de elemento (`elements/`)** — viga, laje, pilar, muro, casca de silo/tanque, sapata, estaca, bloco, radier. Cada elemento expõe: `solve()`, `checks()`, `detail()`, `cost()`.
3. **Interação solo–estrutura (`soil/`)** — capacidade, recalques, NSF, subpressão e acoplamento com radier/sapatas.
4. **Combinações e ações (`loads/`)** — NBR 6120/6123/8681 + casos especiais (silos/tanques).
5. **Otimização e risco (`opt/`, `risk/`)** — busca discreta/contínua, Monte Carlo, LHS, **FORM** e **Sobol**.
6. **Relatórios (`reports/`)** — gerador `.md` com LaTeX, números substituídos e tabela de referências.
7. **Dados (`data/`)** — normas parametrizadas, custos, materiais, solos. Todos com **versão e data‑base**.
8. **Apps (`apps/`)** — notebooks **Colab** e **UI Streamlit** (Plotly para gráficos interativos).
9. **Qualidade (`tests/`, CI)** — **pytest** + testes de regressão numérica; linters; exemplos validados.

---

## 0.2 Princípio de composição — "estrutura como rede de elementos"

Uma estrutura é construída por **elementos interligados**:

> **cargas → lajes → vigas → pilares → blocos/sapatas/estacas/radier → solo**

O framework **propaga esforços** ao longo desse caminho resistente e **retroalimenta** o modelo quando há **recalques** relevantes (ex.: radier elástico alterando o esforço nos pilares). Em cada etapa:

* cada elemento **consome ações** das etapas anteriores;
* executa **verificações normativas locais**;
* devolve **resultados e rigidez equivalente** para o acoplamento com o próximo nível;
* registra **KPIs e custos** para compor o **custo total** e o **risco sistêmico**.

---

## 1. Escopo coberto

### 1.1 Superestrutura — concreto armado

* **Vigas**: flexão, cisalhamento, torção (quando aplicável), ELS (flechas e fissuração), detalhamento (cobrimento, bitola, espaçamentos, ancoragens/emendas).
* **Lajes**: unidirecionais e maciças; flechas imediatas e diferidas; fissuração; punção em apoios/pilares.
* **Pilares**: N–M–M, esbeltez, 2ª ordem aproximada (amplificação), ELS de deslocamentos e detalhamento.
* **Cascas/Paredes**: casca cilíndrica de silo/tanque; esforços de membrana, tração anular, flambagem local e fissuração.

### 1.2 Armazenamento

* **Silos de grãos (casco de concreto)**: carregamentos de **enchimento**, **fluxo** e **descarga excêntrica**; perfis de pressão; tensões de membrana; anéis de tração; flambagem; fissuração; deslocamentos; **envelope normativo**.
* **Tanques de água/esgoto**: pressão hidrostática; anéis de tração; fissuração para estanqueidade; deslocamentos.

### 1.3 Contenções

* **Muros de arrimo**: empuxos ativo/repouso; sobrecargas; estabilidade (deslizamento, tombamento, capacidade de apoio); dimensionamento; fissuração; detalhamento.

### 1.4 Fundações e interação solo–estrutura

* **Sapatas**: capacidade (Terzaghi/Meyerhof/Vesic), punção, pressões de contato, recalques (elástico/consolidação) e flutuação/subpressão.
* **Radier**: placa sobre **fundação elástica** (Winkler, fase 1; Pasternak, fase 2). Iteração com superestrutura.
* **Estacas**: capacidades **Aoki‑Velloso**, **Décourt‑Quaresma**, outras quando aplicável; **atrito negativo (NSF)**; grupo e verificação estrutural do fuste.
* **Blocos sobre estacas**: **bielas e tirantes**, esmagamento, ancoragens e cisalhamento.
* **Melhoria de solos (paramétrico)**: **jet grouting**, drenos verticais (tempo de consolidação) e compactação.

---

## 2. Normas e referências utilizadas

* **Ações e combinações**: NBR 6120 (pesos e sobrecargas), **NBR 6123:2023** (vento), NBR 8681 (combinações; γ e ψ), **EN 1990** (bases de projeto e confiabilidade – β‑alvos por classe de consequência, usado como referência).
* **Concreto armado**: **NBR 6118** — dimensionamento (ELU/ELS), durabilidade (CAA, a/c mínima, fck mínimo), cobrimentos, detalhamento, taxas mín./máx., fissuração e deslocamentos.
* **Fundações**: **NBR 6122:2022** — consolida a versão 2019 com a **Emenda 1:2022**. Sapatas, estacas, blocos, **atrito negativo (AN/NSF)**, provas de carga, segurança à ruptura e recalques.
* **Provas de carga**: **NBR 16903:2020** (prova de carga **estática** em fundação profunda, **revoga a NBR 12131:2006**); **NBR 13208:2007** (prova de carga **dinâmica**); **NBR 6489:2019** (prova de carga **estática em fundação direta – ensaio de placa**).
* **Estabilidade de encostas/taludes**: **NBR 11682:2009** — estudo e controle da **estabilidade global (FS)**.
* **Ações sísmicas**: **NBR 15421** — procedimentos e requisitos para verificação da segurança de estruturas usuais. Para tanques/estruturas ambientais, complementar com **ACI 350.3‑20** (componentes **impulsivo** e **convectivo** — método de **Housner**).
* **Incêndio**: **NBR 15200** — projeto de estruturas de concreto em situação de incêndio (método tabular e cálculo; TRRF).
* **Impermeabilização**: **NBR 9575:2010** (seleção e projeto) e **NBR 9574:2008** (execução). Ensaio de **estanqueidade 72 h** após a execução.
* **Materiais e execução**: **NBR 7480** (aço), **NBR 12655** (concreto — preparo/controle), **NBR 14931** (execução). Para tolerâncias construtivas internacionais, **ACI 117** (quando contratualmente requerido).
* **Silos e tanques**: **EN 1991‑4** (ações em silos/tanques) e **ACI 313‑16** (projeto de silos de concreto). Para revisão crítica de falhas e carregamentos, literatura de **Rotter**.
* **Estanqueidade e fissuração**: **ACI 350** (estruturas ambientais — **wk≈0,10 mm** como diretriz), **ACI 224R‑01** (larguras recomendáveis). Para SLS avançado, **fib Model Code 2010** / **fib Bulletin 92**.
* **Confiabilidade estrutural**: **EN 1990** e **fib Model Code 2010** — metas de **β** por classe de consequência e vida de projeto; integração com **Monte Carlo/FORM**.
* **Subpressão e piping** (referências complementares): **USACE EM 1110‑2‑1901** (seepage; **exit gradient** e controle de subpressão), **USACE EM 1110‑2‑2100** (estabilidade de estruturas de concreto), **NAVFAC DM‑7.02** (FS típicos para muros — deslizamento/tombamento).

> As **cláusulas** são **citadas no relatório** (seção “Referências normativas”), com **ano/versão** e **seção/tabela**. Declarar explicitamente **NBR 6122:2022**, **NBR 6123:2023** e, quando aplicável, **NBR 15421** e **NBR 15200**.

---

## 3. Hipóteses de modelo (por família de elemento)

### 3.1 Vigas e lajes

* Concreto **normal** e aço CA‑50/CA‑60.
* Estados limites: **ELU** (flexão, cisalhamento, torção quando previsto) e **ELS** (flecha total/ativa, fissuração com limites por classe de agressividade).
* Fluência e retração conforme NBR 6118 nos deslocamentos de longo prazo.
* Ligações viga–pilar consideradas rígidas no cálculo manual; redistribuições conforme norma quando necessário.

### 3.2 Pilares

* Análise N–M–M com **2ª ordem aproximada** (amplificação) para esbeltos; limites de esbeltez NBR 6118.
* Diagramas de interação coerentes com o domínio de deformações da norma.
* Confinamento, taxas mínimas e ancoragens compatíveis com durabilidade.

### 3.3 Muros de arrimo

* Empuxo **ativo** (usual) ou **repouso** quando não há alívio; passivo só quando justificável.
* Sobrecargas de superfície (linhas/equipamentos/aterros) consideradas.
* Estabilidade global, **capacidade de apoio** e **punção** na base.

### 3.4 Silos e tanques (cascas)

* Silos: pressões para **enchimento**, **fluxo** e **descarga excêntrica**. Parâmetros: **k (Janssen)**, **μ (atrito)**, densidade aparente e coeficientes de modelo.
* Tensões membranares **σ\_h (anel)** e **σ\_v (meridiano)** ao longo da altura; **anel de tração**, **flambagem** e **fissuração** (estanques quando requerido).
* Tanques: pressão hidrostática; ações térmicas/vento quando pertinentes; fissuração limitada para estanqueidade.

### 3.5 Fundações

* **Sapatas**: capacidade por métodos clássicos (Terzaghi/Meyerhof/Vesic) e **recalques** (Schmertmann/elástico). Verificar ainda **punção**, **pressões de contato** e **subpressão** quando houver **lençol freático** elevado ou **sobrepressão de poros**. Em obras sujeitas a **cheias** ou **rebaixamento do NA**, avaliar **flutuação** (empuxo ascensional) e, se necessário, dimensionar **lastro**, **tirantes de ancoragem** ou **aumento de peso próprio**.
* **Radier**: placa sobre **fundação elástica** (Winkler, fase 1; Pasternak, fase 2). Considerar **subpressão na laje de fundo** e o **empuxo de água no subsolo**, com verificação do equilíbrio global (peso próprio + sobrecargas permanentes + ancoragens ≥ empuxo), incluindo **fatores parciais** adequados. Iterar com a superestrutura por rigidezes.
* **Estacas**: capacidade axial por **Aoki‑Velloso**, **Décourt‑Quaresma** (e outros, quando aplicável); consideração explícita de **atrito negativo (AN/NSF)** quando houver possibilidade de adensamento/rebaixamento. Avaliar **eficiência de grupo** e verificação **estrutural do fuste** (compressão, tração e cisalhamento). Provas de carga conforme NBR 6122.
* **Blocos sobre estacas**: modelo de **bielas e tirantes** (compressão no concreto, tração nas armaduras), verificação de **ancoragens**, **esmagamento** e **cisalhamento**.
* **Estabilidade global**: quando o elemento interage com taludes/aterros, verificar **FS global** segundo **NBR 11682** e registrar no relatório.

### 3.6 Ações sísmicas (quando aplicável)

* Aplicar **NBR 15421** para definição de espectros e combinações sísmicas, de acordo com a periculosidade regional, classe de importância e tipo estrutural.
* Em **estruturas de reservação** e tanques, aplicar **ACI 350.3‑20** para cálculo de **pressões hidrodinâmicas** (componentes **impulsivo Pi** e **convectivo/sloshing Pc**, método de **Housner**), esforços de ancoragem e verificação de altura de onda/livre bordo.
* Em **silos**, avaliar amplificação inercial do conteúdo e compatibilizar com EN 1991‑4 quando necessário.
* Quando a ação sísmica for desprezável pelo zoneamento, **registrar a justificativa** formalmente nas premissas.

---

## 4. Entradas necessárias

### 4.1 Geometria

* Dimensões do elemento (ex.: viga: `b, h, L`; casca de silo: **D**, **H**, **t** por faixas).
* Posições de cargas e restrições, quando relevantes.

### 4.2 Materiais

* Concreto: **fck** (e idade), módulo; classe de consistência se pertinente.
* Aço: **fyk** (CA‑50/CA‑60), módulo.
* Protensão (futuro): fptk, perdas, traçado.

### 4.3 Ambiente e durabilidade

* **Classe de agressividade** e **vida útil**. O sistema calcula **cobrimento nominal c\_nom** pelas tabelas normativas (inclui ∆c\_exec).

### 4.4 Ações e combinações

* Pesos próprios, sobrecargas, **vento (6123:2023)**, empuxos/pressões (silos/tanques), temperatura.
* Geração automática de **combinações ELU/ELS** com **γ/ψ** e **envelope**.

### 4.5 Solo

* **Estratigrafia** com γ\_nat/γ\_sat, **N\_SPT** e correções, **φ**, **cu**, **E**, **ν**, **k**, **NA** e observações (adensamento, sobrecargas, rebaixamento).

### 4.6 Custos

* R\$/m³ concreto (por fck), R\$/kg aço (CA‑50/60), R\$/m² forma, produtividade.
* Em análises probabilísticas, custos com **distribuições** e **correlação**.

---

## 5. Saídas e critérios de aprovação

### 5.1 Saídas

* **KPIs**: status (aprovado/reprovado), razões de utilização, consumos, **custo estimado**.
* **Checks**: `valor`, `limite`, `status`, `margem`, **cláusula/tabela**.
* **Tabelas**: combinações ELU/ELS, perfis de pressão, tensões por altura, pressões de contato, recalques.
* **Gráficos Plotly**: perfis/envelopes, histogramas/ECDF (Monte Carlo), Pareto custo×aço×deslocamento.
* **Relatório Markdown**: cabeçalho, entradas, **fórmulas LaTeX com substituições**, verificações, detalhamento, custo e referências.

### 5.2 Aprovação

* **ELU**: todas as verificações resistentes devem atender `E_d ≤ R_d` com os **fatores parciais** aplicáveis.
* **ELS**: deslocamentos e abertura de fissuras dentro dos **limites por classe de agressividade/uso**. Para estruturas **estanques/ambientais**, adotar **wk alvo típico = 0,10 mm (ACI 350)**, salvo justificativa técnica distinta registrada no relatório.
* **Durabilidade**: cobrimentos, a/c, fck mínimo e detalhamento compatíveis com a classe de agressividade e vida útil.
* **Fundações**: segurança à ruptura (capacidade), **recalques admissíveis**, **NSF** considerado quando aplicável, **subpressão/empuxo** verificados, estabilidade global (**NBR 11682**) e flutuação controlada (lastros/ancoragens quando necessário).
* **Silos/tanques**: todos os **casos de carregamento** verificados; adota‑se o **envelope** entre normas quando houver divergência.
* **Confiabilidade (quando aplicável)**: reportar **Pf** e **β**. Recomenda‑se, como referência, **β\_ULS ≈ 3,8** para classe de consequência **CC2** e vida de **50 anos** (padrão EN 1990). Para ELS, adotar **β\_SLS ≈ 1,5** como guia. Valores podem ser ajustados conforme criticidade; o relatório deve **declarar o alvo adotado**.

---

## 6. Exemplo de fluxo — viga retangular (M\_d conhecido)

1. Informar `b, h, L`, `fck`, `fyk`, classe de agressividade, `M_d`, `V_d` e custos.
2. Sistema calcula `fcd`, `fyd`, `c_nom` e limites de fissuração.
3. Dimensiona **A\_s,req** (flexão) e verifica **corte** (estribos) e **flecha**/fissuração.
4. Propõe detalhamento (bitola e espaçamentos), checa cobrimento e emendas.
5. Gera relatório `.md` com passos e **cláusulas**.
6. (Opcional) Varre bitola/espessura/fck e apresenta **Top 3** por custo.

---

## 7. Exemplo de fluxo — silo de soja (D, H, t)

1. Informar `D`, `H` e **faixas t**; materiais (fck/fyk), ambiente, propriedades do grão (γ, k, μ).
2. Gerar **pressões** para **enchimento**, **fluxo** e **excêntrico** (em ambos os referenciais) e produzir o **envelope**.
3. Calcular **σ\_h, σ\_v**, verificar **anel de tração**, **flambagem** e **fissuração** por faixas de altura.
4. Montar detalhamento horizontal/vertical; consolidar consumos de aço e concreto.
5. (Opcional) **Otimização** (custo mínimo) e/ou **Monte Carlo** (Pf, β, Sobol) com gráficos Plotly.

---

## 8. Limites de aplicação e boas práticas

* Aplicável a **concreto normal**; concretos especiais (leve, pesado, alta resistência, fibras) exigem validação específica.
* Em **situações não usuais** (sismo relevante, temperatura diferencial crítica, impacto/choque, fadiga, dinâmica de fluxo), validar hipóteses com especialista.
* Em **solos moles** espessos (> 6–7 m), priorizar **recalques** (imediatos e consolidação) e **NSF** nas estacas.
* **Silos altos**: atenção a flambagem, tolerâncias e controle de fissuração/estanques.
* **Entrada manda no resultado**: use SPT/provas de carga sempre que possível; evite extrapolações sem lastro.

---

## 9. Checklist antes da emissão

1. **Normas e versões**: 6118, 6120, **6123:2023**, 8681, **6122:2022**, **11682**, **15421** (se aplicável), **15200** (incêndio, se aplicável), EN 1991‑4, ACI 313, **ACI 350/350.3** (estanques/sismo). Declarar **EN 1990/fib MC2010** quando usar metas de β.
2. **Vento (6123:2023)**: registrar **V0 (isopletas)**, **direção de projeto**, **categoria de terreno**, **fator topográfico**, **altura de referência** e, quando cabível, **avaliação dinâmica**.
3. **Classe de agressividade e cobrimento**: CAA correta; **c\_nom** calculado; limites de **wk** impressos (e **wk=0,10 mm** para estanques quando aplicável).
4. **Fundações**: capacidade, **recalques**, **NSF**, **subpressão/empuxo** (peso próprio + sobrecargas + lastro/ancoragem ≥ empuxo), **FS global (NBR 11682)**.
5. **Provas de carga**: especificar plano conforme **NBR 16903 (estática em estacas)**, **NBR 13208 (dinâmica/PDA)** e **NBR 6489 (placa)** — com critérios de aceitação/correlação.
6. **Muros de arrimo**: declarar **FS de referência** (ex.: **deslizamento ≥1,5; tombamento ≥2,0**) com base em **NAVFAC/USACE**, e verificar tensões de apoio.
7. **Sismo (NBR 15421/ACI 350.3)**: aplicabilidade avaliada e declarada; para tanques, checar **Pi/Pc**, **ancoragens** e **livre bordo**.
8. **Incêndio (NBR 15200)**: exigir **TRRF** do cliente/legislação e verificar método tabular/cálculo quando aplicável.
9. **Impermeabilização**: **NBR 9575/9574**; prever **ensaio de estanqueidade (72 h)** no plano de controle.
10. **Relatório .md**: fórmulas, substituições numéricas, **cláusulas citadas**, conclusões e responsabilidades.
11. **Custos**: data‑base, fonte e correções regionais; premissas de produtividade.
12. **Rastreabilidade**: hash das entradas, versão do pacote e datasets; data/hora; usuário.
13. **Execução e tolerâncias**: **NBR 14931** e, se contratualmente exigido, **ACI 117**.
14. **Revisão técnica**: validação por engenheiro responsável e, em casos críticos, **revisão independente**.

---

## 10. Análise probabilística — quando usar

Use **Monte Carlo/LHS/FORM** quando:

* variáveis chave têm grande variabilidade (ex.: `k`, `μ`, pressão de fluxo, `φ`, `E`);
* a consequência da falha é alta;
* precisa **hierarquizar mitigadores** (índices de Sobol);
* deseja reportar **β** (alvo de confiabilidade) e **intervalos de confiança**.

**Critério de falha**: qualquer verificação crítica reprovada (ELU/ELS/detalhamento/NSF), definida explicitamente no relatório.

**Saídas**: `Pf`, `β`, IC 95% (Clopper–Pearson), Sobol, curva custo×β.

> **Importante**: a análise probabilística **não substitui** a conformidade normativa; ela **complementa** a decisão de projeto.

---

## 11. Versionamento e rastreabilidade

Cada resultado grava:

* **hash das entradas**;
* **versão do pacote** e **versões dos datasets** (normas/custos/solos);
* data e hora; usuário (quando disponível).

O relatório lista as **cláusulas**. Alterações de norma/dataset geram **nova versão** do estudo.

---

## 12. Execução em Colab/Streamlit e testes

* **Colab**: notebooks em `apps/colab/*.ipynb` com exemplos reproduzíveis e botões para exportar `.md`.
* **Streamlit**: `apps/streamlit/` com páginas para cada família de elemento; gráficos **Plotly**; download de relatório.
* **Testes**: `pytest -q` roda a suíte. Inclui **tests de regressão numérica** (tolerância relativa) e snapshots de relatórios.
* **Dados externos**: uploads de **boletim de fundação/sondagens** (`.csv`, `.xlsx`) e perfis SPT; parser converte para `soil.Profile`.

---

## 13. Suporte e dúvidas

* Dúvidas de **modelo**: revisar hipóteses na seção 3 e as **cláusulas** citadas no relatório.
* Dúvidas de **dados**: conferir `data/` (normas, custos, materiais, solos) e **data‑base**.
* Casos fora do escopo ou com dinâmica complexa → **revisão independente** por especialista.

---

## 14. Template de relatório — Subpressão e Empuxo de Água no Subsolo

Esta seção é um **bloco padrão** a ser incluído automaticamente nos relatórios de **sapatas, radiers, caixas enterradas e reservatórios**. O objetivo é demonstrar, de forma auditável, o balanço entre **forças resistentes** (peso próprio, sobrecargas permanentes, lastros e ancoragens) e a **força ascensional de empuxo/subpressão**.

### 14.1 Entradas

* **Geometria da base**: área `A_b`, perímetro molhado `P_b`, cota da base `z_b`.
* **Condições hidráulicas**: nível d’água `NA`, altura de carga **hw = (NA − z\_b)**, gradiente previsto em operação (`i_op`) e em cheia (`i_max`).
* **Propriedades**: `γ_w` (peso específico da água), propriedades do solo para verificação de subpressão/piping quando aplicável.
* **Pesos resistentes**:

  * **Peso próprio** do bloco/estrutura `W_c` (com fatores parciais);
  * **Sobrecargas permanentes** `G_perm`;
  * **Lastro** (concreto magro, enrocamento) `W_l`;
  * **Ancoragens/tirantes** `T_a` (capacidade de tração de projeto, com fator de utilização);
  * **Fator de redução por flutuação** quando houver volumes vazios.
* **Fatores parciais**: `γ_G` (ações permanentes), `γ_Q` (variáveis) e `γ_U` (empuxo/subpressão) conforme combinações adotadas.

### 14.2 Cálculos

1. **Pressão de poros na base**:
   `u = γ_w · hw`
   (quando houver variação ao longo da base, integrar `u(z)` → `U = ∫ u dA`).

2. **Empuxo ascensional resultante**:
   `U_d = γ_U · U = γ_U · (γ_w · hw · A_b)`
   (para base horizontal e `u` uniforme).

3. **Força resistente de projeto**:
   `R_d = γ_G · (W_c + G_perm + W_l) + γ_T · T_a`
   (usar `γ_T` conforme critério do projeto para resistências de tirantes/ancoragens; documentar).

4. **Equilíbrio vertical (ULS – flutuação)**:
   **Condição:** `R_d ≥ U_d`
   **Margem:** `Δ = R_d − U_d`
   **Fator de segurança equivalente:** `FS = R_d / U_d`.

5. **Verificação de subpressão/piping (quando aplicável)**:

   * **Gradiente hidráulico crítico** `i_cr ≈ (γ_sat − γ_w) / γ_w` (solo granular).
   * **Condição:** `i_max ≤ i_adm = α · i_cr` (α ≥ 0,5 típico; adotar valores conservadores conforme **USACE EM 1110‑2‑1901/1913** quando relevante).
   * Em argilas, avaliar estabilidade pelo **alívio de tensões efetivas** e considerar **poços/drenos aliviadores** (**USACE EM 1110‑2‑1914**).

### 14.3 Veredictos

* **ULS – flutuação**: Aprovado/Reprovado, com `FS` e `Δ`.
* **Piping/Subpressão**: Aprovado/Reprovado, com `i_max / i_adm`.
* **Sensibilidade**: impressão de variação de `FS` para ±0,50 m no NA.

### 14.4 Mitigações e alternativas

| Alternativa                        | Descrição                                                | Efeito principal                 | Impacto em custo | Observações                                      |
| ---------------------------------- | -------------------------------------------------------- | -------------------------------- | ---------------- | ------------------------------------------------ |
| **Aumentar lastro**                | Acréscimo de espessura/volume de concreto ou enrocamento | ↑ Peso resistente                | Médio            | Verificar punção e recalques.                    |
| **Ancoragens/tirantes**            | Tirantes ativos/passivos ou chumbadores no radier        | ↑ Resistência à tração           | Médio–Alto       | Requer inspeção e plano de manutenção.           |
| **Aumento de espessura do radier** | Mais peso próprio e rigidez                              | ↑ Peso e ↓ subpressão localizada | Médio            | Checar custos e efeitos em recalque.             |
| **Drenagem/alívio**                | Drenos aliviadores, poços de rebaixamento                | ↓ `hw`/`u`                       | Médio            | Exige operação/monitoramento; risco operacional. |
| **Reconfiguração operacional**     | Limites de nível máximo, sequência de enchimento         | ↓ `hw`                           | Baixo            | Depende de disciplina operacional.               |

> O relatório deve **selecionar e justificar** a alternativa adotada, atualizando o balanço `R_d × U_d`.

### 14.5 Saída tabular padrão

```
Tabela — Balanço de Empuxo/Subpressão (ULS)
A_b [m²] : ...
hw [m]   : ...
γ_w [kN/m³] : ...
U (caract.) [kN] : γ_w · hw · A_b = ...
U_d = γ_U · U [kN] : ...
W_c [kN] : ...  | γ_G · W_c = ...
G_perm [kN] : ... | γ_G · G_perm = ...
W_l [kN] : ... | γ_G · W_l = ...
T_a [kN] : ... | γ_T · T_a = ...
R_d [kN] = γ_G( W_c+G_perm+W_l ) + γ_T T_a = ...
FS = R_d / U_d = ...  → Status: Aprovado/Reprovado
```

### 14.6 API sugerida (resumo)

* `soil.check_uplift(...) -> {U_d, R_d, FS, Δ, status}`
* `reports.blocks.render_uplift(...) -> str`

> **Detalhe completo da assinatura e parâmetros**: ver **Anexo B**.

---

### Anexo A — Roadmap curto

| ID | Entregável                   | Descrição                                                                               | Responsável     | Prazo | Status          |
| -- | ---------------------------- | --------------------------------------------------------------------------------------- | --------------- | ----- | --------------- |
| R1 | **Radier Pasternak v1**      | Implementar fundação elástica Pasternak com calibração `k,Gp` e validação em caso‑teste | Eng. Estruturas | D+21  | Em planejamento |
| R2 | **check\_uplift() + testes** | Função de empuxo/subpressão, piping e bloco `uplift.md` prontos com `pytest`            | Geotecnia       | D+7   | Em execução     |
| R3 | **FORM/SORM básico**         | Cálculo de β por FORM, convergência e sensitividade; wrapper para Monte Carlo           | Risco           | D+30  | Backlog         |
| R4 | **Sismo em tanques (Pi/Pc)** | Implementar ACI 350.3 (Housner), verificação de livre bordo e ancoragens                | Estruturas      | D+28  | Backlog         |
| R5 | **Incêndio NBR 15200**       | Bloco de verificação tabular, TRRF e notas de cálculo                                   | Estruturas      | D+25  | Backlog         |
| R6 | **Exportação DXF**           | Geração de DXF para detalhamento básico (viga, pilar, casca anelar)                     | Dev             | D+40  | Backlog         |
| R7 | **Custos regionalizados**    | Dataset R\$/m³, R\$/kg, R\$/m² com data‑base e atualização mensal                       | Orçamentos      | D+35  | Backlog         |

Tarefas auxiliares:

* **Doc/QA**: snapshots de relatório para cada elemento; tolerâncias de regressão numérica.

* **Performance**: vetorizar loops críticos; cache de combinações; paralelizar Monte Carlo.

* [ ] Radier **Pasternak** com auto‑calibração de parâmetros a partir de retroanálise de recalques.

* [ ] **FORM/SORM** com superfícies de falha e direcionadores de mitigação.

* [ ] **Ciclagem térmica** em tanques e controle de fissuração por estanqueidade.

* [ ] **Exportação DXF** de detalhamento básico.

* [ ] **Pacote de custos regionalizados** com atualização mensal.

---

### Anexo B — API de Subpressão (detalhada)

*Resumo:* a assinatura completa e a tabela de parâmetros estão no **final do documento**. Use a versão curta da API em 14.6 para integração rápida; para detalhes, consulte o **Anexo B**. B — API de Subpressão (detalhada)

```
soil.check_uplift(
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
) -> dict
```

**Retorno**: `{ 'U_d': ..., 'R_d': ..., 'FS': ..., 'delta': ..., 'status': 'approved'|'failed', 'piping': { 'ratio': ..., 'status': ... }, 'table': {...} }`

**Parâmetros essenciais**

| Parâmetro | Significado                             | Observações                                |
| --------- | --------------------------------------- | ------------------------------------------ |
| `A_b`     | Área molhada da base                    | m²                                         |
| `hw`      | Coluna d’água sobre a base (`NA − z_b`) | m                                          |
| `gamma_w` | Peso específico da água                 | default 9,81 kN/m³                         |
| `Wc`      | Peso próprio da estrutura               | kN (característico)                        |
| `Gperm`   | Sobrecargas permanentes                 | kN (característico)                        |
| `Wl`      | Peso de lastro                          | kN (característico)                        |
| `Ta`      | Tração de ancoragens                    | kN (resistência de projeto, aplicar `γ_T`) |
| `gamma_G` | Fator parcial para permanentes          | ajustar conforme combinação                |
| `gamma_U` | Fator parcial para empuxo/subpressão    | ajustar conforme combinação                |
| `gamma_T` | Fator para resistências de tirantes     | definir política do projeto                |
| `i_max`   | Gradiente em cheia/operacional          | para piping                                |
| `i_cr`    | Gradiente crítico                       | granular: `(γ_sat − γ_w)/γ_w`              |

**Renderização**

```
reports.blocks.render_uplift(result: dict, params: dict) -> str  # markdown
```
