"""Verificador do estado: completude (C), consistência entre etapas (K) e integridade (I).

Só aponta problemas; não corrige nada.
Uso: python3 -m tools.verificador projetos/<id>
"""
import sys
from pathlib import Path

from . import calculadora
from .estado import ETAPAS, carregar, indice_etapa, sha256_arquivo

METODOS = ("antes_depois", "grupo_controle", "serie_temporal")
TIPOS_INDICADOR = ("execucao", "antecedente", "resultado")
ORIGENS = ("pessoa", "calculadora", "premissa")
PAPEIS = ("projeto", "indicador", "beneficio", "governanca")

# Documento aprovado exigido para estar em cada etapa
EXIGIDO_PARA = {
    "monitoramento": ["proposta_de_valor"],
    "mensuracao": ["proposta_de_valor", "relatorio_monitoramento"],
    "sustentacao": ["proposta_de_valor", "relatorio_monitoramento", "relatorio_beneficios"],
    "encerrado": ["proposta_de_valor", "relatorio_monitoramento", "relatorio_beneficios",
                  "termo_transicao", "licoes_aprendidas"],
}


def _vazio(valor):
    return valor is None or valor == "" or valor == [] or valor == {}


def _ativos(estado):
    return [i for i in estado.get("indicadores", []) if i.get("situacao", "ativo") != "descontinuado"]


def _valor(bloco):
    return (bloco or {}).get("valor")


def _referencia(estado):
    """Retrato dos indicadores na Proposta de Valor aprovada mais recente."""
    propostas = [d for d in estado.get("documentos", []) if d.get("tipo") == "proposta_de_valor"]
    if not propostas:
        return None
    return max(propostas, key=lambda d: d.get("versao", 0)).get("referencia") or {}


def _decisoes_que_afetam(estado, ident, tipos=None):
    return [d for d in estado.get("decisoes", [])
            if ident in d.get("afeta", []) and (tipos is None or d.get("tipo") in tipos)]


def verificar(estado, pasta=None, exigir_ficticio=True, exigir_datas=False, exigir_resultados=False):
    """Devolve a lista de falhas: dicionários com regra, item e motivo.

    exigir_datas: cobra as datas de medição (C7) antes mesmo da etapa de Mensuração.
    exigir_resultados: cobra que toda medição tenha resultado calculado (K4).
    """
    falhas = []

    def falha(regra, item, motivo):
        falhas.append({"regra": regra, "item": item, "motivo": motivo})

    etapa = estado.get("projeto", {}).get("etapa_atual")
    if etapa not in ETAPAS:
        falha("I6", "projeto", "etapa_atual inválida: %r" % etapa)
        return falhas
    indicadores = {i.get("id"): i for i in estado.get("indicadores", [])}
    ativos = _ativos(estado)

    # --- Completude
    papeis = estado.get("papeis", {})
    for papel in PAPEIS:
        if _vazio(papeis.get(papel)):
            falha("C1", "papeis." + papel, "papel não nomeado")

    for beneficio in estado.get("beneficios", []):
        ident = beneficio.get("id", "?")
        for campo in ("responsavel", "prazo", "mudancas_necessarias"):
            if _vazio(beneficio.get(campo)):
                falha("C2", ident, "campo obrigatório ausente: " + campo)
        tipos = [indicadores.get(i, {}).get("tipo") for i in beneficio.get("indicadores", [])]
        if "resultado" not in tipos:
            falha("C2", ident, "benefício sem indicador de resultado")
    if not estado.get("beneficios"):
        falha("C2", "beneficios", "nenhum benefício registrado")

    for indicador in ativos:
        ident = indicador.get("id", "?")
        for campo in ("nome", "tipo", "formula", "unidade", "sentido", "fonte", "periodicidade", "responsavel"):
            if _vazio(indicador.get(campo)):
                falha("C3", ident, "campo obrigatório ausente: " + campo)
        if indicador.get("tipo") not in TIPOS_INDICADOR:
            falha("C3", ident, "tipo inválido: %r" % indicador.get("tipo"))
        if indicador.get("sentido") not in ("menor_melhor", "maior_melhor"):
            falha("C3", ident, "sentido inválido: %r" % indicador.get("sentido"))
        base = indicador.get("linha_de_base") or {}
        if _vazio(base.get("valor")) and _vazio((base.get("plano") or {}).get("data")):
            falha("C4", ident, "sem linha de base: informe valor, data e fonte, ou um plano com 'como' e 'data'")
        meta = indicador.get("meta") or {}
        if _vazio(meta.get("valor")) and _vazio((meta.get("plano") or {}).get("data")):
            falha("C4", ident, "sem meta: informe valor e prazo, ou um plano com 'como' e 'data' para defini-la")
        if exigir_datas and indicador.get("tipo") == "resultado":
            if _vazio(base.get("valor")):
                falha("C4", ident, "a linha de base precisa estar medida antes da Mensuração (o plano não basta)")
            if _vazio(meta.get("valor")):
                falha("C4", ident, "a meta precisa estar definida antes da Mensuração (o plano não basta)")
        if indicador.get("tipo") == "resultado":
            if _vazio(indicador.get("criterio_sucesso")):
                falha("C5", ident, "sem critério de sucesso")
            if indicador.get("metodo_comprovacao") not in METODOS:
                falha("C5", ident, "método de comprovação ausente ou inválido")
            if (exigir_datas or indice_etapa(etapa) >= indice_etapa("mensuracao")) \
                    and _vazio(indicador.get("datas_medicao")):
                falha("C7", ident, "sem datas de medição pós-implementação")

    for linha in estado.get("raci", []):
        if sum(1 for papel in PAPEIS if linha.get(papel) == "A") != 1:
            falha("C6", linha.get("atividade", "?"), "a atividade precisa de exatamente um A")
    if not estado.get("raci"):
        falha("C6", "raci", "matriz RACI vazia")

    # --- Integridade
    for indicador in ativos:
        ident = indicador.get("id", "?")
        base, meta = _valor(indicador.get("linha_de_base")), _valor(indicador.get("meta"))
        if _vazio(base) or _vazio(meta):
            continue
        try:
            b, m = calculadora.fracao(base), calculadora.fracao(meta)
        except calculadora.ErroCalculo as erro:
            falha("I1", ident, str(erro))
            continue
        if b == m:
            falha("I1", ident, "meta igual à linha de base")
        elif (indicador.get("sentido") == "menor_melhor") != (m < b):
            falha("I2", ident, "meta do lado errado da linha de base para o sentido informado")

    premissas = {p.get("id"): p for p in estado.get("premissas", [])}

    def checar_origem(item, bloco):
        origem = (bloco or {}).get("origem")
        if origem not in ORIGENS:
            falha("I3", item, "valor sem origem válida (pessoa, calculadora ou premissa)")
        elif origem == "pessoa" and _vazio(bloco.get("informado_por")):
            falha("I3", item, "valor de pessoa sem informado_por")
        elif origem == "premissa" and bloco.get("premissa") not in premissas:
            falha("I3", item, "valor de premissa sem referência a uma premissa registrada")

    for indicador in ativos:
        ident = indicador.get("id", "?")
        if not _vazio(_valor(indicador.get("linha_de_base"))):
            checar_origem(ident + ".linha_de_base", indicador["linha_de_base"])
        if not _vazio(_valor(indicador.get("meta"))):
            checar_origem(ident + ".meta", indicador["meta"])
    for leitura in estado.get("monitoramento", {}).get("leituras", []):
        checar_origem("leitura %s %s" % (leitura.get("indicador"), leitura.get("data")), leitura)
    for medicao in estado.get("medicoes", []):
        if medicao.get("origem") != "pessoa":
            falha("I3", medicao.get("id", "?"), "medição precisa ser informada por pessoa")
        else:
            checar_origem(medicao.get("id", "?"), medicao)

    for premissa in estado.get("premissas", []):
        if premissa.get("bloqueante") and premissa.get("situacao") == "aberta":
            falha("I4", premissa.get("id", "?"), "premissa bloqueante em aberto")

    documentos = estado.get("documentos", [])
    if pasta is not None:
        for documento in documentos:
            arquivo = Path(pasta) / documento.get("arquivo", "")
            if not arquivo.is_file():
                falha("I5", documento.get("id", "?"), "arquivo não encontrado: %s" % documento.get("arquivo"))
            elif sha256_arquivo(arquivo) != documento.get("sha256"):
                falha("I5", documento.get("id", "?"), "hash do arquivo difere do aprovado")

    aprovados = {d.get("tipo") for d in documentos if not _vazio(d.get("aprovado_por"))}
    for tipo in EXIGIDO_PARA.get(etapa, []):
        if tipo not in aprovados:
            falha("I6", "projeto.etapa_atual", "etapa %s exige %s aprovado" % (etapa, tipo))

    objetivos = {o.get("id") for o in estado.get("objetivos", [])}
    medicoes = {m.get("id"): m for m in estado.get("medicoes", [])}
    for beneficio in estado.get("beneficios", []):
        if beneficio.get("objetivo") not in objetivos:
            falha("I7", beneficio.get("id", "?"), "objetivo inexistente: %r" % beneficio.get("objetivo"))
        for ref in beneficio.get("indicadores", []):
            if ref not in indicadores:
                falha("I7", beneficio.get("id", "?"), "indicador inexistente: %r" % ref)
    for medicao in estado.get("medicoes", []):
        if medicao.get("indicador") not in indicadores:
            falha("I7", medicao.get("id", "?"), "indicador inexistente: %r" % medicao.get("indicador"))
    for resultado in estado.get("resultados", []):
        if resultado.get("indicador") not in indicadores or resultado.get("medicao") not in medicoes:
            falha("I7", "resultado %s" % resultado.get("indicador"), "referência inexistente")

    if exigir_ficticio and estado.get("projeto", {}).get("ficticio") is not True:
        falha("I8", "projeto.ficticio", "projeto no repositório precisa ser fictício")

    # --- Consistência entre etapas
    referencia = _referencia(estado)
    if referencia is not None:
        for medicao in estado.get("medicoes", []):
            ident = medicao.get("indicador")
            if ident in indicadores and ident not in referencia and not _decisoes_que_afetam(estado, ident):
                falha("K1", medicao.get("id", "?"), "indicador %s não está na Proposta nem em decisão" % ident)
        for ident, indicador in indicadores.items():
            antes = referencia.get(ident)
            if antes is None:
                if not _decisoes_que_afetam(estado, ident):
                    falha("K2", ident, "indicador criado depois da Proposta, sem decisão registrada")
                continue
            for campo, tipo in (("linha_de_base", "revisao_linha_de_base"), ("meta", "revisao_meta")):
                if _valor(indicador.get(campo)) != antes.get(campo):
                    if not _decisoes_que_afetam(estado, ident, (tipo, "revisao_indicador", "mudanca_escopo")):
                        falha("K2", ident, "%s mudou de %r para %r sem decisão registrada"
                              % (campo, antes.get(campo), _valor(indicador.get(campo))))
            if indicador.get("situacao") == "descontinuado" and not _decisoes_que_afetam(estado, ident):
                falha("K2", ident, "indicador descontinuado sem decisão registrada")
        for ident in referencia:
            if ident not in indicadores:
                falha("K2", ident, "indicador da Proposta removido do estado")

    atribuidos = {a.get("indicador") for a in estado.get("atribuicao", [])}
    faixas = estado.get("classificacao", {})
    for resultado in estado.get("resultados", []):
        ident = resultado.get("indicador")
        indicador, medicao = indicadores.get(ident), medicoes.get(resultado.get("medicao"))
        if not indicador or not medicao:
            continue
        if indicador.get("metodo_comprovacao") not in METODOS or ident not in atribuidos:
            falha("K3", ident, "resultado sem método de comprovação ou sem registro de atribuição")
        if medicao.get("indicador") != ident:
            falha("K4", ident, "a medição %s é de outro indicador" % medicao.get("id"))
            continue
        try:
            r = calculadora.realizacao(_valor(indicador.get("linha_de_base")), _valor(indicador.get("meta")),
                                       medicao.get("valor"))
            classe = calculadora.classificar(r, faixas.get("realizado_a_partir_de", "1"),
                                             faixas.get("parcial_a_partir_de", "1/2"))
            gravado = calculadora.fracao(resultado.get("realizacao"))
        except calculadora.ErroCalculo as erro:
            falha("K4", ident, "não foi possível refazer o cálculo: %s" % erro)
            continue
        if gravado != r:
            falha("K4", ident, "realização gravada %s difere da recalculada %s"
                  % (resultado.get("realizacao"), calculadora.texto(r)))
        if resultado.get("classificacao") != classe:
            falha("K4", ident, "classificação gravada %r difere da recalculada %r"
                  % (resultado.get("classificacao"), classe))

    if exigir_resultados:
        calculadas = {r.get("medicao") for r in estado.get("resultados", [])}
        for ident in medicoes:
            if ident not in calculadas:
                falha("K4", ident, "medição sem resultado calculado")
        medidos = {m.get("indicador") for m in estado.get("medicoes", [])}
        justificados = {n.get("indicador") for n in estado.get("nao_medidos", []) if not _vazio(n.get("motivo"))}
        cobertas = {(m.get("indicador"), m.get("data")) for m in estado.get("medicoes", [])}
        cobertas |= {(n.get("indicador"), n.get("data")) for n in estado.get("nao_medidos", [])
                     if not _vazio(n.get("motivo"))}
        for indicador in ativos:
            if indicador.get("tipo") != "resultado":
                continue
            ident = indicador.get("id", "?")
            if ident not in medidos | justificados:
                falha("B2", ident, "indicador de resultado sem medição e sem registro em nao_medidos com o motivo")
            for data in indicador.get("datas_medicao") or []:
                if (ident, data) not in cobertas:
                    falha("B2", ident, "medição prevista para %s não foi realizada nem justificada em nao_medidos" % data)

    return falhas


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    falhas = verificar(carregar(argv[0]), pasta=argv[0])
    for f in falhas:
        print("%-3s %-28s %s" % (f["regra"], f["item"], f["motivo"]))
    print("verificador: %s" % ("sem falhas" if not falhas else "%d falha(s)" % len(falhas)))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
