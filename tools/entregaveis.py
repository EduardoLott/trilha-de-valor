"""Gera os entregáveis da Trilha de Valor a partir do estado.

Os documentos são sempre derivados do estado: ninguém digita número em relatório.
Modelos provisórios, a alinhar com o kit de ferramentas.
"""
from . import calculadora

ROTULO_CLASSE = {"realizado": "realizado", "parcial": "parcial", "nao_realizado": "não realizado",
                 "nao_medido": "não medido"}
ROTULO_METODO = {"antes_depois": "antes e depois", "grupo_controle": "grupo de controle ou piloto",
                 "serie_temporal": "série temporal"}
ROTULO_TIPO = {"execucao": "execução", "antecedente": "antecedente", "resultado": "resultado"}


def _t(valor, vazio="não informado"):
    if valor is None or valor == "" or valor == []:
        return vazio
    if isinstance(valor, list):
        return "; ".join(str(v).rstrip(".;") for v in valor)
    return str(valor).replace("|", "/").replace("\n", " ")


def _autoria(item):
    """Marca, no documento, o texto que o assistente redigiu."""
    if item.get("redacao") == "assistente":
        return " *(redação do assistente, confirmada por %s)*" % _t(item.get("confirmado_por"))
    return ""


def _autoria_da_lista(itens, rotulo="itens"):
    """Linha que identifica, abaixo de uma tabela, o que o assistente redigiu."""
    do_assistente = [i for i in itens or [] if i.get("redacao") == "assistente"]
    if not do_assistente:
        return []
    return ["", "*Redação do assistente, confirmada pela pessoa indicada: %s.*" % "; ".join(
        "%s (%s)" % (i.get("id") or i.get("indicador"), _t(i.get("confirmado_por"))) for i in do_assistente)]


RODAPE = ["", "---", "", "*Como ler este documento: os números vêm de quem está indicado como origem e da calculadora. "
          "A estrutura e a redação de problema, objetivos, benefícios e indicadores foram propostas pelo assistente e "
          "confirmadas pela pessoa antes de cada registro. Nos demais textos, o que o assistente redigiu está "
          "identificado; o que não está identificado são palavras da pessoa.*"]


def _tabela(cabecalho, linhas):
    saida = ["| " + " | ".join(cabecalho) + " |", "|" + "---|" * len(cabecalho)]
    saida += ["| " + " | ".join(_t(c) for c in linha) + " |" for linha in linhas]
    return saida


def _origem(bloco):
    bloco = bloco or {}
    if bloco.get("origem") == "pessoa":
        return "informado por " + _t(bloco.get("informado_por"))
    if bloco.get("origem") == "premissa":
        return "premissa " + _t(bloco.get("premissa"))
    return _t(bloco.get("origem"))


def _cabecalho(estado, titulo):
    projeto = estado.get("projeto", {})
    linhas = ["# %s" % titulo, "", "**Projeto:** %s" % _t(projeto.get("nome"))]
    if projeto.get("ficticio"):
        linhas += ["", "*Exemplo fictício: todos os dados são inventados.*"]
    return linhas + [""]


def _premissas(estado):
    linhas = ["## Premissas", ""]
    visiveis = [p for p in estado.get("premissas", []) if p.get("situacao") in ("aberta", "contrariada")]
    if not visiveis:
        return linhas + ["Nenhuma em aberto ou contrariada.", ""]
    for p in visiveis:
        marca = "CONTRARIADA" if p.get("situacao") == "contrariada" else "em aberto"
        marca += ", presumida pelo assistente" if p.get("criada_por") == "agente" else ", enunciada pela pessoa"
        linhas.append("- %s (%s%s): %s" % (p.get("id"), marca, ", bloqueante" if p.get("bloqueante") else "",
                                           _t(p.get("texto"))))
    return linhas + [""]


def _fracao_e_percentual(valor):
    return "%s (%s)" % (calculadora.texto(valor), calculadora.percentual(valor))


def _meta(indicador):
    meta = indicador.get("meta") or {}
    if meta.get("valor") not in (None, ""):
        return "%s %s até %s (%s)" % (meta["valor"], _t(indicador.get("unidade"), ""), _t(meta.get("prazo")), _origem(meta))
    plano = meta.get("plano") or {}
    if plano.get("data"):
        return "a definir até %s: %s" % (_t(plano.get("data")), _t(plano.get("como")))
    return "meta pendente"


def _faixas(estado):
    faixas = estado.get("classificacao", {})
    return "Classificação: realizado a partir de %s da meta; parcial a partir de %s." % (
        calculadora.percentual(faixas.get("realizado_a_partir_de", "1")),
        calculadora.percentual(faixas.get("parcial_a_partir_de", "1/2")))


def _base(indicador):
    base = indicador.get("linha_de_base") or {}
    if base.get("valor") not in (None, ""):
        return "%s %s em %s (fonte: %s; %s)" % (base["valor"], _t(indicador.get("unidade"), ""), _t(base.get("data")),
                                                 _t(base.get("fonte")), _origem(base))
    plano = base.get("plano") or {}
    return "a obter até %s: %s" % (_t(plano.get("data")), _t(plano.get("como")))


def proposta_de_valor(estado):
    projeto = estado.get("projeto", {})
    linhas = _cabecalho(estado, "Proposta de Valor do Projeto")
    linhas += ["## Problema e alinhamento estratégico", "", _t(projeto.get("problema")), "",
               "**Solução proposta:** " + _t(projeto.get("descricao")), ""]
    for objetivo in estado.get("objetivos", []):
        linhas.append("- Objetivo %s: %s" % (objetivo.get("id"), _t(objetivo.get("descricao"))))
    linhas += ["", "## Benefícios esperados", ""]
    for b in estado.get("beneficios", []):
        linhas += ["### %s. %s" % (b.get("id"), _t(b.get("descricao"))), "",
                   "- Objetivo: %s" % _t(b.get("objetivo")),
                   "- Responsável pelo benefício: %s" % _t(b.get("responsavel")),
                   "- Mudanças necessárias: %s" % _t(b.get("mudancas_necessarias")),
                   "- Condições e dependências: %s" % _t(b.get("condicoes"), "nenhuma registrada"),
                   "- Prazo esperado: %s" % _t(b.get("prazo")),
                   "- Indicadores: %s" % _t(b.get("indicadores")), ""]
    ativos = [i for i in estado.get("indicadores", []) if i.get("situacao", "ativo") != "descontinuado"]
    linhas += ["## Indicadores", ""]
    linhas += _tabela(["Id", "Indicador", "Tipo", "Fórmula", "Unidade", "Fonte", "Periodicidade", "Responsável"],
                      [[i.get("id"), i.get("nome"), ROTULO_TIPO.get(i.get("tipo"), i.get("tipo")), i.get("formula"),
                        i.get("unidade"), i.get("fonte"), i.get("periodicidade"), i.get("responsavel")] for i in ativos])
    linhas += ["", "## Linha de base, metas e comprovação", ""]
    linhas += _tabela(["Id", "Linha de base", "Meta", "Critério de sucesso", "Método de comprovação"],
                      [[i.get("id"), _base(i),
                        _meta(i),
                        _t(i.get("criterio_sucesso"), "não se aplica"),
                        ROTULO_METODO.get(i.get("metodo_comprovacao"), "não se aplica")] for i in ativos])
    linhas += ["", _faixas(estado), ""]
    papeis = estado.get("papeis", {})
    linhas += ["## Papéis", ""]
    linhas += _tabela(["Papel", "Quem"], [["Responsável pelo projeto", papeis.get("projeto")],
                                          ["Responsável pelo indicador", papeis.get("indicador")],
                                          ["Responsável pelo benefício", papeis.get("beneficio")],
                                          ["Responsável pela governança", papeis.get("governanca")]])
    linhas += ["", "## Matriz RACI", ""]
    linhas += _tabela(["Atividade", "Proj.", "Ind.", "Ben.", "Gov."],
                      [[r.get("atividade"), r.get("projeto"), r.get("indicador"), r.get("beneficio"), r.get("governanca")]
                       for r in estado.get("raci", [])])
    linhas += [""] + _anotacoes(estado, "definicao") + _premissas(estado)
    return "\n".join(linhas).rstrip() + "\n"


def relatorio_monitoramento(estado):
    linhas = _cabecalho(estado, "Relatório de Monitoramento de Valor")
    cadencia = estado.get("monitoramento", {}).get("cadencia", {})
    linhas += ["## Cadência", "", "Operacional: %s. Revisão de valor: %s. Executiva: %s." % (
        _t(cadencia.get("operacional")), _t(cadencia.get("revisao_valor")), _t(cadencia.get("executiva"))), "",
        "## Leituras dos indicadores", ""]
    leituras = estado.get("monitoramento", {}).get("leituras", [])
    if leituras:
        referencia = {i.get("id"): i for i in estado.get("indicadores", [])}
        linhas += _tabela(["Indicador", "Data", "Valor", "Linha de base", "Meta", "Origem", "Comentário"],
                          [[l.get("indicador"), l.get("data"), l.get("valor"),
                            _t((referencia.get(l.get("indicador"), {}).get("linha_de_base") or {}).get("valor"), "a obter"),
                            _t((referencia.get(l.get("indicador"), {}).get("meta") or {}).get("valor"), "a definir"),
                            _origem(l), _t(l.get("comentario"), "")] for l in leituras])
    else:
        linhas.append("Nenhuma leitura registrada.")
    linhas += ["", "## Riscos e oportunidades de valor", ""]
    riscos = estado.get("riscos", [])
    if riscos:
        linhas += _tabela(["Id", "Tipo", "Descrição", "Impacto no valor", "Ação", "Responsável", "Prazo"],
                          [[r.get("id"), r.get("tipo"), r.get("descricao"), r.get("impacto_no_valor"), r.get("acao"),
                            r.get("responsavel"), r.get("prazo")] for r in riscos])
    else:
        linhas.append("Nenhum registrado.")
    linhas += _autoria_da_lista(riscos)
    linhas += ["", "## Decisões e mudanças de escopo", ""]
    decisoes = estado.get("decisoes", [])
    if decisoes:
        linhas += _tabela(["Id", "Data", "Tipo", "Descrição", "Afeta", "Justificativa", "Decidido por"],
                          [[d.get("id"), d.get("data"), d.get("tipo"), d.get("descricao"),
                            _t(d.get("afeta"), "nenhum indicador"), d.get("justificativa"), d.get("decidido_por")]
                           for d in decisoes])
    else:
        linhas.append("Nenhuma decisão registrada.")
    linhas += _autoria_da_lista(decisoes)
    linhas += ["", "## Plano de Mensuração Pós-implementação", ""]
    linhas += _tabela(["Indicador", "Responsável", "Método de comprovação", "Datas de medição"],
                      [[i.get("id"), i.get("responsavel"), ROTULO_METODO.get(i.get("metodo_comprovacao")),
                        i.get("datas_medicao")] for i in estado.get("indicadores", []) if i.get("tipo") == "resultado"])
    linhas += [""] + _anotacoes(estado, "monitoramento") + _premissas(estado)
    return "\n".join(linhas).rstrip() + "\n"


def _anotacoes(estado, prefixo_no):
    inicial = {"definicao": "D", "monitoramento": "M", "mensuracao": "B", "sustentacao": "S"}[prefixo_no]
    notas = [a for a in estado.get("anotacoes", []) if str(a.get("no", "")).startswith(inicial)]
    if not notas:
        return []
    return ["## Observações", ""] + ["- %s%s" % (_t(a.get("texto")), _autoria(a)) for a in notas] + [""]


def relatorio_beneficios(estado):
    indicadores = {i.get("id"): i for i in estado.get("indicadores", [])}
    medicoes = {m.get("id"): m for m in estado.get("medicoes", [])}
    linhas = _cabecalho(estado, "Relatório de Benefícios")
    linhas += ["## Quadro comparativo", ""]
    quadro = []
    for r in estado.get("resultados", []):
        i, m = indicadores.get(r.get("indicador"), {}), medicoes.get(r.get("medicao"), {})
        quadro.append([i.get("nome"), (i.get("linha_de_base") or {}).get("valor"), (i.get("meta") or {}).get("valor"),
                       "%s em %s" % (_t(m.get("valor")), _t(m.get("data"))), _fracao_e_percentual(r["realizacao"]),
                       ROTULO_CLASSE.get(r.get("classificacao"), r.get("classificacao"))])
    medidos = {r.get("indicador") for r in estado.get("resultados", [])}
    for i in indicadores.values():
        if i.get("tipo") == "resultado" and i.get("id") not in medidos:
            quadro.append([i.get("nome"), (i.get("linha_de_base") or {}).get("valor"), (i.get("meta") or {}).get("valor"),
                           "sem medição", "", ROTULO_CLASSE["nao_medido"]])
    linhas += _tabela(["Indicador", "Linha de base", "Meta", "Resultado", "Realização", "Classificação"], quadro)
    linhas += ["", "Realização = (resultado − linha de base) ÷ (meta − linha de base), calculada por %s." % calculadora.NOME,
               "", _faixas(estado), ""]
    nao_medidos = estado.get("nao_medidos", [])
    if nao_medidos:
        linhas += ["## Indicadores não medidos", ""]
        linhas += _tabela(["Indicador", "Data de referência", "Motivo", "Como e quando será obtido"],
                          [[n.get("indicador"), n.get("data"), n.get("motivo"),
                            _t(n.get("plano"), "não definido") + (" (até %s)" % n["prazo"] if n.get("prazo") else "")]
                           for n in nao_medidos])
        linhas += _autoria_da_lista(nao_medidos) + [""]
    linhas += ["## Origem das medições", ""]
    linhas += _tabela(["Medição", "Indicador", "Data", "Fonte", "Origem"],
                      [[m.get("id"), m.get("indicador"), m.get("data"), m.get("fonte"), _origem(m)]
                       for m in estado.get("medicoes", [])])
    linhas += ["", "## Atribuição e limitações", ""]
    for a in estado.get("atribuicao", []):
        i = indicadores.get(a.get("indicador"), {})
        linhas += ["- %s (método: %s). Fatores concorrentes: %s. Conclusão: %s. Limitações: %s" % (
            a.get("indicador"), ROTULO_METODO.get(i.get("metodo_comprovacao"), "não informado"),
            _t(a.get("fatores_concorrentes"), "nenhum identificado"), _t(a.get("conclusao")), _t(a.get("limitacoes")))
            + _autoria(a)]
    linhas += ["", "## Decisões e ações", ""]
    encaminhamentos = estado.get("encaminhamentos", [])
    if encaminhamentos:
        linhas += _tabela(["Indicador", "Decisão", "Ação", "Responsável", "Prazo"],
                          [[e.get("indicador"), e.get("decisao"), e.get("acao"), e.get("responsavel"), e.get("prazo")]
                           for e in encaminhamentos])
        linhas += _autoria_da_lista(encaminhamentos)
    else:
        linhas.append("Nenhuma decisão registrada.")
    linhas += [""] + _anotacoes(estado, "mensuracao") + _premissas(estado)
    return "\n".join(linhas).rstrip() + "\n"


def termo_transicao(estado):
    transicao = estado.get("transicao", {})
    papeis = estado.get("papeis", {})
    linhas = _cabecalho(estado, "Termo de Transição para a Operação")
    for rotulo, chave in (("Data da transição", "data"), ("Quem assume o acompanhamento", "recebido_por"),
                          ("O que foi entregue", "itens"), ("Acesso às fontes de dados", "acessos"),
                          ("Disponível até a primeira medição", "apoio_ate_primeira_medicao"),
                          ("Pendências e riscos atribuídos", "pendencias")):
        linhas.append("- %s: %s" % (rotulo, _t(transicao.get(chave), "nenhum registro")))
    if transicao.get("redacao") == "assistente":
        linhas += ["", "*Texto da transição redigido pelo assistente e confirmado por %s.*" % _t(transicao.get("confirmado_por"))]
    linhas += ["", "## Responsáveis depois do projeto", ""]
    linhas += _tabela(["Papel", "Quem"], [["Responsável pelo indicador", papeis.get("indicador")],
                                          ["Responsável pelo benefício", papeis.get("beneficio")],
                                          ["Responsável pela governança", papeis.get("governanca")]])
    linhas += ["", "## Calendário de medição", ""]
    linhas += _tabela(["Indicador", "Datas de medição"],
                      [[i.get("id"), i.get("datas_medicao")] for i in estado.get("indicadores", [])
                       if i.get("tipo") == "resultado"])
    notas = [a for a in estado.get("anotacoes", []) if a.get("no") in ("S2", "VT", "GT")]
    if notas:
        linhas += ["", "## Observações", ""] + ["- %s%s" % (_t(a.get("texto")), _autoria(a)) for a in notas]
    linhas += [""] + _premissas(estado)
    return "\n".join(linhas).rstrip() + "\n"


def licoes_aprendidas(estado):
    linhas = _cabecalho(estado, "Registro de Lições Aprendidas")
    linhas += ["## Lições e ações", ""]
    linhas += _tabela(["Id", "Etapa", "Lição", "Ação", "Responsável", "Prazo"],
                      [[l.get("id"), l.get("etapa"), l.get("licao"), l.get("acao"), l.get("responsavel"), l.get("prazo")]
                       for l in estado.get("licoes", [])])
    linhas += _autoria_da_lista(estado.get("licoes"))
    indicadores = {i.get("id"): i for i in estado.get("indicadores", [])}
    ultimo = {}
    for r in estado.get("resultados", []):
        ultimo[r.get("indicador")] = r
    medicoes = {m.get("id"): m for m in estado.get("medicoes", [])}
    linhas += ["", "## Catálogo de indicadores (base de referência)", ""]
    catalogo = []
    for c in estado.get("catalogo", []):
        i, r = indicadores.get(c.get("indicador"), {}), ultimo.get(c.get("indicador"))
        catalogo.append([i.get("nome"), i.get("formula"), i.get("fonte"),
                         _t((i.get("linha_de_base") or {}).get("valor"), "não obtida"),
                         _t((i.get("meta") or {}).get("valor"), "não definida"),
                         _t(medicoes.get(r.get("medicao"), {}).get("valor")) if r else "não medido",
                         {"media": "média"}.get(c.get("dificuldade"), c.get("dificuldade")), {"sim": "sim", "em_parte": "em parte", "nao": "não"}.get(
                             c.get("util_para_decidir"), c.get("util_para_decidir")), c.get("observacao")])
    linhas += _tabela(["Indicador", "Fórmula aplicada", "Fonte", "Linha de base", "Meta", "Resultado",
                       "Dificuldade de medição", "Útil para decidir", "Observação"], catalogo)
    linhas += _autoria_da_lista(estado.get("catalogo"))
    papeis = estado.get("papeis", {})
    linhas += ["", "## Papéis exercidos", ""]
    linhas += _tabela(["Papel", "Quem"], [["Responsável pelo projeto", papeis.get("projeto")],
                                          ["Responsável pelo indicador", papeis.get("indicador")],
                                          ["Responsável pelo benefício", papeis.get("beneficio")],
                                          ["Responsável pela governança", papeis.get("governanca")]])
    linhas += [""] + _anotacoes(estado, "sustentacao")
    return "\n".join(linhas).rstrip() + "\n"


GERADORES = {
    "proposta_de_valor": proposta_de_valor,
    "relatorio_monitoramento": relatorio_monitoramento,
    "relatorio_beneficios": relatorio_beneficios,
    "termo_transicao": termo_transicao,
    "licoes_aprendidas": licoes_aprendidas,
}


def gerar(tipo, estado):
    return GERADORES[tipo](estado).rstrip() + "\n" + "\n".join(RODAPE) + "\n"
