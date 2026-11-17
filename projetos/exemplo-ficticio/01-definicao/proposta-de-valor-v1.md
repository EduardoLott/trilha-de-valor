# Proposta de Valor do Projeto

**Projeto:** Automação do fechamento financeiro

*Exemplo fictício: todos os dados são inventados.*

## Problema e alinhamento estratégico

O fechamento mensal leva 10 dias úteis e atrasa os relatórios gerenciais.

**Solução proposta:** Automatizar conciliações e lançamentos recorrentes do fechamento mensal.

- Objetivo OBJ-1: Dar à gestão informação financeira mais cedo para decidir.

## Benefícios esperados

### BEN-1. Fechamento mensal mais rápido.

- Objetivo: OBJ-1
- Responsável pelo benefício: Gerente de Controladoria
- Mudanças necessárias: Analistas passam a usar a conciliação automática em vez da planilha; Áreas enviam os dados até o segundo dia útil
- Condições e dependências: Integração com o sistema de gestão em produção
- Prazo esperado: 2026-09-30
- Indicadores: IND-1; IND-2

## Indicadores

| Id | Indicador | Tipo | Fórmula | Unidade | Fonte | Periodicidade | Responsável |
|---|---|---|---|---|---|---|---|
| IND-1 | Tempo de fechamento mensal | resultado | Dias úteis entre o fim do mês e a publicação do fechamento | dias úteis | Calendário de fechamento da Controladoria | mensal | Coordenador de Contabilidade |
| IND-2 | Conciliações feitas pela automação | antecedente | Conciliações automáticas dividido pelo total de conciliações do mês | percentual | Registro do sistema de conciliação | mensal | Coordenador de Contabilidade |

## Linha de base, metas e comprovação

| Id | Linha de base | Meta | Critério de sucesso | Método de comprovação |
|---|---|---|---|---|
| IND-1 | 10 dias úteis em 2026-01-31 (fonte: Média dos 6 fechamentos anteriores; informado por Coordenador de Contabilidade) | 7 dias úteis até 2026-09-30 (informado por Gerente de Controladoria) | Meta atingida e mantida por três fechamentos seguidos. | antes e depois |
| IND-2 | 0 percentual em 2026-01-31 (fonte: Processo manual; informado por Coordenador de Contabilidade) | 80 percentual até 2026-08-31 (informado por Gerente de Controladoria) | não se aplica | não se aplica |

Classificação: realizado a partir de 100% da meta; parcial a partir de 50%.

## Papéis

| Papel | Quem |
|---|---|
| Responsável pelo projeto | Gerente do Projeto |
| Responsável pelo indicador | Coordenador de Contabilidade |
| Responsável pelo benefício | Gerente de Controladoria |
| Responsável pela governança | Escritório de Projetos |

## Matriz RACI

| Atividade | Proj. | Ind. | Ben. | Gov. |
|---|---|---|---|---|
| Medir o tempo de fechamento | I | R | A | I |
| Aprovar mudança de meta | C | C | R | A |

## Premissas

- PRE-1 (em aberto, presumida pelo assistente): O volume de lançamentos se mantém estável no período.

---

*Como ler este documento: os números vêm de quem está indicado como origem e da calculadora. A estrutura e a redação de problema, objetivos, benefícios e indicadores foram propostas pelo assistente e confirmadas pela pessoa antes de cada registro. Nos demais textos, o que o assistente redigiu está identificado; o que não está identificado são palavras da pessoa.*
