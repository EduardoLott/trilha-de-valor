---
name: trilha-definicao
description: Conduz a etapa Definição de Valor da Trilha de Valor (pré-projeto) e produz a Proposta de Valor do Projeto. Use quando a pessoa quiser definir o valor de um projeto, escolher benefícios e indicadores, fixar linha de base e metas, nomear responsáveis ou iniciar um projeto na Trilha de Valor.
---

# Definição de Valor (pré-projeto)

Objetivo: sair com a **Proposta de Valor do Projeto** aprovada. As regras do `CLAUDE.md` do repositório valem aqui sem exceção.

## O que você recebe e o que entrega

- **Recebe:** a descrição do projeto e as respostas da pessoa.
- **Entrega:** os nós D1 a D5 registrados, a verificação V1 aprovada e, com a aprovação da pessoa, o portão G1.

## Antes de começar

1. Pergunte se os dados são fictícios ou reais. Se forem reais, aplique a regra de dados sigilosos do `CLAUDE.md`.
2. Se o projeto não existir, crie-o: `python3 -m tools.trilha iniciar projetos/<id> --id <id> --nome "<nome>" --modelo "<modelo>"`.
3. Rode `status` e retome do primeiro nó liberado.

## Como conduzir

Um passo por vez. Em cada passo: faça as perguntas, **mostre à pessoa o que vai registrar**, espere um "sim" claro, grave a proposta em `rascunhos/<NO>.json` e rode `aplicar`. Faça poucas perguntas por vez. Você propõe redação, estrutura e classificações (tipo e sentido do indicador, método de comprovação); a pessoa confirma. Números, datas, nomes e fontes vêm da pessoa.

### D1. Compreender o problema e alinhá-lo à estratégia

Pergunta orientadora: qual problema ou oportunidade justifica o projeto e como ele se relaciona aos objetivos da organização?

Pergunte: que processo é afetado e como funciona hoje; quem é impactado; o que acontece se nada for feito; a que objetivo da organização isso responde. Se a pessoa descrever uma solução ("precisamos automatizar o fechamento"), ajude a chegar ao problema ("o fechamento leva muitos dias e tem retrabalho"). Em `projeto`, `problema` é o problema e `descricao` é a solução proposta.

```json
{"projeto": {"problema": "...", "descricao": "..."},
 "objetivos": [{"id": "OBJ-1", "descricao": "..."}]}
```

### D2. Identificar os benefícios esperados

Pergunta orientadora: o que deverá melhorar no negócio depois da implementação?

Separe entrega, **mudança necessária**, resultado e benefício. Para cada benefício, pergunte quem é o responsável (deve ser da área beneficiada e ficar depois do projeto), o que as pessoas precisam fazer diferente, de que ele depende e em que prazo deve aparecer. Prefira poucos benefícios relevantes.

```json
{"beneficios": [{"id": "BEN-1", "descricao": "...", "objetivo": "OBJ-1", "responsavel": "...",
  "mudancas_necessarias": ["..."], "condicoes": ["..."], "prazo": "AAAA-MM-DD"}]}
```

### D3. Definir os indicadores de valor

Pergunta orientadora: como saberemos se os benefícios foram alcançados?

Proponha indicadores proporcionais ao projeto. Todo benefício precisa de ao menos um indicador de **resultado**; sugira também um **antecedente** (por exemplo, adoção) quando fizer sentido. Indicadores de **execução** conduzem o projeto, mas não comprovam valor. Para cada um, confirme com a pessoa a fórmula, a unidade, a fonte, a periodicidade e o responsável. Proponha o tipo e o sentido (`menor_melhor` ou `maior_melhor`) e peça a confirmação dela; confirmados, não são premissa. Ligue os indicadores ao benefício.

```json
{"indicadores": [{"id": "IND-1", "nome": "...", "tipo": "resultado", "formula": "...", "unidade": "...",
   "sentido": "menor_melhor", "fonte": "...", "periodicidade": "mensal", "responsavel": "...", "situacao": "ativo"}],
 "beneficios": [{"id": "BEN-1", "indicadores": ["IND-1"]}]}
```

### D4. Estabelecer linha de base, metas e método de comprovação

Pergunta orientadora: qual é a situação atual, qual resultado pretendemos e como comprovaremos que ele decorre do projeto?

Para cada indicador ativo, de qualquer tipo, peça o valor da linha de base, a data e a fonte, e a meta com o prazo. **Não sugira valores nem datas**, mesmo que a pessoa peça.

Se a pessoa não tiver a linha de base ou a meta, siga a tabela "Quando a pessoa não sabe" do `CLAUDE.md`. O plano tem a mesma forma nos dois casos, e o "como" e a data vêm dela:

```json
{"indicadores": [{"id": "IND-2", "meta": {"valor": null, "plano": {"como": "O responsável pelo benefício define com a área", "data": "AAAA-MM-DD"}}}]}
```

Se ela não souber nem a data, não invente uma: explique que a Proposta não pode ser aprovada com essa lacuna e deixe que ela escolha entre voltar depois com a informação ou retirar o indicador.

Para indicadores de resultado, defina com a pessoa:
- o **método de comprovação**: `antes_depois` (há linha de base e o contexto muda pouco), `grupo_controle` (dá para comparar áreas com e sem o projeto) ou `serie_temporal` (há vários pontos ou sazonalidade). Explique que grupo de controle e histórico só podem ser criados antes da implantação. Se a pessoa não souber escolher, recomende um a partir do que ela descreveu, explique por quê e peça a confirmação;
- o **critério de sucesso**: a evidência que fará o grupo considerar o benefício realizado.

Critério de sucesso e método de comprovação valem só para indicadores de resultado. Confirme as faixas de classificação (padrão: realizado a partir de 100% da meta, parcial a partir de 50%).

```json
{"indicadores": [{"id": "IND-1",
   "linha_de_base": {"valor": "10", "data": "AAAA-MM-DD", "fonte": "...", "origem": "pessoa", "informado_por": "..."},
   "meta": {"valor": "7", "prazo": "AAAA-MM-DD", "origem": "pessoa", "informado_por": "..."},
   "criterio_sucesso": "...", "metodo_comprovacao": "antes_depois"}],
 "classificacao": {"realizado_a_partir_de": "1", "parcial_a_partir_de": "1/2"},
 "premissas": [{"id": "PRE-1", "texto": "...", "bloqueante": false, "situacao": "aberta", "criada_por": "agente"}]}
```

### D5. Definir fontes, responsáveis e condições

Pergunta orientadora: temos condições de acompanhar e alcançar os resultados, e todos concordam com o valor proposto?

Confirme o acesso às fontes de dados e as dependências. Nomeie os quatro papéis e monte a matriz RACI: cada atividade tem exatamente um `A`. Pergunte se as áreas envolvidas têm percepções diferentes do que é valor e registre as divergências como premissa ou anotação.

```json
{"papeis": {"projeto": "...", "indicador": "...", "beneficio": "...", "governanca": "..."},
 "raci": [{"atividade": "...", "projeto": "I", "indicador": "R", "beneficio": "A", "governanca": "I"}],
 "anotacoes": [{"redacao": "assistente", "confirmado_por": "...", "id": "NOTA-1", "no": "D5", "texto": "Acesso às fontes: ... Dependências: ..."}]}
```

Este passo fica liberado logo depois do D2 e pode ser feito antes, durante ou depois de D3 e D4.

### V1. Verificação

Rode `python3 -m tools.trilha verificar PASTA --no V1`. Se reprovar, mostre cada falha à pessoa em linguagem simples, corrija com ela no passo correspondente e rode de novo. Alterar um passo depois da verificação a invalida: é esperado.

### G1. Aprovação da Proposta de Valor

1. Rode `previa PASTA --tipo proposta_de_valor` e mostre o documento inteiro. Se vier marcado "RASCUNHO", a V1 ainda não passou: volte a ela.
2. Destaque as premissas em aberto e as limitações.
3. Pergunte de forma direta se a pessoa aprova e em nome de quem (em regra, o patrocinador ou o responsável pelo benefício). "Parece bom" ou "ok" não bastam.
4. Só com a resposta explícita, rode `aprovar PASTA --portao G1 --por "<quem declarou>" --em-nome-de "<cargo que ela representa>"`.
5. Informe o arquivo gerado e o hash, e que qualquer mudança futura em indicador, linha de base ou meta exigirá decisão registrada.

## Critérios de qualidade

| Bom | Ruim |
|---|---|
| Problema: "o fechamento leva 10 dias úteis e atrasa os relatórios" | Problema: "falta um sistema de automação" |
| Indicador de resultado: "dias úteis entre o fim do mês e a publicação do fechamento" | "Melhorar a eficiência do fechamento" |
| Meta informada pelo responsável pelo benefício, com prazo | Meta sugerida por você "para começar" |
| Sem histórico: plano de coleta, com a data dada pela pessoa | Linha de base estimada, ou data do plano escolhida por você |
| "Não posso escolher a meta; quem define e até quando?" | Aceitar o "coloca o que achar razoável" |
| Benefício com mudança necessária explícita | Benefício que decorre só da entrega |

## O que não fazer

- Não preencha vários passos de uma vez a partir de uma descrição curta do projeto.
- Não proponha mais indicadores do que a pessoa consegue medir.
- Não trate indicador de execução como prova de valor.
- Não converta benefício intangível em dinheiro: use um indicador qualitativo ou substituto e declare a limitação.
- Não rode `aprovar` sem a confirmação explícita nesta conversa.
