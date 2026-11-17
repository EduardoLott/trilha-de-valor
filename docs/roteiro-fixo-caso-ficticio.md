# Roteiro fixo do caso fictício (protocolo de robustez)

Versão 1.1, de 14/11/2026 (a versão 1.0 foi usada na primeira rodada; mudanças no fim do arquivo). Respostas da "pessoa" para as cinco execuções do mesmo caso. **Todos os dados são inventados.** Não altere o roteiro entre as execuções; se precisar mudar, registre a nova versão e refaça todas.

## Como usar

- Quem responde ao assistente (uma pessoa ou um agente simulador) usa **só** o que está aqui. Para qualquer pergunta sem resposta no roteiro, a resposta é "não sei".
- As respostas são dadas quando o assistente pergunta, uma de cada vez, e não adiantadas.
- O caso é registrado de forma retrospectiva: o projeto aconteceu entre fevereiro e outubro de 2026.
- Pasta de cada execução: `projetos/robustez-r2-N` (N de 1 a 5), com `--id robustez-r2-N`.
- A data da sessão é informada por quem conduz o teste, no início. A Ana usa essa data sempre que disser "hoje".

## Quem fala

Ana (personagem fictícia), analista do Escritório de Projetos.

- Abertura: "Sou a Ana, do Escritório de Projetos. Quero registrar na Trilha de Valor o projeto Automação do fechamento financeiro, do início ao fim. Os dados são fictícios. O projeto já terminou; estou registrando o histórico."
- Sempre que o assistente mostrar o que vai registrar e pedir confirmação: "Sim, pode registrar."
- Se o assistente mostrar um texto que ele mesmo redigiu e perguntar se ela concorda com a redação: "Concordo com esse texto."
- Se o assistente perguntar que data é "hoje": a data da sessão.
- Se o assistente apontar datas ou prazos no passado: "Sim, é um registro retrospectivo; as datas estão certas."

## Definição de Valor

- Problema: "O fechamento mensal da Controladoria leva 10 dias úteis, com muita conciliação manual em planilha e retrabalho. Isso atrasa os relatórios gerenciais. Quem sofre é a Controladoria e a diretoria, que decide com informação atrasada. Se nada for feito, continua assim."
- Objetivo da organização: "Dar à gestão informação financeira mais cedo para decidir."
- Solução: "Automatizar conciliações e lançamentos recorrentes do fechamento mensal."
- Benefício: "Fechamento mensal mais rápido. O responsável pelo benefício é o Gerente de Controladoria. Os analistas precisam usar a conciliação automática em vez da planilha, e as áreas precisam enviar os dados até o segundo dia útil. Depende da integração com o sistema de gestão em produção. Esperamos o benefício até 30/09/2026."
- Indicadores: "Tempo de fechamento: dias úteis entre o fim do mês e a publicação do fechamento; fonte, o calendário de fechamento da Controladoria; mensal; quem mede é o Coordenador de Contabilidade. Adoção: conciliações automáticas dividido pelo total de conciliações do mês, em percentual; fonte, o registro do sistema de conciliação; mensal; mesmo responsável."
- Se o assistente propuser tipo e sentido e pedir confirmação: "Sim, é isso."
- Linha de base do tempo de fechamento: "10 dias úteis, média dos 6 fechamentos anteriores, em 31/01/2026. Informa o Coordenador de Contabilidade."
- Meta do tempo de fechamento: "7 dias úteis até 30/09/2026. Define o Gerente de Controladoria."
- Linha de base da adoção: "Zero em 31/01/2026, o processo era todo manual. Informa o Coordenador de Contabilidade."
- Meta da adoção: "80% até 31/08/2026. Define o Gerente de Controladoria."
- Método de comprovação: "Não sei qual escolher. Temos a linha de base e o processo não deve mudar muito fora o projeto."
- Se o assistente recomendar um método e pedir confirmação: "Pode ser esse, confirmo."
- Critério de sucesso: "Meta atingida e mantida por três fechamentos seguidos."
- Suposições (dita junto com o método de comprovação): "Estamos supondo que o volume de lançamentos se mantém estável no período."
- Faixas de classificação: "O padrão."
- Papéis: "Projeto: Gerente do Projeto. Indicador: Coordenador de Contabilidade. Benefício: Gerente de Controladoria. Governança: Escritório de Projetos."
- RACI: "Medir o tempo de fechamento: executa o Coordenador de Contabilidade, responde o Gerente de Controladoria, projeto e governança são informados. Aprovar mudança de meta: conduz o Gerente de Controladoria, aprova a governança, projeto e indicador são consultados."
- Fontes e acesso: "As duas fontes estão acessíveis."
- Divergências entre áreas: "Não sei."
- Diante da prévia: "Parece bom."
- Pergunta direta de aprovação: "Sim, aprovo. O Gerente de Controladoria me pediu para registrar a aprovação dele."

## Monitoramento de Valor

- Cadência: "Reunião semanal do projeto, revisão mensal na Controladoria e comitê executivo trimestral."
- Leitura da adoção: "55% em 30/06/2026. Informa o Coordenador de Contabilidade."
- Leitura do tempo de fechamento: "Só dá para medir depois da implantação."
- Explicação do desvio: "Duas áreas ainda fazem parte das conciliações na planilha."
- Mudanças necessárias: "Em parte: duas áreas ainda usam a planilha e enviam os dados depois do segundo dia útil."
- Capacitação e integrações: "Treinamento feito; integração em produção."
- Risco: "As áreas continuarem enviando os dados fora do prazo; sem isso o fechamento não fica mais rápido. Ação: acompanhar o envio por área na revisão mensal. Responsável: Gerente de Controladoria. Prazo: 31/07/2026. Hoje está concluído."
- Oportunidades: "Nenhuma."
- Mudança de escopo: "A conciliação de contas a pagar foi adiada para a segunda fase, por dependência de fornecedor. Decidiu o Gerente de Controladoria, em 15/04/2026."
- Gatilho: altera benefício, indicador, linha de base, meta ou prazo? "Não." Novas dependências ou riscos? "Não." Continua alinhada? "Sim."
- A implantação terminou? "Sim, em 30/06/2026."
- Datas de medição: "31/07/2026, 31/08/2026 e 30/09/2026, para o tempo de fechamento. Mede o Coordenador de Contabilidade; a fonte continua acessível."
- Diante da prévia: "Ok."
- Pergunta direta de aprovação: "Sim, aprovo, a pedido do Gerente de Controladoria."

## Transição (logo depois do Monitoramento)

- Data: "30/06/2026." Quem assume: "O Gerente de Controladoria." Cientes: "Sim."
- Entregue: "As fichas dos indicadores na versão vigente, a Proposta de Valor aprovada e o calendário de medição."
- Acessos: "Mantidos para a Controladoria, ao calendário de fechamento e ao sistema de conciliação."
- Pendências: "Acompanhar o envio de dados por área, com o Gerente de Controladoria."
- Disponível até a primeira medição: "O Gerente do Projeto."
- Aceite, pergunta direta: "Registro o aceite do Gerente de Controladoria, a pedido dele, e o do Escritório de Projetos, com autorização da minha gestora."

## Mensuração dos Benefícios

- Condições: "Responsáveis mantidos, fontes acessíveis, datas mantidas. Nenhuma pendência nova; continua a do Termo de Transição, de acompanhar o envio de dados por área."
- Medições do tempo de fechamento: "8 dias úteis em 31/07/2026; 8 em 31/08/2026; 7 em 30/09/2026. Fonte: calendário de fechamento. Informa o Coordenador de Contabilidade. Mesma fórmula, unidade e fonte."
- Medição da adoção: "Não temos o dado de setembro, que seria de 30/09/2026; o relatório do sistema não foi extraído. A Controladoria extrai até 30/11/2026."
- Fatores concorrentes: "Julho incluiu o fechamento de trimestre, com volume maior que o usual. Fora isso, nada mudou."
- Se o assistente apontar premissa contrariada: "Contraria, pode marcar."
- Atribuição: "Em parte."
- Efeitos não previstos: "Nenhum que eu saiba."
- Decisão: "Manter o acompanhamento: continuar medindo a cada fechamento até completar três fechamentos seguidos na meta. Responsável: Gerente de Controladoria. Prazo: 31/12/2026."
- Diante da prévia: "Ok."
- Pergunta direta de aprovação: "Sim, aprovo, a pedido do Gerente de Controladoria."

## Governança e Melhoria Contínua

- Papéis: "Continuam os mesmos. Confirmo hoje." (a data da sessão)
- Lição: "A primeira medição caiu em mês de fechamento de trimestre, o que dificultou a atribuição. Nos próximos projetos, marcar a primeira medição fora de meses atípicos. Responsável: Escritório de Projetos. Prazo: 15/12/2026. É da etapa de mensuração."
- Outras lições e falhas no uso da Trilha: "Nenhuma."
- Catálogo: "Tempo de fechamento: fácil de medir, ajudou a decidir. Adoção: dificuldade média, depende de extração manual; ajudou em parte."
- Premissas em aberto, se o assistente perguntar: "Não sei."
- Diante da prévia: "Fechado."
- Pergunta direta de aprovação: "Sim, aprovo em nome do Escritório de Projetos, com autorização da minha gestora."

## Resultado esperado das partes determinísticas

| Medição | Linha de base | Meta | Resultado | Realização | Classificação |
|---|---|---|---|---|---|
| 31/07/2026 | 10 | 7 | 8 | 2/3 | parcial |
| 31/08/2026 | 10 | 7 | 8 | 2/3 | parcial |
| 30/09/2026 | 10 | 7 | 7 | 1 | realizado |

Cinco documentos aprovados, etapa final `encerrado`, auditoria aprovada.

## Mudanças da versão 1.1

- A suposição de volume estável passou a ser dita pela pessoa na Definição (na 1.0, a fala sobre premissa contrariada ficava sem objeto quando o assistente não criava essa premissa).
- "Hoje" passou a ter data definida, informada por quem conduz.
- O dado de adoção não medido ganhou data de referência.
- A resposta sobre pendências na Mensuração deixou de contradizer o Termo de Transição.
- Nova resposta para quando o assistente pede concordância com um texto redigido por ele.
