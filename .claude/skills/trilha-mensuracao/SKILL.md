---
name: trilha-mensuracao
description: Conduz a etapa Mensuração dos Benefícios da Trilha de Valor (pós-projeto) e produz o Relatório de Benefícios. Use quando a pessoa quiser medir resultados depois da implantação, comparar linha de base, meta e resultado, calcular a realização da meta, verificar a atribuição ou comprovar o valor de um projeto já definido na Trilha de Valor.
---

# Mensuração dos Benefícios (pós-projeto)

Objetivo: sair com o **Relatório de Benefícios** aprovado. As regras do `CLAUDE.md` do repositório valem aqui sem exceção. Nesta etapa, duas delas pesam mais: **você não faz contas** e **você não estima medições**.

Esta etapa fica **aberta até a última medição prevista**. Cada data de medição é um ciclo: registrar a medição, calcular, rever a atribuição e as decisões. O Relatório de Benefícios é aprovado uma única vez, depois da última data; antes disso, a verificação V3 reprova. Para comunicar um resultado parcial entre os ciclos, mostre a prévia, que sai marcada como rascunho.

## O que você recebe e o que entrega

- **Recebe:** um projeto com a Proposta de Valor e o Relatório de Monitoramento aprovados, e as medições informadas pela pessoa.
- **Entrega:** os nós B1 a B5 registrados, o cálculo B4 feito pela calculadora, a verificação V3 aprovada e, com a aprovação da pessoa, o portão G3.

## Antes de começar

Rode `python3 -m tools.trilha status PASTA`. Se a etapa atual não for `mensuracao`, diga à pessoa em que etapa o projeto está e o que falta para chegar aqui; não tente pular etapas. Releia no estado os indicadores, a linha de base, a meta, o critério de sucesso e o método de comprovação definidos na Definição: é contra eles que se mede.

## Como conduzir

Um passo por vez. Mostre o que vai registrar, espere um "sim" claro, grave a proposta em `rascunhos/<NO>.json` e rode `aplicar`.

### B1. Confirmar as condições para a mensuração

Pergunta orientadora: temos o que é necessário para medir o valor depois que a equipe de projeto sair?

Confira com a pessoa, para **cada indicador ativo**, de resultado e antecedente: os responsáveis pelo indicador e pelo benefício continuam os mesmos; a fonte de dados segue acessível; as datas de medição estão mantidas. Se o `status` mostrar que a transição para a operação ainda não foi aceita, avise; se a pessoa adiar, registre com `ocorrencia`. Pendências são aceitáveis se tiverem responsável e prazo.

```json
{"anotacoes": [{"redacao": "assistente", "confirmado_por": "...", "id": "NOTA-n", "no": "B1", "texto": "Condições confirmadas: ... Pendências: ..."}]}
```

Se um responsável mudou, atualize `papeis` ou o `responsavel` do indicador na mesma proposta.

### B2. Planejar e executar as medições

Pergunta orientadora: o que será medido, por quem, quando e como?

Pergunte pela medição de **cada indicador ativo**, de resultado e antecedente: sem os antecedentes (como a adoção), não dá para interpretar o resultado. Peça o valor, a data, a fonte e quem informa. Confirme que a fórmula, a unidade e a fonte de dados são as mesmas do indicador na Definição. Se algo mudou, pare: isso exige recalcular a linha de base e registrar uma decisão.

Se o dado não existir, **não estime**, mesmo que a pessoa peça. Não registre a medição; registre o indicador em `nao_medidos`, com o motivo e, se a pessoa souber, como e quando o dado será obtido. Ele sairá no relatório como "não medido". **Cada data de medição prevista** de um indicador de resultado precisa de uma medição ou desse registro, com a mesma data: é o que o guia chama de medições "realizadas ou justificadas". Não é possível fechar o relatório antes da última data prevista: se a pessoa quiser antecipar, a saída é uma decisão registrada que mude as datas de medição do indicador.

A cada data prevista, registre a medição (B2), refaça o cálculo (B4) e atualize a atribuição e as decisões. Se ainda faltam datas, encerre a sessão dizendo quando é a próxima. Recuse o pedido de estimar e registre-o com `ocorrencia`.

```json
{"medicoes": [{"id": "MED-1", "indicador": "IND-1", "data": "AAAA-MM-DD", "valor": "8",
   "fonte": "...", "origem": "pessoa", "informado_por": "..."}],
 "nao_medidos": [{"redacao": "pessoa", "id": "NM-1", "indicador": "IND-2", "data": "AAAA-MM-DD", "motivo": "...", "plano": "...", "prazo": "AAAA-MM-DD"}]}
```

### B3. Verificar a atribuição do resultado

Pergunta orientadora: a melhoria observada pode ser atribuída ao projeto?

Percorra com a pessoa os fatores concorrentes: mudança de processo, equipe ou política; sazonalidade ou variação de volume; outro projeto atuando sobre o mesmo indicador; mudança na forma de medir; mudança de escopo que altere o que o indicador representa. Para a mudança de escopo, consulte também `decisoes` no estado (`mostrar PASTA --bloco decisoes`); se houver decisão de escopo e a pessoa não souber avaliar o efeito, proponha registrar isso como limitação, com o texto mostrado a ela. Aplique o método de comprovação definido na Definição.

Compare os fatores encontrados com as premissas em aberto (`mostrar PASTA --bloco premissas`). Se um fato relatado contraria uma premissa, mostre isso à pessoa e, com a concordância dela, mude a premissa para `"situacao": "contrariada"`; se a confirma, para `"confirmada"`.

Registre a conclusão (`atribuivel`, `parcial` ou `nao_atribuivel`) e as limitações, mesmo que a pessoa não encontre nenhum fator.

```json
{"atribuicao": [{"redacao": "pessoa", "indicador": "IND-1", "fatores_concorrentes": ["..."], "conclusao": "parcial", "limitacoes": "..."}],
 "premissas": [{"id": "PRE-1", "situacao": "contrariada"}]}
```

As limitações aparecem no relatório aprovado: escreva o que a pessoa disse ou confirmou.

Este passo pode ser feito antes ou depois do cálculo.

### B4. Calcular a realização e classificar

Pergunta orientadora: quanto do que foi planejado foi alcançado?

Rode `python3 -m tools.trilha calcular PASTA`. Apresente à pessoa exatamente o que o comando devolveu: linha de base, meta, resultado, realização (fração e percentual), classificação e as faixas usadas. Não refaça nem arredonde a conta por conta própria.

Se a pessoa pedir outra classificação ("ficou perto, coloca como realizado"), explique que a classificação segue as faixas combinadas na Definição e não mude nada. Mudar as faixas ou a meta é uma decisão registrada, que fica visível no relatório. Registre o pedido recusado com `ocorrencia`. A fórmula é realização = (resultado − linha de base) ÷ (meta − linha de base), e vale também quando menor é melhor.

Ajude a interpretar em conjunto: um resultado só se sustenta se os indicadores antecedentes (como a adoção) também tiverem evoluído. Pergunte por efeitos não previstos, positivos e negativos, e registre-os como anotação no passo seguinte.

Se uma medição for corrigida depois, o cálculo é invalidado e precisa ser refeito: é esperado.

### B5. Decidir e comunicar

Pergunta orientadora: o que fazemos com o que aprendemos?

Para cada indicador com resultado, o responsável pelo benefício decide entre `manter` (o acompanhamento), `corrigir` (benefício parcial), `revisar` (a meta ou o indicador; a premissa estava errada) ou `encerrar` (benefício realizado e estável), com ação, responsável e prazo. A decisão é da pessoa: apresente as opções, não escolha por ela. Para indicador não medido, pergunte quem obtém o dado e até quando, e registre no `prazo` do `nao_medidos`.

```json
{"encaminhamentos": [{"redacao": "pessoa", "id": "ENC-1", "indicador": "IND-1", "decisao": "corrigir", "acao": "...",
   "responsavel": "...", "prazo": "AAAA-MM-DD"}],
 "anotacoes": [{"redacao": "assistente", "confirmado_por": "...", "id": "NOTA-n", "no": "B5", "texto": "Efeitos não previstos: ..."}]}
```

### V3. Verificação

Rode `python3 -m tools.trilha verificar PASTA --no V3` só depois da última medição prevista. Ela refaz as contas, confere se os indicadores medidos são os da Proposta de Valor, se toda mudança tem decisão registrada, se todo resultado tem atribuição e decisão. Se reprovar, mostre cada falha em linguagem simples e corrija com a pessoa.

### G3. Aprovação do Relatório de Benefícios

1. Rode `previa PASTA --tipo relatorio_beneficios` e mostre o documento inteiro. Se vier marcado "RASCUNHO", a V3 ainda não passou: volte a ela.
2. Destaque as limitações de atribuição, as premissas em aberto e o que ficou "não medido".
3. Pergunte de forma direta se a pessoa aprova e em nome de quem (em regra, o responsável pelo benefício). "Ok" ou "parece bom" não bastam.
4. Só com a resposta explícita, rode `aprovar PASTA --portao G3 --por "<quem declarou>" --em-nome-de "<cargo que ela representa>"`.
5. Informe o arquivo e o hash, e sugira rodar `python3 -m tools.auditar PASTA`.
6. Diga que as lições seguem para a etapa de Governança e Melhoria Contínua.

## Critérios de qualidade

| Bom | Ruim |
|---|---|
| "A calculadora devolveu 2/3 (67%), classificação parcial" | "Foram cerca de 70% da meta" |
| Medição com data, fonte e quem informou | "O time acha que ficou em uns 8 dias" registrado como medição |
| "O mês medido teve volume atípico; a atribuição é parcial" | Atribuir todo o resultado ao projeto sem checar outros fatores |
| Indicador sem dado aparece como "não medido", com o motivo | Valor estimado para completar o quadro |
| Decisão com ação, responsável e prazo | "Seguir acompanhando" sem dono |

## O que não fazer

- Não calcule, não arredonde e não corrija o resultado da calculadora.
- Não troque o indicador, a linha de base ou a meta para o resultado parecer melhor. Se a pessoa pedir isso, explique que a mudança exige decisão registrada e fica visível no relatório.
- Não transforme um resultado parcial em "realizado" na redação.
- Não omita as limitações.
- Não rode `aprovar` sem a confirmação explícita nesta conversa.
