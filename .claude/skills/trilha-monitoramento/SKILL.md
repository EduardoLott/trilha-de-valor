---
name: trilha-monitoramento
description: Conduz a etapa Monitoramento de Valor da Trilha de Valor (durante o projeto) e produz o Relatório de Monitoramento de Valor. Use quando a pessoa quiser acompanhar indicadores durante a execução, registrar leituras, avaliar a adoção, tratar riscos ao valor, avaliar uma mudança de escopo ou preparar o projeto para a mensuração.
---

# Monitoramento de Valor (durante o projeto)

Objetivo: manter o projeto apontado para os benefícios e sair com o **Relatório de Monitoramento de Valor** aprovado. As regras do `CLAUDE.md` do repositório valem aqui sem exceção.

Esta etapa é **recorrente**: os passos M2, M3 e M4 se repetem a cada ciclo de acompanhamento, por semanas ou meses. Uma sessão normal registra um ciclo e termina; só a última consolida e pede a aprovação.

## O que você recebe e o que entrega

- **Recebe:** um projeto com a Proposta de Valor aprovada, e as leituras, os fatos e as decisões que a pessoa trouxer.
- **Entrega:** a cada ciclo, leituras, riscos e decisões registrados. No fim, M5, a verificação V2 e, com a aprovação da pessoa, o portão G2.

## Antes de começar

Rode `status`. Se a etapa não for `monitoramento`, diga onde o projeto está. Leia os indicadores com `mostrar PASTA --bloco indicadores`: é contra a linha de base e a meta deles que se acompanha. Pergunte à pessoa o que ela quer fazer hoje: registrar um ciclo, avaliar uma mudança ou fechar a etapa.

## Como conduzir

Mostre o que vai registrar, espere um "sim" claro, grave a proposta em `rascunhos/` e rode `aplicar`. Ao reenviar um passo, use outro nome de arquivo (`M2-2.json`).

### M1. Estruturar a rotina e a cadência (uma vez)

Pergunta orientadora: como e com que frequência acompanharemos o valor?

Pergunte como o projeto já se reúne e encaixe o acompanhamento do valor nessa governança, sem criar reuniões paralelas. Três níveis, a adaptar: operacional (semanal ou quinzenal), revisão de valor (mensal) e executiva (por marco ou trimestral). Confirme quem atualiza cada indicador.

```json
{"monitoramento": {"cadencia": {"operacional": "semanal", "revisao_valor": "mensal", "executiva": "trimestral"}}}
```

### M2. Acompanhar a evolução dos indicadores (a cada ciclo)

Pergunta orientadora: os indicadores estão evoluindo na direção dos resultados esperados?

Para cada indicador que já pode ser lido, peça o valor, a data e quem informa. Compare com a linha de base e a meta **sem calcular percentuais**: diga apenas se o valor está entre os dois, além da meta ou aquém da linha de base, e pergunte a explicação dos desvios (campo `comentario`). O comando `calcular` é da Mensuração e não se usa aqui; se a pessoa pedir o percentual, diga que a realização é calculada na Mensuração. Indicador de resultado que só pode ser medido depois da implantação não tem leitura agora: acompanhe os antecedentes.

Cada leitura tem `id` próprio (`LEI-1`, `LEI-2`), para se acumular com as anteriores. Confira o próximo número com `mostrar PASTA --bloco monitoramento`.

```json
{"monitoramento": {"leituras": [{"id": "LEI-1", "indicador": "IND-2", "data": "AAAA-MM-DD", "valor": "55",
   "origem": "pessoa", "informado_por": "...", "comentario": "..."}]}}
```

Se a pessoa não tiver o dado, não registre leitura e não estime.

### M3. Monitorar a adoção e as condições (a cada ciclo)

Pergunta orientadora: a solução está sendo incorporada à operação e existem condições para gerar os benefícios?

Releia as **mudanças necessárias** de cada benefício (`mostrar PASTA --bloco beneficios`) e pergunte, uma a uma, se estão acontecendo. Pergunte também por capacitação, integrações e acessos, e pelas dificuldades relatadas pelos usuários. Entregar não é adotar.

```json
{"anotacoes": [{"redacao": "assistente", "confirmado_por": "...", "id": "NOTA-n", "no": "M3", "texto": "Adoção em AAAA-MM: ..."}]}
```

### M4. Tratar desvios, riscos e mudanças de escopo (quando houver)

Pergunta orientadora: o que pode comprometer ou ampliar o valor, e as mudanças propostas preservam o valor esperado?

**Riscos e oportunidades.** Separe risco do projeto (prazo, custo) de risco ao valor: um projeto no prazo pode não gerar o benefício. Registre com ação, responsável e prazo.

**Gatilho de revisão.** Diante de qualquer mudança de escopo, prioridade ou orçamento, faça as três perguntas à pessoa e registre as respostas na decisão:
1. A mudança altera algum benefício, indicador, linha de base, meta ou prazo?
2. Cria dependências ou riscos novos?
3. Continua alinhada ao objetivo estratégico?

Toda mudança vira uma **decisão** do tipo `mudanca_escopo`, com as três respostas no campo `gatilho` (a verificação cobra). Quando a resposta à primeira pergunta é "não", `afeta` fica vazio. Se a resposta da pessoa não combinar com o que está no estado (por exemplo, a parte adiada parece alimentar um indicador), aponte e pergunte de novo antes de registrar. Se a resposta for "sim", a mesma proposta traz a decisão e a alteração no indicador; a verificação reprova alteração sem decisão. Quem decide é a pessoa.

```json
{"riscos": [{"redacao": "pessoa", "id": "RIS-1", "tipo": "risco", "descricao": "...", "impacto_no_valor": "...", "acao": "...",
   "responsavel": "...", "prazo": "AAAA-MM-DD"}],
 "decisoes": [{"redacao": "pessoa", "id": "DEC-1", "data": "AAAA-MM-DD", "tipo": "mudanca_escopo", "descricao": "...",
   "gatilho": {"altera_valor": true, "novas_dependencias": false, "alinhada": true},
   "afeta": ["IND-1"], "antes": "7", "depois": "8", "justificativa": "...", "decidido_por": "..."}],
 "indicadores": [{"id": "IND-1", "meta": {"valor": "8", "prazo": "AAAA-MM-DD", "origem": "pessoa", "informado_por": "..."}}]}
```

Tipos de decisão: `mudanca_escopo`, `revisao_indicador`, `revisao_meta`, `revisao_linha_de_base`, `encaminhamento`, `outra`. Só `mudanca_escopo` leva `gatilho`.

Se a pessoa pedir uma alteração sem registrar decisão e depois desistir, nada muda no estado; registre o fato com `ocorrencia`.

### M5. Consolidar e preparar a transição (perto do fim do projeto)

Pergunta orientadora: temos informações e condições para medir os benefícios depois da implementação?

Antes de fechar, confirme que a implantação terminou de fato e avise se houver um único ciclo de leituras registrado. Confirme com a pessoa, para cada indicador de resultado: a linha de base e a meta estão com valor (um plano não basta daqui em diante); as **datas de medição** depois da implantação, escolhidas de modo que o benefício já possa ter aparecido; a fonte de dados continuará acessível; quem mede. As datas vêm da pessoa. Confira se elas combinam com o critério de sucesso (um critério de "três períodos seguidos" pede datas suficientes) e se não estão no passado; se não combinarem, pergunte. Quem mede e o acesso à fonte vão em anotação.

```json
{"indicadores": [{"id": "IND-1", "datas_medicao": ["AAAA-MM-DD", "AAAA-MM-DD"]}],
 "anotacoes": [{"redacao": "assistente", "confirmado_por": "...", "id": "NOTA-n", "no": "M5", "texto": "Quem mede: ... Fonte acessível: ..."}]}
```

### V2. Verificação

Rode `verificar PASTA --no V2`. Ela cobra as datas de medição, linha de base e meta com valor nos indicadores de resultado, e decisão para toda mudança. Mostre as falhas em linguagem simples e corrija com a pessoa.

### G2. Aprovação do Relatório de Monitoramento

1. Rode `previa PASTA --tipo relatorio_monitoramento` e mostre o documento inteiro. Se vier marcado "RASCUNHO", volte à V2.
2. Diga com clareza: concluir esta etapa não significa que os benefícios foram realizados; significa que há informação para encerrar a execução e transferir o acompanhamento.
3. Pergunte de forma direta se a pessoa aprova e em nome de quem. "Ok" não basta.
4. Só então rode `aprovar PASTA --portao G2 --por "<quem declarou>" --em-nome-de "<cargo que ela representa>"`.
5. Lembre que a **transição para a operação** deve ser formalizada agora, antes de a equipe do projeto sair (skill `trilha-sustentacao`, passo S2). Se a pessoa adiar, registre com `ocorrencia` a data combinada.

## Critérios de qualidade

| Bom | Ruim |
|---|---|
| "A adoção está em 55; a linha de base é 0 e a meta, 80" | "A adoção está em 69% da meta" (conta feita por você) |
| Mudança de escopo com as três perguntas respondidas e decisão registrada | Meta alterada "para refletir a realidade", sem decisão |
| Risco ao valor: "as áreas não enviam os dados no prazo" | Só riscos de prazo e custo |
| "As planilhas paralelas continuam em uso em duas áreas" | "Sistema entregue" como evidência de adoção |

## O que não fazer

- Não calcule percentuais de avanço nem projete tendências com números seus.
- Não altere indicador, linha de base ou meta sem a decisão da pessoa registrada na mesma proposta.
- Não trate indicador de execução como sinal de valor.
- Não feche a etapa só porque o projeto terminou: sem datas de medição e responsáveis, a V2 reprova.
- Não rode `aprovar` sem a confirmação explícita nesta conversa.
