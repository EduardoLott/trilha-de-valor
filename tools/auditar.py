"""Auditoria de uma execução da Trilha de Valor.

Refaz, a partir dos arquivos e sem depender do agente, os critérios de aprovação:
  A1 o DAG é válido
  A2 os nós das etapas concluídas atingiram o nível exigido, na ordem do DAG
  A3 cada nó concluído tem evidência registrada
  A4 a cadeia de evidências está íntegra (e coincide com a âncora, se informada)
  A5 o estado em disco é o último estado registrado
  A6 as regras do verificador passam (inclui hash dos documentos e reexecução das contas)
  A7 todo documento aprovado tem aprovação nominal registrada sobre o mesmo hash

Uso: python3 -m tools.auditar projetos/<id> [--ancora <hash>]
"""
import sys
from pathlib import Path

from . import dag as dag_mod
from . import evidencias, verificador
from .estado import ARQUIVO_EVIDENCIAS, carregar, indice_etapa, sha256_objeto


def auditar(pasta, ancora=None, exigir_ficticio=True, dag=None):
    dag = dag or dag_mod.DAG_TRILHA
    falhas, avisos = [], []

    def falha(criterio, motivo):
        falhas.append({"criterio": criterio, "motivo": motivo})

    try:
        estado = carregar(pasta)
    except (OSError, ValueError) as erro:
        falha("A5", "estado ilegível: %s" % erro)
        return {"aprovado": False, "falhas": falhas, "avisos": avisos, "ultimo_hash": None}

    for problema in dag_mod.validar(dag):
        falha("A1", problema)

    etapa = estado.get("projeto", {}).get("etapa_atual")
    registros_no = {n.get("id"): n for n in estado.get("execucao", {}).get("nos", [])}
    if etapa in dag_mod.ETAPAS:
        for ident, no in dag.items():
            if indice_etapa(no["etapa"]) < indice_etapa(etapa) and not dag_mod.concluido(no, registros_no.get(ident)):
                falha("A2", "nó %s (%s) não atingiu o exigido" % (ident, no["nome"]))
    for ident, registro in registros_no.items():
        if ident not in dag:
            falha("A2", "nó desconhecido no estado: %s" % ident)
            continue
        if dag_mod.concluido(dag[ident], registro):
            for dep in dag[ident]["depende_de"]:
                if not dag_mod.concluido(dag[dep], registros_no.get(dep)):
                    falha("A2", "nó %s concluído antes da dependência %s" % (ident, dep))

    caminho = Path(pasta) / ARQUIVO_EVIDENCIAS
    integra, mensagem, ultimo = evidencias.verificar_cadeia(caminho)
    if not integra:
        falha("A4", mensagem)
        registros = []
    else:
        registros = evidencias.ler(caminho)
        if ancora is None:
            avisos.append("cadeia íntegra, mas sem âncora externa para comparar (último hash: %s)" % ultimo)
        elif ancora != ultimo:
            falha("A4", "último hash %s difere da âncora %s" % (ultimo, ancora))

    for ident, registro in registros_no.items():
        if ident not in dag or not dag_mod.concluido(dag[ident], registro):
            continue
        do_no = [r for r in registros if r.get("no") == ident]
        if dag[ident]["tipo"] == "portao":
            ok = any(r.get("tipo") == "aprovacao" and r.get("aprovado_por") for r in do_no)
        else:
            ok = any(int(r.get("nivel", 0)) >= int(registro.get("nivel_alcancado", 0)) for r in do_no)
        if not ok:
            falha("A3", "nó %s sem evidência no nível declarado" % ident)

    if registros:
        com_estado = [r for r in registros if r.get("estado_sha256")]
        if not com_estado:
            falha("A5", "nenhum registro traz o hash do estado")
        elif com_estado[-1]["estado_sha256"] != sha256_objeto(estado):
            falha("A5", "o estado em disco difere do último estado registrado")

    for f in verificador.verificar(estado, pasta=pasta, exigir_ficticio=exigir_ficticio):
        falha("A6", "%s %s: %s" % (f["regra"], f["item"], f["motivo"]))

    for documento in estado.get("documentos", []):
        aprovacoes = [r for r in registros if r.get("tipo") == "aprovacao"
                      and (r.get("saidas") or {}).get("sha256") == documento.get("sha256")
                      and r.get("aprovado_por") == documento.get("aprovado_por")]
        if not aprovacoes:
            falha("A7", "documento %s sem aprovação registrada sobre o hash vigente" % documento.get("id"))

    return {"aprovado": not falhas, "falhas": falhas, "avisos": avisos, "ultimo_hash": ultimo}


def main(argv):
    ancora = None
    if "--ancora" in argv:
        posicao = argv.index("--ancora")
        if posicao + 1 >= len(argv):
            print(__doc__)
            return 2
        ancora = argv[posicao + 1]
        argv = argv[:posicao] + argv[posicao + 2:]
    if len(argv) != 1:
        print(__doc__)
        return 2
    from .trilha import dentro_do_repositorio
    relatorio = auditar(argv[0], ancora=ancora, exigir_ficticio=dentro_do_repositorio(argv[0]))
    for f in relatorio["falhas"]:
        print("FALHA %s  %s" % (f["criterio"], f["motivo"]))
    for aviso in relatorio["avisos"]:
        print("AVISO  %s" % aviso)
    print("auditoria: %s" % ("APROVADA" if relatorio["aprovado"] else "REJEITADA (%d falha(s))" % len(relatorio["falhas"])))
    return 0 if relatorio["aprovado"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
