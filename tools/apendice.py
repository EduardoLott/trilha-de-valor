"""Gera, a partir do código do assistente, as tabelas do apêndice do guia.

O apêndice do guia não é digitado: as seções de cada documento vêm das funções que
geram os documentos (tools/entregaveis.py), para que o guia e o assistente não divirjam.

Uso: python3 -m tools.apendice
"""
import inspect
import re
import sys
import tempfile
from pathlib import Path

from . import calculadora, entregaveis, exemplo

# Rótulo, tipo de documento e momento de emissão (o conteúdo vem do código)
DOCUMENTOS = (
    ("Proposta de Valor do Projeto", "proposta_de_valor", "Definição de Valor, antes da aprovação do projeto"),
    ("Relatório de Monitoramento de Valor", "relatorio_monitoramento",
     "Monitoramento de Valor, antes do encerramento da execução"),
    ("Termo de Transição para a Operação", "termo_transicao",
     "Sustentação, antes de a equipe ser desfeita; aceite do responsável pelo benefício e da governança"),
    ("Relatório de Benefícios", "relatorio_beneficios",
     "Mensuração dos Benefícios, depois da última medição prevista"),
    ("Registro de Lições Aprendidas", "licoes_aprendidas", "Sustentação, depois da última medição prevista"),
)
MEDICOES_DO_EXEMPLO = ("8", "8", "7")


def _titulos_do_exemplo():
    """Seções que aparecem nos documentos do exemplo fictício, por tipo."""
    nomes = {"proposta_de_valor": "proposta", "relatorio_monitoramento": "monitoramento",
             "termo_transicao": "transicao", "relatorio_beneficios": "beneficios", "licoes_aprendidas": "licoes"}
    saida = {}
    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp) / "exemplo"
        exemplo.gerar(pasta, ate="sustentacao")
        for tipo, trecho in nomes.items():
            arquivo = next(pasta.glob("*/*%s*" % trecho))
            saida[tipo] = {l[3:].strip() for l in arquivo.read_text(encoding="utf-8").splitlines() if l.startswith("## ")}
    return saida


_EXEMPLO = None


def secoes(tipo):
    """Seções do documento, na ordem do código; as que o exemplo não emite levam '(quando houver)'."""
    global _EXEMPLO
    if _EXEMPLO is None:
        _EXEMPLO = _titulos_do_exemplo()
    fonte = inspect.getsource(entregaveis.GERADORES[tipo])
    achados = [(m.start(), m.group(1)) for m in re.finditer(r'"## ([^"]+)"', fonte)]
    for chamada, titulo in (("_anotacoes(", "Observações"), ("_premissas(", "Premissas")):
        posicao = fonte.find(chamada)
        if posicao >= 0:
            achados.append((posicao, titulo))
    titulos = []
    for _, titulo in sorted(achados):
        if titulo not in [t.replace(" (quando houver)", "") for t in titulos]:
            titulos.append(titulo if titulo in _EXEMPLO[tipo] else titulo + " (quando houver)")
    return titulos


def tabela_documentos():
    linhas = ["| Documento | Etapa e momento | Seções |", "|---|---|---|"]
    for rotulo, tipo, momento in DOCUMENTOS:
        extra = ""
        if tipo == "termo_transicao":  # campos listados antes das seções, lidos do código
            campos = re.findall(r'\("([^"]+)", "[a-z_]+"\)', inspect.getsource(entregaveis.termo_transicao))
            extra = "Campos: " + ", ".join(c.lower() for c in campos) + ". Seções: "
        linhas.append("| %s | %s | %s%s |" % (rotulo, momento, extra, "; ".join(secoes(tipo))))
    return "\n".join(linhas)


def tabela_exemplo(base="10", meta="7"):
    linhas = ["| Medição | Linha de base | Meta | Resultado | Realização | Classificação |", "|---|---|---|---|---|---|"]
    for numero, valor in enumerate(MEDICOES_DO_EXEMPLO, 1):
        r = calculadora.realizacao(base, meta, valor)
        classe = {"realizado": "realizado", "parcial": "parcial", "nao_realizado": "não realizado"}[calculadora.classificar(r)]
        linhas.append("| %d | %s | %s | %s | %s | %s |" % (numero, base, meta, valor, calculadora.percentual(r), classe))
    return "\n".join(linhas)


if __name__ == "__main__":
    print(tabela_documentos())
    print()
    print(tabela_exemplo())
    sys.exit(0)
