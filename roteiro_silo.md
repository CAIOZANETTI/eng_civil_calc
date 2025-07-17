# Roteiro Completo – Silo Ø 30 m × 48 m (Concreto Protendido)

> **Versão:** 2025‑07‑17  
> **Responsável:** Eng. Caio (Coordenador de Orçamentos)  
> **Revisor Técnico:** Eng. Estruturas Sênior  
> **Objetivo:** Documentar, passo a passo, o processo de dimensionamento, verificação normativa, interação solo‑estrutura, otimização econômica e controle de qualidade de um silo cilíndrico para armazenamento de soja.

---

## Sumário
1. [Premissas e Dados de Entrada](#1-premissas-e-dados-de-entrada)  
2. [Fluxo de Cálculo Top‑Down](#2-fluxo-de-cálculo-top-down)  
3. [Interação Solo‑Estrutura](#3-interação-solo‑estrutura)  
4. [Avaliação Técnica / CQP](#4-avaliação-técnica--cqp)  
5. [Iteração de Ajuste e Otimização](#5-iteração-de-ajuste-e-otimização)  
6. [Saídas Consolidadas](#6-saídas-consolidadas)  
7. [Checagens Finais & Monitoramento](#7-checagens-finais--monitoramento)  
8. [Critérios de Aprovação](#8-critérios-de-aprovação)  
9. [Anexos](#9-anexos)

---

## 1. Premissas e Dados de Entrada

| Item | Valor‑base | Observações |
|------|-----------|-------------|
| **Geometria** | Ø 30 m (r = 15 m); H = 48 m | Parede cilíndrica inicial t ≈ 0,30 m (ajustável) |
| **Materiais** | Concreto C40 (fck = 40 MPa, γc = 25 kN m⁻³, Ec = 30 GPa)<br>Aço passivo CA‑50 (fyk = 500 MPa)<br>Aço ativo 7 h/mm (fpk = 1 860 MPa, perda global 25 %) | Classe de agressividade moderada‑severa (grãos) |
| **Ações** | **G1, G2** Peso‑próprio + equipamentos  
**Qgrão** Soja γ = 8 kN m⁻³ – Janssen + Airy (15 m superiores)  
**Qdin** 25–30 % p_base (descarga rápida)  
**Qvento** NBR 6123 + verificação frequência f₁ ≥ 1 Hz  
**ΔT** Gradiente térmico 25 °C  
**A_exp** Explosão de pó (pressão interna 20 kPa) | Sísmico ignorado (zona de baixa sismicidade) |
| **Fundação – dados geotécnicos preliminares** | Solo residual argiloso sobre arenito intemperizado  
SPT > 50, Es ≈ 45 MPa, NA = –2 m | Estacas Φ 0,60 m (n≈180), passo 3 Φ |
| **Normas** | NBR 6118:2023 • NBR 8681:2020 • NBR 6123:1988 • NBR 6122:2022 • ACI 313‑14 / EC 1‑4 | ACI/EC para benchmark |

---

## 2. Fluxo de Cálculo Top‑Down

| Etapa | Descrição | Resultados‑chave |
|-------|-----------|------------------|
| **2.1** | **Pressões laterais** | p_Janssen(z), p_Airy(z), p_max |
| **2.2** | **Combinações ELU & SLS** (NBR 8681) | Envelopes com γG, γQ, Qdin, A_exp |
| **2.3** | **Solver casca axisimétrica** | σθ(z), σz(z), τrz(z) – inclui rigidez domo + anel |
| **2.4** | **Espessura preliminar** | t₀ por Bresler (σ_eq) |
| **2.5** | **Protensão circunferencial** | Força total P, perdas ΔP, σprot final |
| **2.6** | **Armadura passiva horizontal** | As_h(z) ≥ As_min |
| **2.7** | **Armadura / protensão vertical** | Correção de tração Poisson + ΔT |
| **2.8** | **SLS** | wk ≤ 0,3 mm; flecha topo ≤ H/1 000; f₁ ≥ 1 Hz |
| **2.9** | **Laje de fundo** | Punção (V_Ed ≤ V_Rd2), cisalhamento radial, flotação NA |
| **2.10** | **Interação Solo‑Estrutura** | ver Seção 3 |
| **2.11** | **Flambagem local da casca** | λ = H/t, verif. modo pancake |
| **2.12** | **Longo prazo** | Perdas pós‑60 d, retração/fluência, creep do grão |
| **2.13** | **Custo direto** | R$ concreto, aço, estacas |

---

## 3. Interação Solo‑Estrutura

1. **Investigação geotécnica**  
   – Sondagens SPT/CPTu; Es, φ, c, NA.
2. **Modelo de solo**  
   – Molas Winkler, \(k_v = N/Δ\) em solver.
3. **Capacidade de carga & efeito de grupo**  
   – FS_axial ≥ 2,0, FS_lateral ≥ 1,5.
4. **Recalques**  
   – s_imediato + s_consolidação; s_max ≤ 20 mm, Δs/L ≤ 1/500.
5. **Tombamento e tração periférica**  
   – σv ≤ σadm; nenhuma estaca em tração (ELU vento + descarga parcial).
6. **Empuxo ascendente (flotação)**  
   – Caso NA > cota base com silo vazio.
7. **Monitoramento**  
   – Marcos de nivelamento, piezômetros.

---

## 4. Avaliação Técnica / CQP

### 4.1 Mapeamento cláusula → verificador

| Norma | Cláusula | Função de verificação |
|-------|----------|-----------------------|
| NBR 6118 | §17 As_min | `checar_ass_min()` |
| NBR 6118 | §13 Punção | `checar_puncao()` |
| NBR 8681 | Tabela 2 Fatores γ | `checar_fatores_parciais()` |
| NBR 6123 | §8 f₁ | `checar_frequencia()` |
| NBR 6122 | §6.4 FS estacas | `checar_fs_estacas()` |
| … | … | … |

### 4.2 Workflow CQP
1. **Regras** implementadas em `nucleo/verificador/*.py`.  
2. Classe `ChecagemNorma` devolve lista de falhas.  
3. Check‑lists YAML em `/cqp/` (preliminar, execução, final).  
4. GitHub Actions bloqueia _merge_ se `falhas ≠ ∅`.  
5. PDFs dos check‑lists anexados ao release com assinatura digital.

---

## 5. Iteração de Ajuste e Otimização

| Falha detectada | Ajustes candidatos |
|-----------------|-------------------|
| ELU (σθ, punção, flambagem) | ↑ t, ↑ protensão, ↑ As local |
| SLS (wk, flecha, f₁) | ↑ σprot, anéis extra, ↑ t |
| ρ_total > 150 kg m⁻³ | ↓ t + ↑ protensão (trade‑off) |
| Recalque ou FS baixo | ↑ Φ/n estacas, radier‑estacas, melhoramento solo |
| Custos altos | Ajuste combinatório t × P × estacas |

Loop encerra quando **ChecagemNorma = OK** _e_ **custo** dentro da meta (< 5 % do mínimo).

---

## 6. Saídas Consolidadas

| Descrição | Símbolo | Unidade | Critério |
|-----------|---------|---------|----------|
| Espessura final parede | t_final(z) | m | ≥ t_min ELU |
| Volume de concreto | V_c | m³ | — |
| Massa aço passivo | m_passiva | kg / kg m⁻³ | — |
| Massa aço ativo | m_ativa | kg / kg m⁻³ | — |
| Taxa global de aço | ρ_total | kg m⁻³ | 80–150 |
| Reação fundação | N_fund | kN | — |
| Recalque máximo | s_max | mm | ≤ 20 |
| Recalque diferencial | Δs/L | mm m⁻¹ | ≤ 1/500 |
| FS estacas axial / lat. | FS_axial / FS_lat | — | ≥ 2,0 / 1,5 |
| Utilização σθ | σθ/lim | — | ≤ 1,00 |
| Utilização punção | V_Ed/V_Rd2 | — | ≤ 1,00 |
| Custo total | R$ | — | otimizado |

Relatório **PDF “Conformidade Normativa”** inclui tabela completa de utilizações e check‑lists CQP.

---

## 7. Checagens Finais & Monitoramento

1. **Normas atendidas** (CQP = zero falhas).  
2. **Taxa global** dentro de faixa econômica.  
3. **Construtibilidade** – bitolas comerciais, cobrimento ≥ 50 mm, sequência de concretagem validada.  
4. **Longo prazo** – retração, fluência, perdas protensão pós‑60 d, creep do grão (> 90 d estocagem).  
5. **Cenários acidentais** – explosão de pó (20 kPa), flotação base.  
6. **Plano de monitoramento** – strain‑gauges, nivelamento semestral, piezômetros.

---

## 8. Critérios de Aprovação

| Requisito | Condição |
|-----------|----------|
| ChecagemNorma | lista de falhas = ∅ |
| Custo | ≤ 5 % acima do mínimo otimizado |
| CQP check‑lists | Preliminar, Execução, Final — todos assinados (digital) |
| Auditoria externa | Revisor independente aprova PDF de conformidade |

---

## 9. Anexos

1. **Planilha de pressões Janssen + Airy** (CSV).  
2. **Modelo geotécnico (CPTu)** (PDF).  
3. **Check‑lists YAML** (zip).  
4. **Relatório de Conformidade** (PDF).  
5. **Budget.xlsx** – Custo detalhado (concreto, aço, estacas).

---

> Documento gerado automaticamente via pipeline `calc_estrutural` • Compromisso com rastreabilidade, segurança e economia.

