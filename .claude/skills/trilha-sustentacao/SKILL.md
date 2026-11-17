---
name: trilha-sustentacao
description: Conduz a etapa Governança e Melhoria Contínua (Sustentação) da Trilha de Valor e produz o Termo de Transição e o Registro de Lições Aprendidas. Use quando a pessoa quiser confirmar ou trocar responsáveis, formalizar a passagem do projeto para a operação, registrar lições aprendidas, atualizar o catálogo de indicadores ou encerrar o ciclo de um projeto na Trilha de Valor.
---

# Governança e Melhoria Contínua (Sustentação)

Objetivo: fazer a gestão do valor sobreviver ao projeto. As regras do `CLAUDE.md` do repositório valem aqui sem exceção.

Esta etapa é **transversal**: seus passos não esperam o fim do ciclo. Cada um fica liberado em um momento diferente.

| Passo | Quando fica liberado | Quando fazer |
|---|---|---|
| S1. Papéis e RACI | Depois da Proposta de Valor aprovada (G1) | Sempre que alguém mudar de função, e no encerramento |
| S2, VT, GT. Transição | Depois do Relatório de Monitoramento aprovado (G2) | **Antes de a equipe do projeto sair** |
| S3. Lições aprendidas | Depois do Relatório de Benefícios aprovado (G3) | Depois da última medição prevista |
| S4. Catálogo | Depois de S3 | Junto com as lições |
| V4, G4. Encerramento | Depois de S1, GT e S4 | Fecha o ciclo |

## Antes de começar

Rode `status`: ele mostra os nós transversais e quais estão liberados. Pergunte o que a pessoa quer fazer e vá direto ao passo. Mostre o que vai registrar, espere um "sim" claro, grave a proposta em `rascunhos/` e rode `aplicar`.

## S1. Manter os papéis e a matriz RACI

Pergunta orientadora: quem responde pelo quê, antes e depois do fim do projeto?

Leia `mostrar PASTA --bloco papeis` e confirme cada um dos quatro papéis com a pessoa. Um papel é uma responsabilidade exercida por alguém nomeado, não um cargo vago. Verifique três pontos e leve à pessoa o que encontrar:
- o responsável pelo benefício é da área beneficiada e continua depois do projeto;
- quem comprova o benefício não é só o responsável pelo projeto;
- se alguém vai mudar de função, o substituto está nomeado antes da saída.

Se nada mudou, registre a confirmação. Se mudou, atualize `papeis` e o `responsavel` dos indicadores e benefícios afetados; revise o `raci` só se a distribuição de responsabilidades mudou. Pergunte desde quando vale a troca e registre na anotação quem exerceu o papel antes. Não altere o `informado_por` de valores já registrados. A data da confirmação é a que a pessoa informar.

```json
{"papeis": {"indicador": "..."},
 "anotacoes": [{"redacao": "assistente", "confirmado_por": "...", "id": "NOTA-n", "no": "S1", "texto": "Papéis confirmados em AAAA-MM-DD. Mudanças: ..."}]}
```

## S2. Formalizar a transição para a operação

Pergunta orientadora: quem assume o acompanhamento quando a equipe sair?

Confira com a pessoa, item a item:
- os responsáveis pelo indicador e pelo benefício estão nomeados e **cientes**;
- fichas, fórmulas e a matriz de indicadores foram entregues na versão vigente;
- o acesso às fontes de dados e o calendário de medição estão mantidos;
- pendências e riscos ao benefício têm dono;
- alguém da equipe do projeto fica disponível até a primeira medição.

Se a transição está sendo registrada depois do fato (o `status` avisa quando ela está atrasada), diga isso à pessoa e, com a concordância dela, registre em anotação de `no` "S2" a data real do registro. Itens que não foram entregues entram em `pendencias`, com dono. "Cientes" também vai em anotação.

`transicao.data` é a data em que a transição aconteceu de fato, não a do registro. Se a pessoa não souber se um item foi entregue, ele entra em `pendencias` como "confirmar", e você pergunta quem confirma.

```json
{"transicao": {"redacao": "pessoa", "data": "AAAA-MM-DD", "recebido_por": "...", "itens": ["..."], "acessos": "...",
   "apoio_ate_primeira_medicao": "...", "pendencias": ["..."]}}
```

Depois:
1. Rode `verificar PASTA --no VT`. Ela cobra a data, quem assume, o que foi entregue e quem fica disponível até a primeira medição.
2. Rode `previa PASTA --tipo termo_transicao` e mostre o documento.
3. O Termo pede **dois aceites**: do responsável pelo benefício e do responsável pela governança. Pergunte de forma direta se a pessoa registra o aceite e por qual dos dois papéis ela pode falar.
4. Primeiro aceite: `aprovar PASTA --portao GT --papel beneficio --por "<quem declarou>" --em-nome-de "<cargo>"` (ou `--papel governanca`, se for o caso). Este aceite não muda a etapa do projeto.
5. Segundo aceite, na mesma sessão ou depois: `aceitar PASTA --papel governanca --por "<quem declarou>" --em-nome-de "<cargo>"`. Enquanto faltar um aceite, o `status` avisa e o ciclo não pode ser encerrado. Não registre o aceite de um papel pelo qual a pessoa disse que não pode falar.

## S3. Registrar as lições aprendidas

Pergunta orientadora: o que funcionou, o que dificultou e o que mudaríamos?

Percorra as etapas (definição, monitoramento, mensuração) e pergunte o que funcionou e o que dificultou em cada uma, e quais indicadores ajudaram a decidir. Pergunte também o que falhou no uso da própria Trilha de Valor (registre com `"etapa": "framework"`).

**Uma lição só entra com ação, responsável e prazo.** Se a pessoa trouxer uma constatação sem ação, pergunte o que deve ser feito, por quem e até quando. Se não houver ação, não registre como lição. Se ela pedir que você escreva as lições, recuse e registre o pedido com `ocorrencia`. Você pode apontar fatos do histórico do projeto (uma premissa contrariada, uma medição que faltou) e perguntar se há lição ali; a lição é dela.

```json
{"licoes": [{"redacao": "pessoa", "id": "LIC-1", "etapa": "mensuracao", "licao": "...", "acao": "...", "responsavel": "...", "prazo": "AAAA-MM-DD"}]}
```

## S4. Atualizar o catálogo de indicadores

Pergunta orientadora: o que deste projeto ajuda o próximo?

Para **cada indicador** do projeto, inclusive os descontinuados, pergunte: foi difícil medir? Ajudou a decidir (`sim`, `em_parte`, `nao`)? Alguma observação para quem for usá-lo de novo? A fórmula, a fonte, a linha de base, a meta e o resultado vêm do estado e entram sozinhos no documento. `dificuldade` aceita `baixa`, `media` ou `alta`.

```json
{"catalogo": [{"redacao": "pessoa", "id": "CAT-1", "indicador": "IND-1", "dificuldade": "baixa", "util_para_decidir": "sim", "observacao": "..."}]}
```

## V4 e G4. Encerramento do ciclo

1. Rode `verificar PASTA --no V4`. Ela cobra os quatro papéis, os dois aceites do Termo de Transição, lições com ação, responsável e prazo, e todos os indicadores no catálogo. Exige também a confirmação dos papéis (S1).
2. Rode `previa PASTA --tipo licoes_aprendidas` e mostre o documento inteiro.
3. Antes de pedir a aprovação, reveja com a pessoa as premissas ainda em aberto (`mostrar PASTA --bloco premissas`): cada uma foi confirmada, contrariada ou continua aberta? Pergunte também pelos riscos e encaminhamentos com prazo vencido e marque `"situacao": "concluido"` nos que ela disser que foram tratados.
3. Pergunte de forma direta se a pessoa aprova e em nome de quem (em regra, o responsável pela governança).
4. Só então rode `aprovar PASTA --portao G4 --por "<quem declarou>" --em-nome-de "<cargo que ela representa>"`. O projeto passa a `encerrado` e não aceita mais alterações. Se houver linhas de "ATENÇÃO" no `status` (medição prevista sem registro, prazo vencido), leve-as à pessoa antes de encerrar.
5. Rode `python3 -m tools.auditar PASTA` e mostre o resultado. Sugira guardar o último hash fora da pasta do projeto.

## Critérios de qualidade

| Bom | Ruim |
|---|---|
| Lição: "a primeira medição caiu em mês atípico; marcar fora de fechamento de trimestre; Escritório de Projetos; até 15/12" | "Comunicação precisa melhorar" |
| Transição registrada na semana em que a equipe sai | Termo preenchido meses depois, de memória |
| Responsável pelo benefício: gerente da área beneficiada | Responsável pelo benefício: gerente do projeto, que será realocado |
| Catálogo com a dificuldade real de medir cada indicador | Todos os indicadores marcados como úteis e fáceis |

## O que não fazer

- Não escreva lições pela pessoa.
- Não registre o aceite da transição sem saber em nome de quem.
- Não deixe a transição para depois da Mensuração: se o Relatório de Monitoramento já foi aprovado e a transição não foi feita, avise.
- Não encerre o ciclo com lição sem ação.
- Não rode `aprovar` sem a confirmação explícita nesta conversa.
