"""DAG das operações da Trilha de Valor.

Tipos de nó:
  execucao     operação conduzida pelo agente com a pessoa
  verificacao  checagem determinística (verificador, calculadora)
  portao       aprovação nominal de uma pessoa

Um nó está concluído quando atinge o nível de garantia exigido; um portão, quando
está aprovado. Só nós concluídos liberam os dependentes.

Uso: python3 -m tools.dag
"""
from graphlib import CycleError, TopologicalSorter

from .estado import ETAPAS

TIPOS = ("execucao", "verificacao", "portao")
TRANSVERSAL = "sustentacao"


def _no(etapa, tipo, nome, depende_de=(), nivel=1):
    return {"etapa": etapa, "tipo": tipo, "nome": nome, "depende_de": tuple(depende_de), "nivel_exigido": nivel}


DAG_TRILHA = {
    # Definição de valor
    "D1": _no("definicao", "execucao", "Compreender o problema e alinhá-lo à estratégia"),
    "D2": _no("definicao", "execucao", "Identificar os benefícios esperados", ["D1"]),
    "D3": _no("definicao", "execucao", "Definir os indicadores de valor", ["D2"]),
    "D4": _no("definicao", "execucao", "Linha de base, metas e método de comprovação", ["D3"]),
    "D5": _no("definicao", "execucao", "Fontes, responsáveis e condições", ["D2"]),
    "V1": _no("definicao", "verificacao", "Completude e integridade da Proposta de Valor", ["D4", "D5"], 2),
    "G1": _no("definicao", "portao", "Aprovação da Proposta de Valor do Projeto", ["V1"]),
    # Monitoramento de valor
    "M1": _no("monitoramento", "execucao", "Estruturar a rotina e a cadência", ["G1"]),
    "M2": _no("monitoramento", "execucao", "Acompanhar a evolução dos indicadores", ["M1"]),
    "M3": _no("monitoramento", "execucao", "Monitorar a adoção e as condições", ["M1"]),
    "M4": _no("monitoramento", "execucao", "Tratar desvios, riscos e mudanças de escopo", ["M2", "M3"]),
    "M5": _no("monitoramento", "execucao", "Consolidar os resultados e preparar a transição", ["M4"]),
    "V2": _no("monitoramento", "verificacao", "Toda mudança tem decisão; datas de medição definidas", ["M5"], 2),
    "G2": _no("monitoramento", "portao", "Aprovação do Relatório de Monitoramento de Valor", ["V2"]),
    # Mensuração dos benefícios
    "B1": _no("mensuracao", "execucao", "Confirmar as condições para a mensuração", ["G2"]),
    "B2": _no("mensuracao", "execucao", "Planejar e executar as medições", ["B1"]),
    "B3": _no("mensuracao", "execucao", "Verificar a atribuição do resultado", ["B2"]),
    "B4": _no("mensuracao", "verificacao", "Calcular a realização e classificar (calculadora)", ["B2"], 2),
    "B5": _no("mensuracao", "execucao", "Decidir e comunicar", ["B3", "B4"]),
    "V3": _no("mensuracao", "verificacao", "Reexecução do cálculo e consistência pré x pós", ["B5"], 2),
    "G3": _no("mensuracao", "portao", "Aprovação do Relatório de Benefícios", ["V3"]),
    # Governança e melhoria contínua (Sustentação)
    # Transversal: estes nós ficam liberados assim que as dependências são concluídas, em qualquer etapa.
    # A transição (S2, VT, GT) acontece antes de a equipe do projeto sair, logo depois do Monitoramento.
    "S1": _no("sustentacao", "execucao", "Manter os papéis e a matriz RACI", ["G1"]),
    "S2": _no("sustentacao", "execucao", "Formalizar a transição para a operação", ["G2"]),
    "VT": _no("sustentacao", "verificacao", "Termo de Transição completo", ["S2"], 2),
    "GT": _no("sustentacao", "portao", "Aceite do Termo de Transição", ["VT"]),
    "S3": _no("sustentacao", "execucao", "Registrar as lições aprendidas", ["G3"]),
    "S4": _no("sustentacao", "execucao", "Atualizar o catálogo de indicadores", ["S3"]),
    "V4": _no("sustentacao", "verificacao", "Papéis, transição, lições e catálogo registrados", ["S1", "GT", "S4"], 2),
    "G4": _no("sustentacao", "portao", "Aprovação do Registro de Lições Aprendidas", ["V4"]),
}


def grafo(dag):
    return {ident: set(no["depende_de"]) for ident, no in dag.items()}


def validar(dag):
    """Devolve a lista de problemas do grafo (vazia se válido)."""
    problemas = []
    for ident, no in dag.items():
        if no["tipo"] not in TIPOS:
            problemas.append("%s: tipo inválido %r" % (ident, no["tipo"]))
        if no["etapa"] not in ETAPAS:
            problemas.append("%s: etapa inválida %r" % (ident, no["etapa"]))
        for dep in no["depende_de"]:
            if dep not in dag:
                problemas.append("%s: depende de nó inexistente %s" % (ident, dep))
            elif ETAPAS.index(dag[dep]["etapa"]) > ETAPAS.index(no["etapa"]):
                problemas.append("%s: depende de %s, que é de etapa posterior" % (ident, dep))
        if no["tipo"] == "portao":
            if not no["depende_de"] or any(dag.get(d, {}).get("tipo") != "verificacao" for d in no["depende_de"]):
                problemas.append("%s: portão precisa depender apenas de verificações" % ident)
    if problemas:
        return problemas
    try:
        list(TopologicalSorter(grafo(dag)).static_order())
    except CycleError as erro:
        return ["ciclo: %s" % " -> ".join(erro.args[1])]
    com_dependentes = {dep for no in dag.values() for dep in no["depende_de"]}
    finais = sorted(set(dag) - com_dependentes)
    if len(finais) != 1:
        problemas.append("esperado um único nó final, encontrados: %s" % ", ".join(finais))
    return problemas


def ondas(dag):
    """Grupos de nós que podem rodar em paralelo, em ordem."""
    ordenador = TopologicalSorter(grafo(dag))
    ordenador.prepare()
    resultado = []
    while ordenador.is_active():
        prontos = sorted(ordenador.get_ready())
        resultado.append(prontos)
        ordenador.done(*prontos)
    return resultado


def concluido(no, registro):
    """registro: item de estado['execucao']['nos'] ou None."""
    if not registro:
        return False
    if no["tipo"] == "portao":
        return registro.get("estado") == "aprovado"
    if registro.get("estado") not in ("executado", "verificado"):
        return False
    return int(registro.get("nivel_alcancado", 0)) >= no["nivel_exigido"]


def liberados(dag, registros):
    """Nós ainda não concluídos cujas dependências estão todas concluídas."""
    feito = {i for i, no in dag.items() if concluido(no, registros.get(i))}
    return sorted(i for i, no in dag.items() if i not in feito and all(d in feito for d in no["depende_de"]))


if __name__ == "__main__":
    erros = validar(DAG_TRILHA)
    print("DAG válido" if not erros else "\n".join(erros))
    for numero, onda in enumerate(ondas(DAG_TRILHA), 1):
        print("%2d: %s" % (numero, ", ".join(onda)))
