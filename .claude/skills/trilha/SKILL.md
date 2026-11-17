---
name: trilha
description: Ponto de entrada da Trilha de Valor, framework de gestão e mensuração de valor em projetos digitais. Use quando a pessoa mencionar a Trilha de Valor, quiser começar ou retomar um projeto, perguntar em que etapa um projeto está ou o que falta, ou não deixar claro qual etapa quer conduzir. Identifica a situação do projeto e encaminha para a skill da etapa.
---

# Trilha de Valor: por onde começar

Você identifica onde o projeto está e leva a pessoa à etapa certa. As regras do `CLAUDE.md` do repositório valem em todas as etapas.

## 1. Descubra o projeto

- Pergunte qual é o projeto. Se a pessoa não souber a pasta, liste `projetos/`.
- Se for um projeto novo, pergunte se os dados são fictícios ou reais **antes de qualquer outra coisa**. Dados reais não entram neste repositório: o projeto precisa ficar em uma pasta fora dele (`iniciar ... --real`), e a pessoa deve respeitar a política de uso de IA da organização dela.
- Para criar: `python3 -m tools.trilha iniciar projetos/<id> --id <id> --nome "<nome>" --modelo "<modelo>"`.

## 2. Leia a situação

Rode `python3 -m tools.trilha status PASTA` e conte à pessoa, em poucas linhas:
- a etapa atual e o que já foi aprovado;
- os passos liberados agora;
- as pendências apontadas pelo verificador, em linguagem simples;
- as premissas em aberto, com destaque para as bloqueantes;
- qualquer linha de "ATENÇÃO" (por exemplo, um plano com a data vencida).

## 3. Encaminhe

| Etapa atual | Skill | Entregável |
|---|---|---|
| `definicao` | `trilha-definicao` | Proposta de Valor do Projeto |
| `monitoramento` | `trilha-monitoramento` | Relatório de Monitoramento de Valor |
| `mensuracao` | `trilha-mensuracao` | Relatório de Benefícios |
| `sustentacao` | `trilha-sustentacao` | Registro de Lições Aprendidas |
| `encerrado` | nenhuma | O ciclo terminou; ofereça a auditoria e a leitura dos documentos |

Os passos da Sustentação são transversais e podem estar liberados em outra etapa. Avise quando for o caso:
- **papéis (S1):** liberado desde a Proposta aprovada. Sugira sempre que a pessoa mencionar troca de responsável;
- **transição (S2):** liberada depois do Relatório de Monitoramento. Se o projeto já está em `mensuracao` e a transição não foi aceita (GT pendente no `status`), diga isso logo: ela deveria acontecer antes de a equipe do projeto sair.

Se o pedido da pessoa não combinar com a etapa (por exemplo, medir resultados de um projeto ainda em definição), explique o que falta e não pule etapas. Se ela quiser só entender o framework, explique as quatro etapas e o que cada uma entrega, sem criar projeto.

## 4. Ao fim de qualquer etapa

- Informe o documento gerado e o hash.
- Diga qual é a próxima etapa e o que a pessoa precisa trazer para ela.
- Ofereça o painel de acompanhamento (`python3 -m tools.painel PASTA`), que reúne indicadores, documentos e pendências numa página.
- Ofereça `python3 -m tools.auditar PASTA`, e explique que o aviso de "âncora externa" é esperado enquanto o último hash não for guardado fora do projeto.

## O que não fazer

- Não conduza uma etapa a partir desta skill: use a skill da etapa.
- Não resuma o estado com números que o `status` e o `mostrar` não devolveram.
- Não crie projeto antes de saber se os dados são fictícios.
