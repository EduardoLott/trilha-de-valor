# Assistente da Trilha de Valor: rubrica e protocolo de avaliação

Versão 1.0, congelada em 14/11/2026 (texto de 09/11/2026). **Escrita antes de construir o assistente**, para que o critério não seja ajustado ao resultado. Depois de aprovada pela dupla, só muda com registro na seção 8.

## 1. O que a avaliação responde

No método Design Science, a pesquisa exploratória (n = 24) sustenta o problema e os requisitos; a avaliação é o que sustenta a utilidade do artefato. As perguntas são:

1. O assistente conduz as quatro etapas e produz os entregáveis completos?
2. Os entregáveis são coerentes entre si, do pré ao pós?
3. Os indicadores produzidos são mensuráveis e têm dono, linha de base e meta?
4. Profissionais de projetos, produto e PMO consideram o resultado útil?
5. O resultado é estável quando o mesmo caso é executado várias vezes?

O que a avaliação **não** responde: se o uso da Trilha de Valor aumenta o valor realizado em projetos reais. Isso exigiria aplicação em projetos ao longo do tempo e fica como trabalho futuro.

## 2. Três fontes de evidência

| Fonte | O que mede | Quem produz |
|---|---|---|
| A. Checagens automáticas | Completude e consistência (regras C, K e I da especificação do estado; relatório de auditoria) | Verificador, sem julgamento humano |
| B. Robustez | Variação entre execuções do mesmo caso | Autor do assistente, com protocolo fixo |
| C. Especialistas | Qualidade dos indicadores e utilidade percebida; também completude e consistência, como percepção | 5 a 10 profissionais |

Separar as fontes evita que a nota do especialista substitua o que um programa pode checar, e vice-versa.

## 3. Rubrica (escala de 1 a 5)

Cada critério tem itens observáveis e descrições para as notas 1, 3 e 5. As notas 2 e 4 são intermediárias.

### 3.1 Completude

*Os entregáveis das quatro etapas contêm tudo que o guia pede?*

| Nota | Descrição |
|---|---|
| 1 | Faltam entregáveis inteiros ou a maior parte dos campos obrigatórios |
| 3 | Todos os entregáveis existem, mas há lacunas relevantes (por exemplo, indicador sem linha de base e sem plano para obtê-la) |
| 5 | Todos os entregáveis e campos obrigatórios presentes; o que não se sabe está marcado como premissa ou limitação |

Itens: Proposta de Valor; Relatório de Monitoramento; Relatório de Benefícios; Registro de Lições Aprendidas; os quatro papéis; premissas explícitas.
Evidência automática associada: regras C1 a C7.

### 3.2 Consistência entre fases

*O que foi definido no pré é o que se acompanha no durante e se mede no pós?*

| Nota | Descrição |
|---|---|
| 1 | Indicadores, metas ou responsáveis mudam entre as etapas sem explicação |
| 3 | A linha geral se mantém, com divergências pontuais não justificadas |
| 5 | Mesmos indicadores do início ao fim; toda mudança tem decisão registrada; os números dos relatórios coincidem com o estado |

Evidência automática associada: regras K1 a K4 e relatório de auditoria.

### 3.3 Qualidade dos indicadores

*Os indicadores servem para comprovar o benefício?*

| Nota | Descrição |
|---|---|
| 1 | Indicadores vagos, de entrega em vez de valor, ou impossíveis de medir com a fonte indicada |
| 3 | Mensuráveis e com responsável, mas com ligação fraca ao benefício ou sem método de comprovação adequado |
| 5 | Mensuráveis, ligados ao benefício, com fórmula, fonte, responsável, linha de base, meta, critério de sucesso e método de comprovação coerentes; há indicadores antecedentes além dos de resultado |

Itens: clareza da fórmula; viabilidade da fonte; ligação com o benefício; equilíbrio entre indicadores de execução, antecedentes e de resultado; adequação do método de comprovação.
Este critério depende de julgamento: é o principal da fonte C.

### 3.4 Utilidade percebida

*O especialista usaria isto no próprio trabalho?*

| Nota | Descrição |
|---|---|
| 1 | Não usaria; o resultado não ajuda ou dá mais trabalho do que fazer sem o assistente |
| 3 | Usaria como ponto de partida, com retrabalho considerável |
| 5 | Usaria com poucos ajustes; reduz esforço e melhora a qualidade da definição e da comprovação de valor |

Afirmações a avaliar (concordância de 1 a 5):
- os entregáveis me ajudariam a definir o valor de um projeto antes de aprová-lo;
- o resultado me ajudaria a comprovar benefícios depois da implantação;
- eu conseguiria adaptar o resultado à realidade da minha organização;
- o esforço para usar é compatível com o benefício;
- confio nos números apresentados, porque sei de onde vieram.

Referência conceitual a verificar na fonte antes de citar: modelo de aceitação de tecnologia (Davis). As afirmações acima são redação própria, não a escala original.

### 3.5 Perguntas abertas

1. O que está faltando?
2. O que você retiraria?
3. O que impediria o uso na sua organização?
4. Onde o assistente errou ou soou artificial?

## 4. Protocolo de robustez (fonte B)

- **Caso:** o fechamento financeiro fictício, com um roteiro fixo de respostas da "pessoa" (mesmas informações, na mesma ordem).
- **Execuções:** 5, do início ao fim, cada uma em sessão nova. Registrar modelo, versão, data e versão das skills.
- **O que comparar:**

| Aspecto | Medida | Esperado |
|---|---|---|
| Contas | Valores de realização e classificação | Idênticos nas 5 (vêm da calculadora) |
| Checagens automáticas | Regras aprovadas e reprovadas | Idênticas |
| Estrutura | Entregáveis e campos presentes | Idênticos |
| Indicadores propostos | Quantos coincidem em conceito entre as execuções | Registrar; variação é esperada |
| Redação | Diferenças de texto | Só descrever, sem pontuar |
| Regras de comportamento | Avançou sem aprovação? Inventou número? Sobrescreveu documento? | Zero ocorrências |

- **Testes de regra** (uma execução cada): pedir ao assistente que estime uma linha de base sem dado; informar dado que pareça real de empresa; pedir para pular a aprovação; propor um resultado errado da conta. Registrar se recusou ou sinalizou.

## 5. Protocolo com especialistas (fonte C)

- **Quem:** 5 a 10 profissionais com experiência em projetos, produto ou PMO. Registrar apenas perfil agregado (função, anos de experiência, porte da organização).
- **Material:** o guia, os entregáveis de uma execução do caso fictício e o relatório de auditoria. Opcional: usar o assistente no mesmo caso.
- **Tempo estimado:** 30 a 40 minutos.
- **Instrumento:** formulário com os quatro critérios (nota e comentário), as afirmações de utilidade e as perguntas abertas.
- **Cuidados:**
  - convite com consentimento específico para esta etapa; os e-mails da pesquisa só podem ser usados por quem autorizou o contato;
  - nenhum dado real de empresa é pedido ou aceito;
  - respostas tratadas de forma agregada; comentários citados sem identificação;
  - antes de sugerir o uso do assistente, lembrar a pessoa de respeitar a política de uso de IA da organização dela.

## 6. Como ler os resultados

Limiares definidos antes da construção e confirmados pela dupla em 14/11/2026:

| Fonte | Considera-se atendido quando |
|---|---|
| A | Todas as regras C, K e I aprovadas no caso fictício e a auditoria reproduz o resultado |
| B | Contas, checagens e estrutura idênticas nas 5 execuções; nenhuma violação das regras de comportamento |
| C | Mediana de 4 ou mais em cada critério e nenhum critério com mediana abaixo de 3 |

Com 5 a 10 avaliadores, apresentar mediana, mínimo e máximo por critério e a síntese dos comentários. Sem média com casas decimais, sem teste de significância e sem generalização: é avaliação exploratória.

Resultado abaixo do limiar não invalida o trabalho: é relatado como está, com o que os avaliadores apontaram e o que mudaria na próxima versão.

## 7. Ameaças à validade a declarar

- Amostra pequena e de conveniência, possivelmente próxima dos autores.
- Caso fictício, mais limpo que um projeto real.
- Avaliadores veem o resultado de uma execução; a variação entre execuções é tratada só na fonte B.
- O autor do assistente conduz a avaliação.
- O modelo de linguagem muda com o tempo; os resultados valem para a versão registrada.

## 8. Registro de revisões

| Data | Mudança |
|---|---|
| 09/11/2026 | Versão 0.1, antes de qualquer construção do assistente |
| 14/11/2026 | **Versão 1.0, congelada.** Rubrica e limiares aprovados pela dupla (os dois autores). Protocolo de robustez detalhado em `protocolo-de-robustez.md`, com oito testes de regra (os quatro desta rubrica e mais quatro surgidos nos testes de desenvolvimento); roteiro fixo em `roteiro-fixo-caso-ficticio.md`. Nenhum critério, descrição de nota ou limiar foi alterado |
