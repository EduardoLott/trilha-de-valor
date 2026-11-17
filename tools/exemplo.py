"""Gera o projeto de exemplo (fictício) da Trilha de Valor pelo orquestrador.

Todos os dados são inventados. O roteiro abaixo percorre Definição, Monitoramento
e Mensuração com as mesmas operações que o assistente usa (tools.trilha), mas é
um script: não é uma execução do assistente com um modelo de IA.

Uso: python3 -m tools.exemplo [pasta]   (padrão: projetos/exemplo-ficticio)
"""
import shutil
import sys
from pathlib import Path

from . import evidencias, trilha
from .estado import ARQUIVO_EVIDENCIAS, carregar

MODELO = "roteiro de demonstração (sem modelo de IA)"
COORD, GERENTE = "Coordenador de Contabilidade", "Gerente de Controladoria"
DATAS = {"definicao": "2026-02-10T12:00:00+00:00", "monitoramento": "2026-06-30T12:00:00+00:00",
         "mensuracao": "2026-10-05T12:00:00+00:00", "sustentacao": "2026-10-15T12:00:00+00:00"}

# Proposta aplicada em cada nó de execução
PROPOSTAS = {
    "D1": {
        "projeto": {"problema": "O fechamento mensal leva 10 dias úteis e atrasa os relatórios gerenciais.",
                    "descricao": "Automatizar conciliações e lançamentos recorrentes do fechamento mensal."},
        "objetivos": [{"id": "OBJ-1", "descricao": "Dar à gestão informação financeira mais cedo para decidir."}],
    },
    "D2": {"beneficios": [{
        "id": "BEN-1", "descricao": "Fechamento mensal mais rápido.", "objetivo": "OBJ-1", "responsavel": GERENTE,
        "mudancas_necessarias": ["Analistas passam a usar a conciliação automática em vez da planilha.",
                                 "Áreas enviam os dados até o segundo dia útil."],
        "condicoes": ["Integração com o sistema de gestão em produção."],
        "prazo": "2026-09-30"}]},
    "D3": {
        "indicadores": [
            {"id": "IND-1", "nome": "Tempo de fechamento mensal", "tipo": "resultado",
             "formula": "Dias úteis entre o fim do mês e a publicação do fechamento", "unidade": "dias úteis",
             "sentido": "menor_melhor", "fonte": "Calendário de fechamento da Controladoria",
             "periodicidade": "mensal", "responsavel": COORD, "situacao": "ativo"},
            {"id": "IND-2", "nome": "Conciliações feitas pela automação", "tipo": "antecedente",
             "formula": "Conciliações automáticas dividido pelo total de conciliações do mês", "unidade": "percentual",
             "sentido": "maior_melhor", "fonte": "Registro do sistema de conciliação",
             "periodicidade": "mensal", "responsavel": COORD, "situacao": "ativo"},
        ],
        "beneficios": [{"id": "BEN-1", "indicadores": ["IND-1", "IND-2"]}],
    },
    "D4": {
        "indicadores": [
            {"id": "IND-1",
             "linha_de_base": {"valor": "10", "data": "2026-01-31", "fonte": "Média dos 6 fechamentos anteriores",
                               "origem": "pessoa", "informado_por": COORD},
             "meta": {"valor": "7", "prazo": "2026-09-30", "origem": "pessoa", "informado_por": GERENTE},
             "criterio_sucesso": "Meta atingida e mantida por três fechamentos seguidos.",
             "metodo_comprovacao": "antes_depois"},
            {"id": "IND-2",
             "linha_de_base": {"valor": "0", "data": "2026-01-31", "fonte": "Processo manual",
                               "origem": "pessoa", "informado_por": COORD},
             "meta": {"valor": "80", "prazo": "2026-08-31", "origem": "pessoa", "informado_por": GERENTE}},
        ],
        "classificacao": {"realizado_a_partir_de": "1", "parcial_a_partir_de": "1/2"},
        "premissas": [{"id": "PRE-1", "texto": "O volume de lançamentos se mantém estável no período.",
                       "bloqueante": False, "situacao": "aberta", "criada_por": "agente"}],
    },
    "D5": {
        "papeis": {"projeto": "Gerente do Projeto", "indicador": COORD, "beneficio": GERENTE,
                   "governanca": "Escritório de Projetos"},
        "raci": [
            {"atividade": "Medir o tempo de fechamento", "projeto": "I", "indicador": "R", "beneficio": "A", "governanca": "I"},
            {"atividade": "Aprovar mudança de meta", "projeto": "C", "indicador": "C", "beneficio": "R", "governanca": "A"},
        ],
    },
    "M1": {"monitoramento": {"cadencia": {"operacional": "semanal", "revisao_valor": "mensal", "executiva": "trimestral"}}},
    "M2": {"monitoramento": {"leituras": [{"id": "LEI-1", "indicador": "IND-2", "data": "2026-06-30", "valor": "55",
                                           "origem": "pessoa", "informado_por": COORD}]}},
    "M3": {"anotacoes": [{"redacao": "pessoa", "id": "NOTA-1", "no": "M3",
                          "texto": "Adoção em andamento: parte das áreas ainda envia os dados depois do segundo dia útil."}]},
    "M4": {"riscos": [{
        "id": "RIS-1", "tipo": "risco", "descricao": "Áreas continuam enviando dados depois do segundo dia útil.",
        "impacto_no_valor": "Sem os dados no prazo, o tempo de fechamento não cai.",
        "acao": "Acompanhar o envio por área na revisão de valor mensal.", "responsavel": GERENTE, "prazo": "2026-07-31"}],
           "decisoes": [{
        "id": "DEC-1", "data": "2026-04-15", "tipo": "mudanca_escopo",
        "gatilho": {"altera_valor": False, "novas_dependencias": False, "alinhada": True},
        "descricao": "Conciliação de contas a pagar adiada para a segunda fase.", "afeta": [],
        "justificativa": "Dependência de fornecedor. Avaliado que não altera indicador, linha de base nem meta.",
        "decidido_por": GERENTE}]},
    "M5": {"indicadores": [{"id": "IND-1", "datas_medicao": ["2026-07-31", "2026-08-31", "2026-09-30"]}]},
    "B1": {"anotacoes": [{"redacao": "pessoa", "id": "NOTA-2", "no": "B1",
                          "texto": "Condições confirmadas: responsáveis mantidos, fonte acessível e datas de medição definidas."}]},
    "B2": {"medicoes": [
        {"id": "MED-1", "indicador": "IND-1", "data": "2026-07-31", "valor": "8",
         "fonte": "Calendário de fechamento", "origem": "pessoa", "informado_por": COORD},
        {"id": "MED-2", "indicador": "IND-1", "data": "2026-08-31", "valor": "8",
         "fonte": "Calendário de fechamento", "origem": "pessoa", "informado_por": COORD},
        {"id": "MED-3", "indicador": "IND-1", "data": "2026-09-30", "valor": "7",
         "fonte": "Calendário de fechamento", "origem": "pessoa", "informado_por": COORD}]},
    "B3": {"atribuicao": [{
        "redacao": "pessoa",
        "indicador": "IND-1",
        "fatores_concorrentes": ["O mês medido incluiu fechamento de trimestre, com volume maior que o usual."],
        "conclusao": "parcial",
        "limitacoes": "A primeira medição caiu em mês atípico; a meta foi atingida só na terceira medição."}]},
    "B5": {"encaminhamentos": [{
        "id": "ENC-1", "indicador": "IND-1", "decisao": "manter",
        "acao": "Continuar medindo a cada fechamento até completar três fechamentos seguidos na meta.",
        "responsavel": GERENTE, "prazo": "2026-12-31"}]},
    "S1": {"anotacoes": [{"redacao": "pessoa", "id": "NOTA-3", "no": "S1",
                          "texto": "Papéis confirmados no encerramento do projeto, sem mudança de pessoas."}]},
    "S2": {"transicao": {
        "data": "2026-06-30", "recebido_por": GERENTE,
        "itens": ["Fichas dos indicadores na versão vigente", "Proposta de Valor aprovada",
                  "Calendário de medição pós-implementação"],
        "acessos": "Acesso ao calendário de fechamento e ao sistema de conciliação mantido para a Controladoria",
        "apoio_ate_primeira_medicao": "Gerente do Projeto",
        "pendencias": ["Acompanhar o envio de dados por área (RIS-1), com o Gerente de Controladoria"]}},
    "S3": {"licoes": [{
        "id": "LIC-1", "etapa": "mensuracao",
        "licao": "A primeira medição caiu em mês de fechamento de trimestre, o que dificultou a atribuição.",
        "acao": "Nos próximos projetos, marcar a primeira medição fora de meses atípicos.",
        "responsavel": "Escritório de Projetos", "prazo": "2026-12-15"}]},
    "S4": {"catalogo": [
        {"id": "CAT-1", "indicador": "IND-1", "dificuldade": "baixa", "util_para_decidir": "sim",
         "observacao": "Medido direto no calendário de fechamento."},
        {"id": "CAT-2", "indicador": "IND-2", "dificuldade": "media", "util_para_decidir": "em_parte",
         "observacao": "Depende de extração manual do relatório do sistema."}]},
}

# No exemplo, todos os textos são tratados como palavras da pessoa.
for _proposta in PROPOSTAS.values():
    for _bloco in trilha.COM_AUTORIA:
        for _item in _proposta.get(_bloco, []):
            _item.setdefault("redacao", "pessoa")
    if "transicao" in _proposta:
        _proposta["transicao"].setdefault("redacao", "pessoa")

# Momento (fictício) de cada nó transversal
DATAS_NO = {"S1": "2026-06-30T12:00:00+00:00", "S2": "2026-06-30T13:00:00+00:00", "VT": "2026-06-30T13:00:00+00:00",
            "GT": "2026-06-30T13:00:00+00:00"}


def gerar(pasta, ate="mensuracao"):
    """Monta o exemplo na pasta, até a etapa indicada, e devolve o último hash da cadeia."""
    pasta = Path(pasta)
    if pasta.exists() and any(pasta.iterdir()):
        # Só apaga uma pasta que seja, de fato, um exemplo gerado antes por este script.
        try:
            anterior = carregar(pasta)["projeto"]
        except (OSError, ValueError, KeyError):
            anterior = {}
        if anterior.get("id") != "exemplo-ficticio" or anterior.get("ficticio") is not True:
            raise RuntimeError("a pasta %s não está vazia e não é o exemplo fictício; nada foi apagado" % pasta)
        shutil.rmtree(pasta)
    trilha.iniciar(pasta, "exemplo-ficticio", "Automação do fechamento financeiro", ficticio=True,
                   modelo=MODELO, momento=DATAS["definicao"])
    limite = trilha.ETAPAS.index(ate)
    for onda in trilha.dag_mod.ondas(trilha.DAG):
        for ident in onda:
            no = trilha.DAG[ident]
            if trilha.ETAPAS.index(no["etapa"]) > limite:
                continue
            momento = DATAS_NO.get(ident, DATAS[no["etapa"]])
            if ident == "GT":
                trilha.aprovar(pasta, ident, GERENTE, modelo=MODELO, momento=momento, papel="beneficio")
                trilha.aceitar(pasta, "governanca", "Escritório de Projetos", modelo=MODELO, momento=momento)
            elif no["tipo"] == "portao":
                trilha.aprovar(pasta, ident, GERENTE, modelo=MODELO, momento=momento)
            elif ident == trilha.NO_DE_CALCULO:
                trilha.calcular(pasta, modelo=MODELO, momento=momento)
            elif no["tipo"] == "verificacao":
                falhas = trilha.verificar(pasta, ident, modelo=MODELO, momento=momento)
                if falhas:
                    raise RuntimeError("o exemplo não passou em %s: %s" % (ident, falhas))
            else:
                trilha.aplicar(pasta, ident, PROPOSTAS[ident], modelo=MODELO, momento=momento)
    return evidencias.ler(pasta / ARQUIVO_EVIDENCIAS)[-1]["hash"]


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "projetos/exemplo-ficticio"
    print("exemplo gerado em %s\núltimo hash: %s" % (destino, gerar(destino, ate="sustentacao")))
