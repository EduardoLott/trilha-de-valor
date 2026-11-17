"""Compara várias execuções do mesmo caso (protocolo de robustez).

Para cada pasta de projeto, refaz a auditoria e extrai o que deve ser idêntico entre
execuções (contas, checagens, estrutura) e o que pode variar (indicadores propostos,
premissas, ocorrências). Não avalia a redação.

Uso: python3 -m tools.comparar PASTA1 PASTA2 [PASTA3 ...]
"""
import sys
from pathlib import Path

from . import auditar, calculadora, evidencias
from .estado import ARQUIVO_EVIDENCIAS, carregar
from .trilha import dentro_do_repositorio


def resumo(pasta):
    """O que se compara em uma execução."""
    pasta = Path(pasta)
    estado = carregar(pasta)
    relatorio = auditar.auditar(pasta, exigir_ficticio=dentro_do_repositorio(pasta))
    indicadores = {i.get("id"): i for i in estado.get("indicadores", [])}
    medicoes = {m.get("id"): m for m in estado.get("medicoes", [])}
    contas = []
    for r in estado.get("resultados", []):
        i, m = indicadores.get(r.get("indicador"), {}), medicoes.get(r.get("medicao"), {})
        contas.append((str(m.get("data")), str((i.get("linha_de_base") or {}).get("valor")),
                       str((i.get("meta") or {}).get("valor")), str(m.get("valor")),
                       calculadora.texto(r.get("realizacao")), r.get("classificacao")))
    registros = evidencias.ler(pasta / ARQUIVO_EVIDENCIAS)
    return {
        "pasta": pasta.name,
        "auditoria": "aprovada" if relatorio["aprovado"] else "rejeitada",
        "falhas": sorted({f["criterio"] + " " + f["motivo"].split(":")[0] for f in relatorio["falhas"]}),
        "etapa": estado.get("projeto", {}).get("etapa_atual"),
        "documentos": sorted(d.get("tipo") for d in estado.get("documentos", [])),
        "contas": sorted(contas),
        "indicadores": sorted("%s: %s" % (i.get("tipo"), i.get("nome")) for i in indicadores.values()),
        "beneficios": len(estado.get("beneficios", [])),
        "premissas": len(estado.get("premissas", [])),
        "licoes": len(estado.get("licoes", [])),
        "nao_medidos": len(estado.get("nao_medidos", [])),
        "ocorrencias": sum(1 for r in registros if r.get("tipo") == "ocorrencia"),
        "verificacoes_reprovadas": sum(1 for r in registros if r.get("tipo") == "verificacao" and r.get("nivel") == 0),
        "registros": len(registros),
        "modelos": sorted({(r.get("ator") or {}).get("modelo", "?") for r in registros}),
    }


IDENTICOS = (("contas", "Contas (data, linha de base, meta, resultado, realização, classificação)"),
             ("auditoria", "Resultado da auditoria"),
             ("falhas", "Falhas apontadas pela auditoria"),
             ("etapa", "Etapa final"),
             ("documentos", "Documentos aprovados"))
VARIAVEIS = (("indicadores", "Indicadores propostos"), ("beneficios", "Benefícios"), ("premissas", "Premissas"),
             ("licoes", "Lições"), ("nao_medidos", "Indicadores não medidos"), ("ocorrencias", "Ocorrências registradas"),
             ("verificacoes_reprovadas", "Verificações reprovadas no caminho"), ("registros", "Registros de evidência"),
             ("modelos", "Modelo informado"))


def comparar(pastas):
    """Devolve (resumos, iguais): iguais[chave] diz se o aspecto é idêntico em todas as execuções."""
    resumos = [resumo(p) for p in pastas]
    iguais = {chave: all(r[chave] == resumos[0][chave] for r in resumos) for chave, _ in IDENTICOS}
    return resumos, iguais


def _celula(valor):
    if isinstance(valor, list):
        return "<br>".join(" / ".join(v) if isinstance(v, tuple) else str(v) for v in valor) or "nenhum"
    return str(valor)


def relatorio(pastas):
    resumos, iguais = comparar(pastas)
    linhas = ["# Comparação de %d execuções" % len(resumos), "", "## Aspectos que devem ser idênticos", "",
              "| Aspecto | Idêntico? |", "|---|---|"]
    linhas += ["| %s | %s |" % (rotulo, "sim" if iguais[chave] else "**NÃO**") for chave, rotulo in IDENTICOS]
    cabecalho = ["Aspecto"] + [r["pasta"] for r in resumos]
    for titulo, grupo in (("Detalhe dos aspectos que devem ser idênticos", IDENTICOS),
                          ("Aspectos em que a variação é esperada (só registrar)", VARIAVEIS)):
        linhas += ["", "## " + titulo, "", "| " + " | ".join(cabecalho) + " |", "|" + "---|" * len(cabecalho)]
        linhas += ["| %s | %s |" % (rotulo, " | ".join(_celula(r[chave]) for r in resumos)) for chave, rotulo in grupo]
    comuns = set(resumos[0]["indicadores"]).intersection(*(set(r["indicadores"]) for r in resumos[1:]))
    todos = set().union(*(set(r["indicadores"]) for r in resumos))
    linhas += ["", "Indicadores com o mesmo tipo e nome em todas as execuções: %d de %d distintos. "
               "Nomes diferentes podem descrever o mesmo conceito; essa leitura é humana." % (len(comuns), len(todos))]
    return "\n".join(linhas) + "\n", all(iguais.values())


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    try:
        texto, tudo_igual = relatorio(argv)
    except (OSError, ValueError, KeyError) as erro:
        print("erro: %s" % erro)
        return 2
    print(texto)
    return 0 if tudo_igual else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
