# Trilha de Valor: assistente

Assistente de IA que conduz um projeto pelas quatro etapas da Trilha de Valor (Definição de Valor, Monitoramento de Valor, Mensuração dos Benefícios, Governança e Melhoria Contínua) e deixa uma trilha auditável do que foi feito.

Parte de um trabalho de conclusão de MBA em Gerenciamento de Projetos, desenvolvido em dupla (método Design Science Research).

## Situação (17/11/2026)

| Parte | Situação |
|---|---|
| Ferramentas determinísticas e orquestrador (`tools/`) | Prontos; 91 testes automatizados |
| Skills das quatro etapas e skill de entrada (`.claude/skills/`) | Prontas; todas chegaram ao portão de aprovação em testes de desenvolvimento com subagentes (`docs/registro-das-execucoes.md`) |
| Teste de robustez | Duas rodadas com subagentes: contas, verificações e estrutura idênticas entre as execuções; limiar ainda não dado como atendido (falta a execução conduzida por pessoa) |
| Testes de regra | Oito situações (estimar sem dado, dado real, pular aprovação, arredondar resultado, mudar meta sem decisão, entre outras): todas recusadas, julgadas pelo estado gravado |
| Avaliação com especialistas | Rubrica congelada (`docs/rubrica-de-avaliacao.md`); preparada e não realizada |
| Projeto de exemplo fictício | Percorre as quatro etapas até o encerramento. Gerado por um roteiro que usa o orquestrador, não por uma execução do assistente |

Os testes com subagentes usam o mesmo modelo que ajudou a construir o assistente e uma pessoa simulada: são testes de desenvolvimento, não a avaliação do artefato.

## Ideia central

O agente propõe; ferramentas determinísticas verificam; uma pessoa aprova. O agente não é testemunha do próprio trabalho.

- Toda conta passa pela **calculadora**, com aritmética exata.
- O **verificador** checa completude, consistência entre etapas e integridade do estado.
- O **DAG** define a ordem das operações; nenhuma etapa avança sem verificação e aprovação.
- O **registro de evidências** é encadeado por hash; a **auditoria** refaz os critérios de aprovação a partir dos arquivos.

## Como usar as ferramentas

Requer Python 3.9 ou superior. Sem dependências externas. Rode a partir da raiz do repositório.

```bash
python3 -m unittest discover -s tools/tests -t .
```

```bash
python3 -m tools.calculadora 10 7 8
```

```bash
python3 -m tools.exemplo
```

```bash
python3 -m tools.auditar projetos/exemplo-ficticio
```

| Módulo | Função |
|---|---|
| `tools/trilha.py` | Orquestrador: único caminho para alterar o estado; registra a evidência de cada operação |
| `tools/entregaveis.py` | Gera os documentos a partir do estado |
| `tools/calculadora.py` | Realização da meta = (resultado − linha de base) ÷ (meta − linha de base); classificação por faixas |
| `tools/estado.py` | Leitura, gravação e hash do `projeto.json` |
| `tools/verificador.py` | Regras C (completude), K (consistência) e I (integridade) |
| `tools/dag.py` | DAG das operações e validação do grafo |
| `tools/evidencias.py` | Registro só de acréscimo, encadeado por SHA-256 |
| `tools/auditar.py` | Critérios A1 a A7 de aprovação de uma execução |
| `tools/exemplo.py` | Gera o projeto fictício de exemplo |
| `tools/comparar.py` | Compara várias execuções do mesmo caso (protocolo de robustez) |
| `tools/apendice.py` | Gera, a partir do código, as tabelas do apêndice do guia |

## Como usar o assistente

Abra esta pasta no Claude Code e peça, por exemplo, "quero definir o valor de um projeto pela Trilha de Valor". As regras de comportamento estão em `CLAUDE.md`, e as skills, em `.claude/skills/`. Use apenas dados fictícios dentro do repositório.

## Limites

- A aprovação é registrada pelo assistente a pedido da pessoa; o sistema não tem como provar a identidade de quem aprovou.

- A cadeia de hash **detecta** adulteração, mas não a impede. Guarde o último hash fora do alcance do agente (por exemplo, em um commit) e passe-o à auditoria com `--ancora`.
- A verificação cobre contas, estrutura e ordem. **Não cobre a qualidade do conteúdo** gerado pelo modelo (se um indicador é bom, se o texto faz sentido). Isso depende de avaliação humana.
- A etapa de Governança e Melhoria Contínua é transversal: a transição para a operação é aceita logo depois do Monitoramento, antes de a equipe do projeto sair.
- As operações de texto são registradas, e a verificação acontece por etapa, antes de cada aprovação; ainda não há checagem individual por operação.
- As respostas de um modelo de linguagem variam entre execuções.

## Dados sigilosos

Use apenas dados fictícios neste repositório. Não registre dados reais de empresas, projetos ou pessoas. O `.gitignore` exclui tudo em `projetos/`, exceto o exemplo fictício.

## Licença

Código (`tools/`) sob a licença MIT (`LICENSE`). Textos (`docs/`, skills, `CLAUDE.md` e o exemplo fictício) sob a Creative Commons Atribuição 4.0 Internacional (CC BY 4.0), conforme `LICENSE-docs.md`.
