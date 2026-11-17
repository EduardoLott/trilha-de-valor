"""Painel de acompanhamento: uma página HTML gerada a partir do projeto.json.

Uso: python3 -m tools.painel PASTA [--saida ARQUIVO]

O painel só lê o estado. Não grava evidência, não aprova nada e não faz contas
além de converter, para exibição, a realização que a calculadora já gravou.
"""
import argparse
import html
from pathlib import Path

from . import calculadora, trilha
from .entregaveis import ROTULO_CLASSE, ROTULO_METODO, ROTULO_TIPO
from .estado import carregar, sha256_objeto

ARQUIVO_PAINEL = "painel.html"
NOMES_ETAPA = {"definicao": "Definição de Valor", "monitoramento": "Monitoramento de Valor",
               "mensuracao": "Mensuração dos Benefícios", "sustentacao": "Governança e Melhoria Contínua",
               "encerrado": "Ciclo encerrado"}
NOMES_DOC = {"proposta_de_valor": "Proposta de Valor", "relatorio_monitoramento": "Relatório de Monitoramento",
             "termo_transicao": "Termo de Transição", "relatorio_beneficios": "Relatório de Benefícios",
             "licoes_aprendidas": "Registro de Lições Aprendidas"}
ORDEM_DOC = list(NOMES_DOC)
ROTULO_SENTIDO = {"menor_melhor": "menor é melhor", "maior_melhor": "maior é melhor"}


def _e(valor):
    return html.escape("" if valor is None else str(valor))


def _data(texto):
    """AAAA-MM-DD → DD/MM/AAAA, sem interpretar."""
    texto = str(texto or "")
    if len(texto) == 10 and texto[4] == "-" and texto[7] == "-":
        return "%s/%s/%s" % (texto[8:], texto[5:7], texto[:4])
    return texto


def _num(texto):
    """Número para posicionar no gráfico; None se não for número."""
    try:
        return float(calculadora.fracao(texto))
    except (calculadora.ErroCalculo, TypeError):
        return None


def _valor(bloco):
    bloco = bloco or {}
    if bloco.get("valor") not in (None, ""):
        return bloco["valor"]
    return None


def _grafico(indicador, leituras, medicoes):
    """SVG com linha de base, meta, leituras (vazadas) e medições (cheias)."""
    base, meta = _valor(indicador.get("linha_de_base")), _valor(indicador.get("meta"))
    pontos = [(p["data"], p["valor"], "leitura") for p in leituras] + [(p["data"], p["valor"], "medicao") for p in medicoes]
    pontos = [p for p in pontos if _num(p[1]) is not None and p[0]]
    pontos.sort(key=lambda p: str(p[0]))
    referencias = [v for v in (_num(base), _num(meta)) if v is not None]
    valores = referencias + [_num(p[1]) for p in pontos]
    if not valores:
        return '<p class="vazio">Sem linha de base, meta ou valores registrados para desenhar.</p>'
    baixo, alto = min(valores), max(valores)
    folga = (alto - baixo) * 0.15 or 1
    baixo, alto = baixo - folga, alto + folga
    largura, altura, esq, dir_, topo, rodape = 640, 220, 56, 16, 14, 34

    def y(v):
        return topo + (alto - v) / (alto - baixo) * (altura - topo - rodape)

    n = len(pontos)

    def x(i):
        if n == 1:
            return (esq + largura - dir_) / 2
        return esq + 24 + i * (largura - esq - dir_ - 48) / (n - 1)

    partes = ['<svg viewBox="0 0 %d %d" role="img" aria-label="Evolução de %s">' % (largura, altura, _e(indicador.get("nome")))]
    partes.append('<line class="eixo" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (esq, altura - rodape, largura - dir_, altura - rodape))
    for rotulo, valor, classe in (("linha de base", base, "base"), ("meta", meta, "meta")):
        v = _num(valor)
        if v is None:
            continue
        partes.append('<line class="ref %s" x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (classe, esq, y(v), largura - dir_, y(v)))
        partes.append('<text class="rotulo %s" x="%d" y="%.1f" text-anchor="end">%s</text>' % (classe, esq - 6, y(v) + 4, _e(valor)))
        partes.append('<text class="legenda-ref %s" x="%d" y="%.1f" text-anchor="start">%s</text>'
                      % (classe, esq + 4, y(v) - 5, rotulo))
    if n > 1:
        caminho = " ".join("%s%.1f,%.1f" % ("M" if i == 0 else "L", x(i), y(_num(p[1]))) for i, p in enumerate(pontos))
        partes.append('<path class="serie" d="%s"/>' % caminho)
    for i, (data, valor, tipo) in enumerate(pontos):
        partes.append('<circle class="%s" cx="%.1f" cy="%.1f" r="5"><title>%s: %s (%s)</title></circle>'
                      % (tipo, x(i), y(_num(valor)), _data(data), _e(valor), "leitura" if tipo == "leitura" else "medição"))
        partes.append('<text class="valor" x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (x(i), y(_num(valor)) - 10, _e(valor)))
        partes.append('<text class="data" x="%.1f" y="%d" text-anchor="middle">%s</text>' % (x(i), altura - 12, _data(data)))
    if not pontos:
        partes.append('<text class="data" x="%d" y="%d" text-anchor="middle">nenhuma leitura ou medição ainda</text>'
                      % ((esq + largura) / 2, altura - 12))
    partes.append("</svg>")
    return "".join(partes)


def _cartao_indicador(estado, indicador):
    ident = indicador.get("id")
    leituras = [l for l in (estado.get("monitoramento") or {}).get("leituras") or [] if l.get("indicador") == ident]
    medicoes = [m for m in estado.get("medicoes") or [] if m.get("indicador") == ident]
    resultados = {r.get("medicao"): r for r in estado.get("resultados") or [] if r.get("indicador") == ident}
    nao_medidos = [n for n in estado.get("nao_medidos") or [] if n.get("indicador") == ident]
    base, meta = indicador.get("linha_de_base") or {}, indicador.get("meta") or {}

    def ref(bloco, campo_data):
        if _valor(bloco) is not None:
            return "%s %s" % (_e(bloco["valor"]), _e(indicador.get("unidade") or "")), _data(bloco.get(campo_data))
        plano = bloco.get("plano") or {}
        if plano:
            return "a definir", "plano: %s até %s" % (_e(plano.get("como")), _data(plano.get("data")))
        return "não informado", ""

    base_txt, base_data = ref(base, "data")
    meta_txt, meta_data = ref(meta, "prazo")
    ultimo = None
    for m in medicoes:
        r = resultados.get(m.get("id"))
        if r:
            ultimo = (m, r)
    if ultimo:
        m, r = ultimo
        classe = r.get("classificacao")
        destaque = ('<div class="destaque %s"><span class="pct">%s</span><span>da meta em %s · %s</span></div>'
                    % (_e(classe), calculadora.percentual(r["realizacao"]), _data(m.get("data")),
                       _e(ROTULO_CLASSE.get(classe, classe))))
    elif leituras:
        l = leituras[-1]
        destaque = ('<div class="destaque neutro"><span class="pct">%s</span><span>última leitura, em %s '
                    '(a realização é calculada na Mensuração)</span></div>' % (_e(l.get("valor")), _data(l.get("data"))))
    else:
        destaque = '<div class="destaque neutro"><span>Sem leitura ou medição registrada</span></div>'

    linhas = []
    for l in leituras:
        linhas.append("<tr><td>%s</td><td>leitura</td><td>%s</td><td>%s</td><td>—</td></tr>"
                      % (_data(l.get("data")), _e(l.get("valor")), _e(l.get("informado_por"))))
    for m in medicoes:
        r = resultados.get(m.get("id"))
        res = ("%s (%s)" % (calculadora.percentual(r["realizacao"]), _e(ROTULO_CLASSE.get(r.get("classificacao"))))
               if r else "não calculado")
        linhas.append("<tr><td>%s</td><td>medição</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                      % (_data(m.get("data")), _e(m.get("valor")), _e(m.get("informado_por")), res))
    for nm in nao_medidos:
        linhas.append('<tr class="nm"><td>%s</td><td>não medido</td><td colspan="3">%s%s</td></tr>'
                      % (_data(nm.get("data")), _e(nm.get("motivo")),
                         (" Plano: %s." % _e(nm.get("plano"))) if nm.get("plano") else ""))
    previstas = [d for d in indicador.get("datas_medicao") or [] if d not in {m.get("data") for m in medicoes}
                 and d not in {n.get("data") for n in nao_medidos}]
    tabela = ""
    if linhas:
        tabela = ('<table><thead><tr><th>Data</th><th>Tipo</th><th>Valor</th><th>Informado por</th><th>Realização</th>'
                  '</tr></thead><tbody>%s</tbody></table>' % "".join(linhas))
    proximas = ('<p class="meta-info">Medições previstas sem registro: %s</p>' % ", ".join(_data(d) for d in previstas)
                if previstas else "")
    situacao = indicador.get("situacao") or "ativo"
    return """
<section class="cartao%s">
  <header>
    <div><span class="tag">%s</span><span class="tag">%s</span>%s</div>
    <h3>%s · %s</h3>
    <p class="meta-info">%s · fonte: %s · %s · responsável: %s</p>
  </header>
  <div class="refs">
    <div><span class="k">Linha de base</span><span class="v">%s</span><span class="d">%s</span></div>
    <div><span class="k">Meta</span><span class="v">%s</span><span class="d">%s</span></div>
    <div><span class="k">Método de comprovação</span><span class="v pequeno">%s</span><span class="d">%s</span></div>
  </div>
  %s
  <figure>%s</figure>
  %s%s
</section>""" % (
        " descontinuado" if situacao == "descontinuado" else "",
        _e(ROTULO_TIPO.get(indicador.get("tipo"), indicador.get("tipo"))),
        _e(ROTULO_SENTIDO.get(indicador.get("sentido"), "")),
        '<span class="tag alerta">descontinuado</span>' if situacao == "descontinuado" else "",
        _e(ident), _e(indicador.get("nome")),
        _e(indicador.get("formula")), _e(indicador.get("fonte")), _e(indicador.get("periodicidade")),
        _e(indicador.get("responsavel")),
        base_txt, base_data, meta_txt, meta_data,
        _e(ROTULO_METODO.get(indicador.get("metodo_comprovacao"), "não se aplica")),
        _e(indicador.get("criterio_sucesso") or ""),
        destaque, _grafico(indicador, leituras, medicoes), tabela, proximas)


def _pendencias(estado):
    itens = []
    for bloco, rotulo in (("riscos", "Risco"), ("encaminhamentos", "Encaminhamento"), ("nao_medidos", "Dado a obter"),
                          ("licoes", "Ação de lição")):
        for item in estado.get(bloco) or []:
            if item.get("situacao") == "concluido":
                continue
            texto = item.get("descricao") or item.get("acao") or item.get("motivo") or item.get("texto") or ""
            if bloco == "riscos" and item.get("tipo") == "oportunidade":
                rotulo_item = "Oportunidade"
            else:
                rotulo_item = rotulo
            itens.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                         % (rotulo_item, _e(item.get("id")), _e(texto), _e(item.get("responsavel") or ""),
                            _data(item.get("prazo"))))
    for premissa in estado.get("premissas") or []:
        if premissa.get("situacao") in ("aberta", "contrariada"):
            itens.append("<tr><td>Premissa %s</td><td>%s</td><td>%s</td><td></td><td></td></tr>"
                         % (_e(premissa.get("situacao")), _e(premissa.get("id")), _e(premissa.get("texto"))))
    if not itens:
        return '<p class="vazio">Nenhuma pendência em aberto.</p>'
    return ('<table><thead><tr><th>Tipo</th><th>Id</th><th>Descrição</th><th>Responsável</th><th>Prazo</th></tr></thead>'
            '<tbody>%s</tbody></table>' % "".join(itens))


def _documentos(estado):
    por_tipo = {d.get("tipo"): d for d in estado.get("documentos") or []}
    passos = []
    for tipo in ORDEM_DOC:
        d = por_tipo.get(tipo)
        if d:
            passos.append('<li class="feito"><strong>%s</strong><span>aprovado em %s por %s</span></li>'
                          % (NOMES_DOC[tipo], _data(d.get("aprovado_em")), _e(d.get("aprovado_por"))))
        else:
            passos.append('<li><strong>%s</strong><span>pendente</span></li>' % NOMES_DOC[tipo])
    return '<ol class="documentos">%s</ol>' % "".join(passos)


def gerar_html(estado, avisos=(), alterado_por_fora=False):
    projeto = estado.get("projeto") or {}
    indicadores = estado.get("indicadores") or []
    ordem = {"resultado": 0, "antecedente": 1, "execucao": 2}
    indicadores = sorted(indicadores, key=lambda i: (ordem.get(i.get("tipo"), 3), str(i.get("id"))))
    alerta = ""
    if alterado_por_fora:
        alerta = ('<div class="aviso forte">O projeto.json foi alterado fora do orquestrador. Este painel mostra um '
                  'estado que não corresponde à trilha de evidências.</div>')
    avisos_html = "".join('<li>%s</li>' % _e(a) for a in avisos)
    beneficios = "".join('<li><strong>%s</strong> %s <span class="meta-info">responsável: %s · prazo: %s</span></li>'
                         % (_e(b.get("id")), _e(b.get("descricao")), _e(b.get("responsavel")), _data(b.get("prazo")))
                         for b in estado.get("beneficios") or [])
    return """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel de Valor</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--ink:#1c1f24;--muted:#5c6470;--line:#dedbd4;--accent:#1f5f8b;
--ok:#2f7d4f;--mid:#b07a12;--bad:#b23b3b;--soft:#eef2f5}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15171a;--card:#1e2126;--ink:#e8e6e1;
--muted:#9aa2ad;--line:#33373e;--accent:#6fb0dc;--ok:#5fbf86;--mid:#e0ac45;--bad:#e27474;--soft:#252a31}}
:root[data-theme="dark"]{--bg:#15171a;--card:#1e2126;--ink:#e8e6e1;--muted:#9aa2ad;--line:#33373e;--accent:#6fb0dc;
--ok:#5fbf86;--mid:#e0ac45;--bad:#e27474;--soft:#252a31}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:26px;margin:4px 0}h2{font-size:17px;margin:32px 0 10px;color:var(--muted);font-weight:600;
text-transform:uppercase;letter-spacing:.04em}h3{font-size:18px;margin:6px 0 2px}
.selo{display:inline-block;font-size:12px;padding:2px 8px;border:1px solid var(--line);border-radius:99px;color:var(--muted)}
.etapa{color:var(--accent);font-weight:600}.meta-info{color:var(--muted);font-size:13px;margin:2px 0}
.aviso{background:var(--soft);border-left:4px solid var(--mid);padding:10px 14px;border-radius:6px;margin:12px 0}
.aviso.forte{border-color:var(--bad)}.aviso ul{margin:4px 0;padding-left:18px}
.cartao{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:14px 0}
.cartao.descontinuado{opacity:.6}
.tag{display:inline-block;font-size:12px;background:var(--soft);color:var(--muted);padding:1px 8px;border-radius:99px;margin-right:6px}
.tag.alerta{color:var(--bad)}
.refs{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:14px 0}
.refs div{background:var(--soft);border-radius:8px;padding:8px 10px;display:flex;flex-direction:column;min-width:0}
.k{font-size:12px;color:var(--muted)}.v{font-size:20px;font-weight:600}.v.pequeno{font-size:15px}.d{font-size:12px;color:var(--muted)}
.destaque{display:flex;align-items:baseline;gap:10px;padding:8px 0;border-top:1px solid var(--line)}
.pct{font-size:30px;font-weight:700}.destaque.realizado .pct{color:var(--ok)}.destaque.parcial .pct{color:var(--mid)}
.destaque.nao_realizado .pct{color:var(--bad)}.destaque.neutro .pct{color:var(--accent)}
figure{margin:8px 0}svg{width:100%%;height:auto;display:block}
svg .eixo{stroke:var(--line)}svg .ref{stroke-width:1.5;stroke-dasharray:6 5}svg .ref.base{stroke:var(--muted)}
svg .ref.meta{stroke:var(--ok)}svg text{font-size:12px;fill:var(--muted)}svg .rotulo.meta,svg .legenda-ref.meta{fill:var(--ok)}
svg .serie{fill:none;stroke:var(--accent);stroke-width:2}svg .medicao{fill:var(--accent)}
svg .leitura{fill:var(--card);stroke:var(--accent);stroke-width:2}svg .valor{fill:var(--ink);font-weight:600}
table{width:100%%;border-collapse:collapse;font-size:13px;margin-top:8px}th,td{text-align:left;padding:6px 8px;
border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:600}tr.nm td{color:var(--bad)}
.tabela{overflow-x:auto}
.documentos{list-style:none;padding:0;display:grid;grid-template-columns:repeat(5,1fr);gap:8px;counter-reset:d}
.documentos li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px;font-size:13px;
display:flex;flex-direction:column;gap:2px}.documentos li span{color:var(--muted)}
.documentos li.feito{border-color:var(--ok)}.documentos li.feito strong{color:var(--ok)}
.vazio{color:var(--muted);font-style:italic}
footer{margin-top:36px;font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:12px;word-break:break-all}
@media (max-width:720px){.refs{grid-template-columns:1fr}.documentos{grid-template-columns:1fr 1fr}}
</style>
</head>
<body><main>
<span class="selo">Painel de acompanhamento%s</span>
<h1>%s</h1>
<p class="etapa">%s</p>
<p class="meta-info">%s</p>
%s%s
<h2>Documentos do ciclo</h2>
%s
<h2>Benefícios</h2>
<ul>%s</ul>
<h2>Indicadores</h2>
%s
<h2>Pendências em aberto</h2>
<div class="tabela">%s</div>
<footer>Painel gerado a partir do projeto.json pelo comando <code>python3 -m tools.painel</code>. Não substitui os documentos
aprovados nem registra aprovação. Os valores são os informados pela pessoa; a realização e a classificação vêm da calculadora.
Estado de origem (sha256): %s</footer>
</main></body></html>
""" % (
        " · dados fictícios" if projeto.get("ficticio") else "",
        _e(projeto.get("nome")), _e(NOMES_ETAPA.get(projeto.get("etapa_atual"), projeto.get("etapa_atual"))),
        _e(projeto.get("problema") or ""),
        alerta,
        ('<div class="aviso"><strong>Atenção</strong><ul>%s</ul></div>' % avisos_html) if avisos_html else "",
        _documentos(estado), beneficios or '<li class="vazio">Nenhum benefício registrado.</li>',
        "".join(_cartao_indicador(estado, i) for i in indicadores) or '<p class="vazio">Nenhum indicador registrado.</p>',
        _pendencias(estado), sha256_objeto(estado))


def gerar(pasta, saida=None):
    """Gera o painel e devolve o caminho do arquivo."""
    estado = carregar(pasta)
    registrado = trilha._estado_registrado(pasta)
    alterado = registrado is not None and registrado != sha256_objeto(estado)
    destino = Path(saida) if saida else Path(pasta) / ARQUIVO_PAINEL
    destino.write_text(gerar_html(estado, trilha._avisos(estado), alterado), encoding="utf-8")
    return destino


def main(argv=None):
    parser = argparse.ArgumentParser(description="Gera o painel de acompanhamento de um projeto da Trilha de Valor.")
    parser.add_argument("pasta")
    parser.add_argument("--saida")
    args = parser.parse_args(argv)
    print("painel gerado: %s" % gerar(args.pasta, args.saida))


if __name__ == "__main__":
    main()
