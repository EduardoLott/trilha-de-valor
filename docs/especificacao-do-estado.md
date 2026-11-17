# Assistente da Trilha de Valor: especificação do estado do projeto

Versão 0.1. Define o que o arquivo de estado guarda, quem pode escrever cada parte e quais regras o verificador aplica.

## 1. Para que serve

O estado é a **memória do assistente entre as etapas** e a **fonte única** para a calculadora, o verificador e a auditoria. Os entregáveis do guia (Proposta de Valor, Relatório de Monitoramento, Relatório de Benefícios, Registro de Lições Aprendidas) são gerados a partir dele; ninguém edita um número direto no relatório.

Três princípios:
1. **Todo valor tem origem.** Um número veio de uma pessoa, da calculadora ou é uma premissa. Nunca do agente.
2. **Nada aprovado muda.** Alteração gera nova versão e uma decisão registrada.
3. **O vocabulário é o do guia v3**: quatro papéis; indicadores de execução, antecedentes e de resultado; linha de base; meta; critério de sucesso; método de comprovação.

## 2. Arquivos de um projeto

```
projetos/<id-do-projeto>/
├── projeto.yaml          estado atual (este documento)
├── evidencias.jsonl      registro só de acréscimo, encadeado por hash
├── 01-definicao/         entregáveis gerados, por versão
├── 02-monitoramento/
├── 03-mensuracao/
└── 04-sustentacao/
```

**Formato do estado (decisão em aberto, Q13).** A biblioteca padrão do Python não lê YAML. As opções são:

| Opção | Vantagem | Custo |
|---|---|---|
| `projeto.json` (recomendada) | Lido e gravado só com a biblioteca padrão; serialização canônica para o hash | Menos confortável para ler e editar à mão |
| `projeto.yaml` com PyYAML | Mais legível | Uma dependência externa para todo usuário |
| `projeto.toml` | Leitura na biblioteca padrão (Python 3.11 ou superior) | Sem gravação na biblioteca padrão; listas aninhadas ficam verbosas |

A estrutura abaixo vale para qualquer das três. O exemplo está em YAML por legibilidade. Se a opção for JSON, a leitura humana vem dos entregáveis em markdown, gerados do estado.

## 3. Estrutura

Convenções: identificadores estáveis com prefixo (`OBJ-`, `BEN-`, `IND-`, `DEC-`, `PRE-`, `MED-`, `DOC-`); datas em `AAAA-MM-DD`; valores numéricos gravados como texto (`"10"`, `"7.5"`) para a calculadora usar aritmética exata.

### 3.1 Blocos e quem escreve

| Bloco | Conteúdo | Etapa em que nasce | Quem informa o conteúdo |
|---|---|---|---|
| `projeto` | Identificação, etapa atual, versão do esquema, marca de fictício | Definição | Pessoa |
| `objetivos` | Objetivos estratégicos a que o projeto responde | Definição | Pessoa (agente propõe a redação) |
| `beneficios` | Perfil de cada benefício | Definição | Pessoa (agente propõe) |
| `indicadores` | Ficha, linha de base, meta, critério de sucesso, método de comprovação | Definição | Pessoa (agente propõe a ficha; números só da pessoa) |
| `papeis` e `raci` | Os quatro papéis e a matriz | Definição; revisado na Sustentação | Pessoa |
| `classificacao` | Faixas de realizado, parcial e não realizado | Definição (confirmada no plano pós) | Pessoa (padrão sugerido) |
| `monitoramento` | Cadência e leituras periódicas | Monitoramento | Pessoa |
| `decisoes` | Mudanças de escopo e demais decisões, com justificativa | Qualquer | Pessoa |
| `medicoes` | Medições pós-implementação | Mensuração | Pessoa |
| `resultados` | Realização e classificação | Mensuração | **Calculadora** |
| `atribuicao` | Fatores concorrentes e limitações declaradas | Mensuração | Pessoa (agente propõe a lista de checagem) |
| `transicao` e `licoes` | Termo de Transição e lições aprendidas | Sustentação | Pessoa (agente propõe) |
| `premissas` | Tudo que foi presumido | Qualquer | Agente ou pessoa |
| `documentos` | Versões aprovadas dos entregáveis, com hash | Qualquer | **Orquestrador** |
| `execucao` | Estado dos nós do DAG e nível de garantia | Qualquer | **Orquestrador** |

O agente nunca grava o arquivo direto: ele propõe, a pessoa confirma, e a gravação passa por um script que valida o esquema e registra a evidência.

### 3.2 Campos

**`projeto`**

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `id`, `nome` | texto | sim | |
| `versao_esquema` | texto | sim | Hoje `"0.1"` |
| `ficticio` | booleano | sim | `true` em tudo que for versionado no repositório público |
| `etapa_atual` | `definicao`, `monitoramento`, `mensuracao`, `sustentacao`, `encerrado` | sim | Só avança por portão aprovado (seção 4) |
| `descricao`, `problema` | texto | sim | |

**`objetivos[]`**: `id`, `descricao`.

**`beneficios[]`** (perfil de benefício)

| Campo | Obrigatório | Observação |
|---|---|---|
| `id`, `descricao` | sim | |
| `objetivo` | sim | Referência a um `OBJ-` |
| `responsavel` | sim | Responsável pelo benefício (nome ou cargo) |
| `mudancas_necessarias` | sim | O que precisa mudar entre a entrega e o resultado |
| `condicoes` | não | Dependências e condições |
| `prazo` | sim | Quando se espera o benefício |
| `indicadores` | sim, ao menos um de resultado | Referências a `IND-` |

**`indicadores[]`**

| Campo | Obrigatório | Observação |
|---|---|---|
| `id`, `nome` | sim | |
| `tipo` | sim | `execucao`, `antecedente` ou `resultado` |
| `formula`, `unidade` | sim | Como se calcula a medida |
| `sentido` | sim | `menor_melhor` ou `maior_melhor` |
| `fonte`, `periodicidade` | sim | |
| `responsavel` | sim | Responsável pelo indicador |
| `linha_de_base` | sim, ou `plano` | `valor`, `data`, `fonte`, `origem`; sem histórico, um `plano` de como obtê-la e até quando |
| `meta` | sim | `valor`, `prazo`, `origem` |
| `criterio_sucesso` | sim para tipo `resultado` | Evidência que fará o grupo considerar o benefício realizado |
| `metodo_comprovacao` | sim para tipo `resultado` | `antes_depois`, `grupo_controle` ou `serie_temporal` |
| `datas_medicao` | sim antes do encerramento do projeto | Lista de datas do Plano de Mensuração Pós-implementação |
| `situacao` | sim | `ativo`, `revisado` ou `descontinuado` |

**`origem`** (em todo valor numérico): `pessoa` (com `informado_por`), `calculadora` ou `premissa` (com referência a um `PRE-`).

**`papeis`**: `projeto`, `indicador`, `beneficio`, `governanca`. **`raci[]`**: `atividade` e, para cada papel, `R`, `A`, `C` ou `I`; exatamente um `A` por atividade.

**`classificacao`**: `realizado_a_partir_de` e `parcial_a_partir_de`, como fração da meta. Padrão sugerido (resposta proposta para a Q8): **configurável por projeto**, com `"1"` e `"0.5"`. O guia já diz que a classificação segue "o critério do plano", então a regra fica no projeto, não no código. Abaixo de `parcial_a_partir_de`, não realizado; sem medição, não medido.

**`monitoramento`**: `cadencia` (operacional, tática, estratégica) e `leituras[]` com `indicador`, `data`, `valor`, `origem`.

**`decisoes[]`**

| Campo | Obrigatório | Observação |
|---|---|---|
| `id`, `data`, `descricao` | sim | |
| `tipo` | sim | `mudanca_escopo`, `revisao_indicador`, `revisao_meta`, `revisao_linha_de_base`, `encaminhamento`, `outra` |
| `afeta` | sim se alterar algo | Referências aos itens alterados |
| `antes`, `depois` | sim se alterar valor | |
| `justificativa`, `decidido_por` | sim | |

**`medicoes[]`**: `id`, `indicador`, `data`, `valor`, `fonte`, `origem` (sempre `pessoa`), `informado_por`.

**`resultados[]`**: `indicador`, `medicao`, `realizacao` (fração exata), `classificacao`, `ferramenta` (nome e versão). Só a calculadora grava.

**`atribuicao[]`**: `indicador`, `fatores_concorrentes`, `conclusao` (`atribuivel`, `parcial`, `nao_atribuivel`), `limitacoes`.

**`premissas[]`**: `id`, `texto`, `bloqueante` (booleano), `situacao` (`aberta`, `confirmada`, `descartada`), `criada_por`.

**`documentos[]`**: `id`, `tipo` (`proposta_de_valor`, `relatorio_monitoramento`, `relatorio_beneficios`, `licoes_aprendidas`, `termo_transicao`), `versao`, `arquivo`, `sha256`, `aprovado_por`, `aprovado_em`.

**`execucao.nos[]`**: `id`, `estado` (`pendente`, `pronto`, `executado`, `verificado`, `aprovado`, `falhou`, `invalidado`), `nivel_exigido`, `nivel_alcancado`.

## 4. Etapas e portões

| De | Para | Portão | Condição checada pelo verificador |
|---|---|---|---|
| `definicao` | `monitoramento` | G1 | Proposta de Valor aprovada; regras C1 a C6 |
| `monitoramento` | `mensuracao` | G2 | Relatório de Monitoramento aprovado; C7 e K2; datas de medição definidas |
| `mensuracao` | `sustentacao` | G3 | Relatório de Benefícios aprovado; K1 a K4 |
| `sustentacao` | `encerrado` | G4 | Termo de Transição e lições registrados |

Voltar a uma etapa anterior é permitido, mas gera decisão registrada, nova versão do documento e invalida os nós seguintes. A Sustentação é transversal no guia; no estado, os papéis e as lições podem ser atualizados em qualquer etapa, e o portão G4 só fecha o ciclo.

## 5. Regras do verificador

**Completude**

| # | Regra |
|---|---|
| C1 | Os quatro papéis estão nomeados |
| C2 | Todo benefício tem responsável, prazo, mudança necessária e ao menos um indicador de resultado |
| C3 | Todo indicador ativo tem tipo, fórmula, unidade, sentido, fonte, periodicidade e responsável |
| C4 | Todo indicador ativo tem linha de base (ou plano com data) e meta |
| C5 | Todo indicador de resultado tem critério de sucesso e método de comprovação |
| C6 | Toda atividade do RACI tem exatamente um `A` |
| C7 | Todo indicador de resultado tem datas de medição antes de G2 |

**Consistência entre etapas**

| # | Regra |
|---|---|
| K1 | Toda medição se refere a um indicador que existe desde a Definição ou foi criado por decisão registrada |
| K2 | Toda diferença de linha de base, meta ou indicador em relação ao documento aprovado tem uma decisão que a explica |
| K3 | Indicador com resultado tem método de comprovação e registro de atribuição |
| K4 | Todo resultado gravado é igual ao que a calculadora produz ao ser reexecutada |

**Integridade**

| # | Regra |
|---|---|
| I1 | `meta ≠ linha de base` para todo indicador calculado |
| I2 | A meta está no lado certo da linha de base, conforme o `sentido` |
| I3 | Nenhum valor numérico tem origem diferente de `pessoa`, `calculadora` ou `premissa` |
| I4 | Nenhuma premissa bloqueante está aberta em um portão |
| I5 | O hash de cada documento aprovado coincide com o arquivo |
| I6 | `etapa_atual` é compatível com os portões aprovados |
| I7 | Toda referência (`OBJ-`, `BEN-`, `IND-` etc.) aponta para um item existente |
| I8 | `ficticio: true` em projetos dentro do repositório |

Cada regra devolve aprovado ou reprovado, com o item e o motivo. O verificador não corrige nada.

## 6. Exemplo: caso fictício do fechamento financeiro

Todos os dados são inventados. É o mesmo exemplo do guia: linha de base de 10 dias, meta de 7, resultado de 8. A sintaxe do bloco ainda não foi validada por um analisador (não há PyYAML no ambiente); isso será feito na Fase 1, no formato escolhido na Q13.

```yaml
projeto:
  id: exemplo-ficticio
  nome: Automação do fechamento financeiro
  versao_esquema: "0.1"
  ficticio: true
  etapa_atual: sustentacao
  problema: O fechamento mensal leva 10 dias úteis e atrasa os relatórios gerenciais.
  descricao: Automatizar conciliações e lançamentos recorrentes do fechamento mensal.

objetivos:
  - id: OBJ-1
    descricao: Dar à gestão informação financeira mais cedo para decidir.

beneficios:
  - id: BEN-1
    descricao: Fechamento mensal mais rápido.
    objetivo: OBJ-1
    responsavel: Gerente de Controladoria
    mudancas_necessarias:
      - Analistas passam a usar a conciliação automática em vez da planilha.
      - Áreas enviam os dados até o segundo dia útil.
    condicoes:
      - Integração com o sistema de gestão em produção.
    prazo: 2026-09-30
    indicadores: [IND-1, IND-2]

indicadores:
  - id: IND-1
    nome: Tempo de fechamento mensal
    tipo: resultado
    formula: Dias úteis entre o fim do mês e a publicação do fechamento
    unidade: dias úteis
    sentido: menor_melhor
    fonte: Calendário de fechamento da Controladoria
    periodicidade: mensal
    responsavel: Coordenador de Contabilidade
    linha_de_base: {valor: "10", data: 2026-01-31, fonte: Média dos 6 fechamentos anteriores, origem: pessoa, informado_por: Coordenador de Contabilidade}
    meta: {valor: "7", prazo: 2026-09-30, origem: pessoa, informado_por: Gerente de Controladoria}
    criterio_sucesso: Meta atingida e mantida por três fechamentos seguidos.
    metodo_comprovacao: antes_depois
    datas_medicao: [2026-07-31, 2026-08-31, 2026-09-30]
    situacao: ativo
  - id: IND-2
    nome: Conciliações feitas pela automação
    tipo: antecedente
    formula: Conciliações automáticas dividido pelo total de conciliações do mês
    unidade: percentual
    sentido: maior_melhor
    fonte: Registro do sistema de conciliação
    periodicidade: mensal
    responsavel: Coordenador de Contabilidade
    linha_de_base: {valor: "0", data: 2026-01-31, fonte: Processo manual, origem: pessoa, informado_por: Coordenador de Contabilidade}
    meta: {valor: "80", prazo: 2026-08-31, origem: pessoa, informado_por: Gerente de Controladoria}
    situacao: ativo

papeis:
  projeto: Gerente do Projeto
  indicador: Coordenador de Contabilidade
  beneficio: Gerente de Controladoria
  governanca: Escritório de Projetos

raci:
  - {atividade: Medir o tempo de fechamento, projeto: I, indicador: R, beneficio: A, governanca: I}
  - {atividade: Aprovar mudança de meta, projeto: C, indicador: C, beneficio: R, governanca: A}

classificacao:
  realizado_a_partir_de: "1"
  parcial_a_partir_de: "0.5"

monitoramento:
  cadencia: {operacional: semanal, tatica: mensal, estrategica: trimestral}
  leituras:
    - {indicador: IND-2, data: 2026-06-30, valor: "55", origem: pessoa, informado_por: Coordenador de Contabilidade}

decisoes:
  - id: DEC-1
    data: 2026-04-15
    tipo: mudanca_escopo
    descricao: Conciliação de contas a pagar adiada para a segunda fase.
    afeta: []
    justificativa: Dependência de fornecedor. Avaliado que não altera indicador, linha de base nem meta.
    decidido_por: Gerente de Controladoria

medicoes:
  - {id: MED-1, indicador: IND-1, data: 2026-07-31, valor: "8", fonte: Calendário de fechamento, origem: pessoa, informado_por: Coordenador de Contabilidade}

resultados:
  - {indicador: IND-1, medicao: MED-1, realizacao: "2/3", classificacao: parcial, ferramenta: calculadora@0.1.0}

atribuicao:
  - indicador: IND-1
    fatores_concorrentes:
      - "O mês medido incluiu fechamento de trimestre, com volume maior que o usual."
    conclusao: parcial
    limitacoes: Uma única medição; comparar de novo nas duas datas seguintes.

premissas:
  - {id: PRE-1, texto: "O volume de lançamentos se mantém estável no período.", bloqueante: false, situacao: aberta, criada_por: agente}

documentos:
  - {id: DOC-1, tipo: proposta_de_valor, versao: 1, arquivo: 01-definicao/proposta-de-valor-v1.md, sha256: "<hash>", aprovado_por: Gerente de Controladoria, aprovado_em: 2026-02-10}

execucao:
  nos:
    - {id: B2, estado: verificado, nivel_exigido: 2, nivel_alcancado: 3}
```

## 7. O que fica fora desta versão

- Vários projetos em um mesmo arquivo (portfólio).
- Valores financeiros com moeda e conversão.
- Integração com fontes de dados; toda medição é informada por uma pessoa.
- Assinatura digital das aprovações (hoje, nome e data sobre um hash).

## 8. Ajustes feitos na Fase 1 (09/11/2026)

- **Formato decidido (Q13): `projeto.json`.** O exemplo em YAML acima fica como leitura; o arquivo real é gerado por `tools/exemplo.py` no repositório `trilha-de-valor/`.
- **Campo novo `documentos[].referencia`** na Proposta de Valor: retrato de linha de base e meta de cada indicador no momento da aprovação. É contra ele que as regras K1 e K2 comparam.
- **Conclusão de um nó:** um nó está concluído quando atinge o nível de garantia exigido (operações de texto, nível 1; verificações, nível 2), e um portão, quando aprovado. Portões só podem depender de verificações.
- **Faixas (Q8):** `"1"` e `"1/2"` como padrão.
- **Critérios de auditoria A1 a A7** implementados em `tools/auditar.py`.

## 8.1 Ajustes feitos na Fase 2 (09/11/2026)

- **Orquestrador `tools/trilha.py`**: único caminho para alterar o estado (`iniciar`, `status`, `aplicar`, `verificar`, `calcular`, `previa`, `aprovar`). Recusa nó fora de ordem, bloco protegido, mudança de etapa por proposta e projeto real dentro do repositório.
- **Entregáveis gerados do estado** (`tools/entregaveis.py`): o agente não escreve os documentos; propõe o conteúdo do estado, e o documento é derivado dele no portão.
- **Blocos novos:** `anotacoes[]` (`id`, `no`, `texto`), para observações de um passo; `encaminhamentos[]` (`id`, `indicador`, `decisao`, `acao`, `responsavel`, `prazo`), para as decisões do passo 5 da Mensuração.
- **Regra nova na verificação V3:** todo resultado tem decisão registrada; toda medição tem resultado calculado.
- **Retrabalho:** alterar um passo invalida as verificações seguintes da mesma etapa; corrigir uma medição apaga os resultados, que precisam ser recalculados. Etapa aprovada não aceita alteração.
- **Todo registro de evidência** traz o modelo informado e o hash do estado depois da operação.

## 8.2 Ajustes feitos na Fase 3 (10/11/2026)

- **Sustentação transversal no grafo:** S1 (papéis) depende de G1; S2 (transição) depende de G2 e é seguida de uma verificação (VT) e de um portão próprio (GT, aceite do Termo de Transição), que não muda a etapa; S3 e S4 dependem de G3; V4 depende de S1, GT e S4. Motivo: o guia pede a transição antes de a equipe sair e as lições depois da última medição.
- **Blocos novos:** `riscos[]` (`id`, `tipo`, `descricao`, `impacto_no_valor`, `acao`, `responsavel`, `prazo`) e `catalogo[]` (`id`, `indicador`, `dificuldade`, `util_para_decidir`, `observacao`).
- **`transicao`:** `data`, `recebido_por`, `itens`, `acessos`, `apoio_ate_primeira_medicao`, `pendencias`.
- **`licoes[]`:** `id`, `etapa`, `licao`, `acao`, `responsavel`, `prazo`. A V4 reprova lição sem ação, responsável ou prazo, e indicador fora do catálogo.
- **`monitoramento`:** cadência com `operacional`, `revisao_valor` e `executiva`; leituras com `id` próprio (`LEI-n`), para se acumularem entre os ciclos.
- **Projeto `encerrado`** não aceita mais alterações.

## 9. Decisões da Fase 0 (aceitas em 09/11/2026)

| # | Decisão | Proposta |
|---|---|---|
| Q8 | Faixas de classificação | Configuráveis por projeto; padrão 100% e 50% |
| Q13 | Formato do arquivo de estado | JSON como formato gravado; YAML só se PyYAML for aceito como dependência |
| Q14 | Nomes de pessoas no estado | Só cargos no exemplo público; em uso real, o arquivo fica fora do repositório |
