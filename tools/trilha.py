"""Orquestrador da Trilha de Valor: o único caminho para alterar o estado.

O assistente propõe; este programa valida, grava o estado e registra a evidência.

Uso (a partir da raiz do repositório):
  python3 -m tools.trilha iniciar  PASTA --id ID --nome NOME [--real]
  python3 -m tools.trilha status   PASTA
  python3 -m tools.trilha aplicar  PASTA --no NO --arquivo PROPOSTA.json
  python3 -m tools.trilha verificar PASTA --no NO
  python3 -m tools.trilha calcular PASTA
  python3 -m tools.trilha previa   PASTA --tipo TIPO
  python3 -m tools.trilha mostrar  PASTA [--bloco BLOCO]
  python3 -m tools.trilha aprovar  PASTA --portao NO --por "QUEM DECLAROU" [--em-nome-de "CARGO"] [--papel PAPEL]
  python3 -m tools.trilha aceitar  PASTA --papel PAPEL --por "QUEM DECLAROU" [--em-nome-de "CARGO"]
  python3 -m tools.trilha ocorrencia PASTA --texto "FATO DA CONVERSA QUE NÃO VAI PARA O DOCUMENTO"

Opção comum: --modelo "identificação do modelo de IA" (ou variável TRILHA_MODELO).
"""
import argparse
import copy
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import calculadora, dag as dag_mod, entregaveis, evidencias, verificador
from .estado import (ARQUIVO_ESTADO, ARQUIVO_EVIDENCIAS, ETAPAS, VERSAO_ESQUEMA, carregar, indice_etapa, salvar,
                     sha256_arquivo, sha256_objeto)

DAG = dag_mod.DAG_TRILHA
RAIZ = Path(__file__).resolve().parent.parent

# Blocos que só o orquestrador ou a calculadora gravam
PROTEGIDOS = ("resultados", "documentos", "execucao")
PROJETO_FIXO = ("id", "etapa_atual", "versao_esquema", "ficticio")

# Portão -> documentos gerados e aprovados nele: (tipo, pasta, nome do arquivo)
DOCUMENTOS = {
    "G1": [("proposta_de_valor", "01-definicao", "proposta-de-valor")],
    "G2": [("relatorio_monitoramento", "02-monitoramento", "relatorio-monitoramento")],
    "G3": [("relatorio_beneficios", "03-mensuracao", "relatorio-beneficios")],
    "GT": [("termo_transicao", "04-sustentacao", "termo-transicao")],
    "G4": [("licoes_aprendidas", "04-sustentacao", "licoes-aprendidas")],
}
# Portões que encerram uma etapa (o aceite da transição, GT, não muda a etapa)
ENCERRA_ETAPA = ("G1", "G2", "G3", "G4")
NO_DE_CALCULO = "B4"

# Blocos que uma proposta pode trazer
BLOCOS = ("projeto", "objetivos", "beneficios", "indicadores", "papeis", "raci", "classificacao", "monitoramento",
          "riscos", "decisoes", "medicoes", "nao_medidos", "atribuicao", "encaminhamentos", "premissas", "anotacoes",
          "transicao", "licoes", "catalogo")
LISTAS_COM_ID = ("objetivos", "beneficios", "indicadores", "riscos", "decisoes", "medicoes", "nao_medidos",
                 "encaminhamentos", "premissas", "anotacoes", "licoes", "catalogo")
VALORES = {
    ("indicadores", "tipo"): verificador.TIPOS_INDICADOR,
    ("indicadores", "sentido"): ("menor_melhor", "maior_melhor"),
    ("indicadores", "situacao"): ("ativo", "revisado", "descontinuado"),
    ("indicadores", "metodo_comprovacao"): verificador.METODOS,
    ("premissas", "situacao"): ("aberta", "confirmada", "contrariada", "descartada"),
    ("premissas", "criada_por"): ("agente", "pessoa"),
    ("atribuicao", "conclusao"): ("atribuivel", "parcial", "nao_atribuivel"),
    ("encaminhamentos", "decisao"): ("manter", "corrigir", "revisar", "encerrar"),
    ("riscos", "tipo"): ("risco", "oportunidade"),
    ("riscos", "situacao"): ("aberto", "concluido"),
    ("encaminhamentos", "situacao"): ("aberto", "concluido"),
    ("nao_medidos", "situacao"): ("aberto", "concluido"),
    ("licoes", "situacao"): ("aberto", "concluido"),
    ("catalogo", "dificuldade"): ("baixa", "media", "alta"),
    ("licoes", "etapa"): ("definicao", "monitoramento", "mensuracao", "sustentacao", "framework"),
    ("catalogo", "util_para_decidir"): ("sim", "em_parte", "nao"),
    ("decisoes", "tipo"): ("mudanca_escopo", "revisao_indicador", "revisao_meta", "revisao_linha_de_base",
                           "encaminhamento", "outra"),
}


class ErroTrilha(Exception):
    """Operação recusada pelo orquestrador."""


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dentro_do_repositorio(pasta):
    try:
        Path(pasta).resolve().relative_to(RAIZ)
        return True
    except ValueError:
        return False


def _ator(modelo):
    modelo = modelo or os.environ.get("TRILHA_MODELO")
    return {"tipo": "agente", "modelo": modelo or "não informado"}


def _nos(estado):
    return {n["id"]: n for n in estado.setdefault("execucao", {}).setdefault("nos", [])}


def _marcar(estado, ident, situacao, nivel):
    nos = estado.setdefault("execucao", {}).setdefault("nos", [])
    registro = next((n for n in nos if n["id"] == ident), None)
    if registro is None:
        registro = {"id": ident}
        nos.append(registro)
    exigido = "H" if DAG[ident]["tipo"] == "portao" else DAG[ident]["nivel_exigido"]
    registro.update({"estado": situacao, "nivel_exigido": exigido, "nivel_alcancado": nivel})


def _estado_registrado(pasta):
    """Hash do estado no último registro de evidência que o traz (ou None)."""
    for registro in reversed(evidencias.ler(Path(pasta) / ARQUIVO_EVIDENCIAS)):
        if registro.get("estado_sha256"):
            return registro["estado_sha256"]
    return None


def _carregar_conferido(pasta):
    """Carrega o estado e recusa se ele foi alterado fora do orquestrador."""
    estado = carregar(pasta)
    registrado = _estado_registrado(pasta)
    if registrado is not None and registrado != sha256_objeto(estado):
        raise ErroTrilha("o projeto.json foi alterado fora do orquestrador depois do último registro; "
                         "nada foi gravado. Desfaça a edição direta (o hash registrado é %s) e refaça a "
                         "mudança por 'aplicar'" % registrado)
    return estado


def _gravar(pasta, estado, registro, momento):
    """Salva o estado e acrescenta a evidência, já com o hash do estado gravado."""
    salvar(pasta, estado)
    registro = dict(registro, momento=momento or agora(), projeto=estado["projeto"]["id"],
                    estado_sha256=sha256_objeto(estado))
    return evidencias.registrar(Path(pasta) / ARQUIVO_EVIDENCIAS, registro)


def _exigir_liberado(estado, ident):
    if ident not in DAG:
        raise ErroTrilha("nó desconhecido: %s" % ident)
    no, etapa = DAG[ident], estado["projeto"]["etapa_atual"]
    if etapa == "encerrado":
        raise ErroTrilha("o projeto está encerrado")
    if no["etapa"] != etapa and no["etapa"] != dag_mod.TRANSVERSAL:
        raise ErroTrilha("o nó %s é da etapa %s, e o projeto está em %s" % (ident, no["etapa"], etapa))
    nos = _nos(estado)
    pendentes = [d for d in no["depende_de"] if not dag_mod.concluido(DAG[d], nos.get(d))]
    if pendentes:
        raise ErroTrilha("o nó %s depende de %s, ainda não concluído(s)" % (ident, ", ".join(pendentes)))
    return no


def _descendentes(ident):
    achados, fila = set(), [ident]
    while fila:
        atual = fila.pop()
        for outro, no in DAG.items():
            if atual in no["depende_de"] and outro not in achados:
                achados.add(outro)
                fila.append(outro)
    return achados


def _mesclar(atual, novo):
    if isinstance(atual, dict) and isinstance(novo, dict):
        saida = dict(atual)
        for chave, valor in novo.items():
            saida[chave] = _mesclar(atual.get(chave), valor)
        return saida
    if isinstance(novo, list) and novo and all(isinstance(i, dict) and "id" in i for i in novo):
        saida = [copy.deepcopy(i) for i in (atual or [])] if isinstance(atual, list) else []
        posicao = {item.get("id"): n for n, item in enumerate(saida) if isinstance(item, dict)}
        for item in novo:
            if item["id"] in posicao:
                saida[posicao[item["id"]]] = _mesclar(saida[posicao[item["id"]]], item)
            else:
                saida.append(copy.deepcopy(item))
        return saida
    return copy.deepcopy(novo)


def _falhas_do_no(estado, pasta, ident, hoje=None):
    """Regras que uma verificação precisa ver aprovadas. hoje: data de referência (AAAA-MM-DD)."""
    hoje = hoje or agora()[:10]
    falhas = verificador.verificar(estado, pasta=pasta, exigir_ficticio=dentro_do_repositorio(pasta),
                                   exigir_datas=(ident in ("V2", "V3")), exigir_resultados=(ident == "V3"))
    if ident == "V3":
        for indicador in estado.get("indicadores", []):
            if indicador.get("tipo") != "resultado" or indicador.get("situacao") == "descontinuado":
                continue
            futuras = sorted(str(d) for d in indicador.get("datas_medicao") or [] if str(d) > hoje)
            if futuras:
                falhas.append({"regra": "B2", "item": indicador.get("id", "?"),
                               "motivo": "ainda há medição prevista para %s; o Relatório de Benefícios só é aprovado "
                                         "depois da última medição prevista" % ", ".join(futuras)})
        medidos = {r.get("indicador") for r in estado.get("resultados", [])}
        decididos = {e.get("indicador") for e in estado.get("encaminhamentos", [])}
        for indicador in sorted(medidos - decididos):
            falhas.append({"regra": "B5", "item": indicador, "motivo": "resultado sem decisão registrada"})
    if ident == "V2":
        for decisao in estado.get("decisoes", []):
            if decisao.get("tipo") == "mudanca_escopo":
                gatilho = decisao.get("gatilho")
                if not isinstance(gatilho, dict) or any(not isinstance(gatilho.get(c), bool) for c in GATILHO):
                    falhas.append({"regra": "M4", "item": decisao.get("id", "?"),
                                   "motivo": "mudança de escopo sem o gatilho de revisão respondido "
                                             "(gatilho: altera_valor, novas_dependencias, alinhada, com true ou false)"})
                elif gatilho["altera_valor"] and not decisao.get("afeta"):
                    falhas.append({"regra": "M4", "item": decisao.get("id", "?"),
                                   "motivo": "o gatilho diz que a mudança altera valor, mas 'afeta' está vazio"})
    if ident == "VT":
        transicao = estado.get("transicao") or {}
        for campo, rotulo in (("data", "data da transição"), ("recebido_por", "quem assume o acompanhamento"),
                              ("itens", "o que foi entregue"), ("apoio_ate_primeira_medicao", "quem da equipe do "
                               "projeto fica disponível até a primeira medição")):
            if not transicao.get(campo):
                falhas.append({"regra": "S2", "item": "transicao." + campo, "motivo": "falta " + rotulo})
    if ident == "V4":
        aceites = (_termo(estado) or {}).get("aceites") or {}
        for papel in PAPEIS_DO_ACEITE:
            if papel not in aceites:
                falhas.append({"regra": "S2", "item": "aceite." + papel,
                               "motivo": "o Termo de Transição não tem o aceite deste papel (comando 'aceitar')"})
        licoes = estado.get("licoes") or []
        if not licoes:
            falhas.append({"regra": "S3", "item": "licoes", "motivo": "nenhuma lição registrada"})
        for licao in licoes:
            for campo in ("licao", "acao", "responsavel", "prazo"):
                if not licao.get(campo):
                    falhas.append({"regra": "S3", "item": licao.get("id", "?"),
                                   "motivo": "lição sem %s (uma lição só entra com ação, responsável e prazo)" % campo})
        no_catalogo = {c.get("indicador") for c in estado.get("catalogo") or []}
        for indicador in estado.get("indicadores", []):
            if indicador.get("id") not in no_catalogo:
                falhas.append({"regra": "S4", "item": indicador.get("id", "?"),
                               "motivo": "indicador sem registro no catálogo"})
    return falhas


REDACAO = ("pessoa", "assistente")
# Blocos cujo texto vai para os documentos e precisa declarar quem redigiu
COM_AUTORIA = ("anotacoes", "atribuicao", "riscos", "decisoes", "nao_medidos", "encaminhamentos", "licoes", "catalogo")
GATILHO = ("altera_valor", "novas_dependencias", "alinhada")
PAPEIS_DO_ACEITE = ("beneficio", "governanca")


def _termo(estado):
    termos = [d for d in estado.get("documentos", []) if d.get("tipo") == "termo_transicao"]
    return termos[-1] if termos else None


def _avisos(estado):
    """Pontos que pedem uma pergunta à pessoa (não bloqueiam)."""
    if estado["projeto"]["etapa_atual"] == "encerrado":
        return []
    hoje, avisos = agora()[:10], []
    cobertas = {(m.get("indicador"), m.get("data")) for m in estado.get("medicoes", [])}
    cobertas |= {(n.get("indicador"), n.get("data")) for n in estado.get("nao_medidos", [])}
    for indicador in estado.get("indicadores", []):
        ident = indicador.get("id")
        for campo in ("linha_de_base", "meta"):
            data = ((indicador.get(campo) or {}).get("plano") or {}).get("data")
            if data and str(data) < hoje:
                avisos.append("o plano de %s do %s venceu em %s" % (campo, ident, data))
        for data in indicador.get("datas_medicao") or []:
            if str(data) < hoje and (ident, data) not in cobertas:
                avisos.append("a medição do %s prevista para %s já passou e não há medição nem justificativa" % (ident, data))
    for bloco, rotulo in (("riscos", "o risco"), ("encaminhamentos", "o encaminhamento"), ("nao_medidos", "a obtenção do dado"),
                          ("licoes", "a ação da lição")):
        for item in estado.get(bloco) or []:
            if item.get("prazo") and str(item["prazo"]) < hoje and item.get("situacao") != "concluido":
                avisos.append("%s %s tinha prazo em %s" % (rotulo, item.get("id"), item["prazo"]))
    termo = _termo(estado)
    nos = _nos(estado)
    if termo is None and dag_mod.concluido(DAG["G2"], nos.get("G2")):
        avisos.append("o Relatório de Monitoramento já foi aprovado e a transição para a operação ainda não foi aceita")
    if termo is not None:
        for papel in PAPEIS_DO_ACEITE:
            if papel not in (termo.get("aceites") or {}):
                avisos.append("o Termo de Transição ainda não tem o aceite do responsável pel%s %s"
                              % ("o" if papel == "beneficio" else "a", "benefício" if papel == "beneficio" else "governança"))
    return avisos


NAO_IDENTIFICA = ("nao informou", "não informou", "nao sei", "não sei", "desconhecido", "anonimo", "anônimo",
                  "pessoa", "usuario", "usuário", "n/a", "-")


def _identifica(texto):
    """Exige um nome ou cargo, não um texto vazio ou que diga que ninguém foi identificado."""
    texto = (texto or "").strip().lower()
    return len(texto) >= 3 and texto not in NAO_IDENTIFICA and not any(
        marca in texto for marca in ("não informou", "nao informou", "sem nome", "não identific", "nao identific"))


def _validar(proposta, novo):
    """Recusa cedo o que a verificação só apontaria depois, ou nunca."""
    for chave in proposta:
        if chave in PROTEGIDOS:
            raise ErroTrilha("o bloco %r só é gravado pelo orquestrador ou pela calculadora" % chave)
        if chave not in BLOCOS:
            raise ErroTrilha("bloco desconhecido: %r. Blocos aceitos: %s" % (chave, ", ".join(BLOCOS)))
    for bloco in LISTAS_COM_ID:
        itens = novo.get(bloco)
        if itens is None:
            continue
        if not isinstance(itens, list) or any(not isinstance(i, dict) or not i.get("id") for i in itens):
            raise ErroTrilha("o bloco %r precisa ser uma lista de objetos, cada um com 'id'" % bloco)
    for (bloco, campo), aceitos in VALORES.items():
        for item in novo.get(bloco) or []:
            if isinstance(item, dict) and item.get(campo) is not None and item.get(campo) not in aceitos:
                raise ErroTrilha("%s %s: %s=%r não é aceito. Valores: %s"
                                 % (bloco, item.get("id", item.get("indicador", "?")), campo, item.get(campo),
                                    ", ".join(aceitos)))
    transicao = novo.get("transicao")
    for bloco in COM_AUTORIA:
        for item in (novo.get(bloco) or []) + ([dict(transicao, id="transicao")] if bloco == "anotacoes" and transicao else []):
            rotulo = item.get("id") or item.get("indicador") or "?"
            if rotulo == "transicao":
                bloco_txt = "bloco"
            else:
                bloco_txt = bloco
            if item.get("redacao") not in REDACAO:
                raise ErroTrilha("%s %s: informe 'redacao': \"pessoa\" (o texto são as palavras dela) ou "
                                 "\"assistente\" (você redigiu e ela concordou com o texto)" % (bloco_txt, rotulo))
            if item["redacao"] == "assistente" and not _identifica(item.get("confirmado_por")):
                raise ErroTrilha("%s %s: texto redigido pelo assistente precisa de 'confirmado_por' "
                                 "(nome ou cargo de quem leu e concordou com a redação)" % (bloco_txt, rotulo))
    for item in novo.get("premissas") or []:
        if item.get("criada_por") not in ("agente", "pessoa"):
            raise ErroTrilha("premissa %s: informe 'criada_por': \"agente\" (você presumiu ou redigiu) ou "
                             "\"pessoa\" (ela enunciou, com as palavras dela)" % item.get("id"))
    for item in novo.get("nao_medidos") or []:
        for campo in ("indicador", "data", "motivo"):
            if not item.get(campo):
                raise ErroTrilha("não medido %s: falta '%s' (data é a data de referência da medição que faltou, "
                                 "por exemplo o fim do período)" % (item.get("id"), campo))
    for indicador in novo.get("indicadores") or []:
        for campo in ("linha_de_base", "meta"):
            valor = indicador.get(campo)
            if valor is not None and not isinstance(valor, dict):
                raise ErroTrilha("indicador %s: %s precisa ser um objeto com 'valor' ou 'plano'" % (indicador["id"], campo))
            plano = (valor or {}).get("plano")
            if plano is not None and (valor or {}).get("valor") not in (None, ""):
                raise ErroTrilha("indicador %s: %s tem 'valor' e 'plano' ao mesmo tempo; para trocar o valor por um "
                                 "plano, envie também \"valor\": null" % (indicador["id"], campo))
            if plano is not None and (not isinstance(plano, dict) or not plano.get("como") or not plano.get("data")):
                raise ErroTrilha("indicador %s: o plano de %s precisa de 'como' e 'data'" % (indicador["id"], campo))


# ---------------------------------------------------------------- operações

def iniciar(pasta, ident, nome, ficticio=True, modelo=None, momento=None):
    pasta = Path(pasta)
    if (pasta / ARQUIVO_ESTADO).exists():
        raise ErroTrilha("já existe um projeto em %s" % pasta)
    if not ficticio and dentro_do_repositorio(pasta):
        raise ErroTrilha("projeto com dados reais não pode ficar dentro do repositório")
    for sub in ("01-definicao", "02-monitoramento", "03-mensuracao", "04-sustentacao", "rascunhos"):
        (pasta / sub).mkdir(parents=True, exist_ok=True)
    estado = {"projeto": {"id": ident, "nome": nome, "versao_esquema": VERSAO_ESQUEMA, "ficticio": bool(ficticio),
                          "etapa_atual": "definicao"},
              "execucao": {"nos": []}}
    _gravar(pasta, estado, {"tipo": "inicio", "ator": _ator(modelo), "nivel": evidencias.EXECUTADO}, momento)
    return estado


def aplicar(pasta, ident, proposta, modelo=None, momento=None):
    """Aplica uma proposta (dicionário) ao estado, como resultado do nó de execução `ident`."""
    estado = _carregar_conferido(pasta)
    no = _exigir_liberado(estado, ident)
    if no["tipo"] != "execucao":
        raise ErroTrilha("o nó %s não é de execução; use verificar, calcular ou aprovar" % ident)
    if not isinstance(proposta, dict) or not proposta:
        raise ErroTrilha("a proposta precisa ser um objeto JSON não vazio")
    for chave in PROJETO_FIXO:
        if chave in proposta.get("projeto", {}) and proposta["projeto"][chave] != estado["projeto"].get(chave):
            raise ErroTrilha("projeto.%s não pode ser alterado por proposta" % chave)
    novo = _mesclar(estado, proposta)
    _validar(proposta, novo)
    nos = _nos(novo)
    invalidados = []
    so_anotacoes = set(proposta) == {"anotacoes"}
    for outro in ([] if so_anotacoes else sorted(_descendentes(ident))):
        registro = nos.get(outro)
        if registro and DAG[outro]["tipo"] != "execucao" and dag_mod.concluido(DAG[outro], registro):
            registro["estado"] = "invalidado"
            invalidados.append(outro)
    if NO_DE_CALCULO in invalidados:
        novo["resultados"] = []
    _marcar(novo, ident, "executado", evidencias.EXECUTADO)
    _gravar(pasta, novo, {"tipo": "execucao", "no": ident, "operacao": no["nome"], "ator": _ator(modelo),
                          "nivel": evidencias.EXECUTADO, "entradas": {"sha256": sha256_objeto(proposta)},
                          "blocos": sorted(proposta), "invalidados": invalidados}, momento)
    return {"no": ident, "invalidados": invalidados, "liberados": dag_mod.liberados(DAG, _nos(novo))}


def calcular(pasta, modelo=None, momento=None):
    """Nó B4: a calculadora produz realização e classificação de cada medição."""
    estado = _carregar_conferido(pasta)
    no = _exigir_liberado(estado, NO_DE_CALCULO)
    indicadores = {i["id"]: i for i in estado.get("indicadores", [])}
    faixas = estado.get("classificacao", {})
    resultados, detalhes = [], []
    for medicao in estado.get("medicoes", []):
        indicador = indicadores.get(medicao.get("indicador"))
        if indicador is None:
            raise ErroTrilha("medição %s aponta para indicador inexistente" % medicao.get("id"))
        try:
            r = calculadora.realizacao((indicador.get("linha_de_base") or {}).get("valor"),
                                       (indicador.get("meta") or {}).get("valor"), medicao.get("valor"))
            classe = calculadora.classificar(r, faixas.get("realizado_a_partir_de", "1"),
                                             faixas.get("parcial_a_partir_de", "1/2"))
        except calculadora.ErroCalculo as erro:
            raise ErroTrilha("não foi possível calcular %s: %s" % (medicao.get("id"), erro))
        resultados.append({"indicador": indicador["id"], "medicao": medicao["id"], "realizacao": calculadora.texto(r),
                           "classificacao": classe, "ferramenta": calculadora.NOME})
        detalhes.append("%s (%s): linha de base %s, meta %s, resultado %s em %s -> realização %s (%s), %s" % (
            indicador["id"], indicador.get("nome"), indicador["linha_de_base"]["valor"], indicador["meta"]["valor"],
            medicao.get("valor"), medicao.get("data"), calculadora.texto(r), calculadora.percentual(r), classe))
    if not resultados:
        raise ErroTrilha("não há medições para calcular; se o dado não existe, registre 'não medido' e o motivo")
    estado["resultados"] = resultados
    _marcar(estado, NO_DE_CALCULO, "verificado", evidencias.VERIFICADO)
    _gravar(pasta, estado, {"tipo": "verificacao", "no": NO_DE_CALCULO, "operacao": no["nome"], "ator": _ator(modelo),
                            "nivel": evidencias.VERIFICADO,
                            "evidencias": [{"tipo": "calculo", "ferramenta": calculadora.NOME}],
                            "saidas": {"sha256": sha256_objeto(resultados), "resultados": resultados}}, momento)
    calcular.detalhes = detalhes + ["faixas: realizado a partir de %s da meta; parcial a partir de %s" % (
        calculadora.percentual(faixas.get("realizado_a_partir_de", "1")),
        calculadora.percentual(faixas.get("parcial_a_partir_de", "1/2")))]
    return resultados


def verificar(pasta, ident, modelo=None, momento=None):
    """Nó de verificação: aplica as regras. Só marca como verificado se não houver falha."""
    if ident == NO_DE_CALCULO:
        raise ErroTrilha("use 'calcular' para o nó %s" % NO_DE_CALCULO)
    estado = _carregar_conferido(pasta)
    no = _exigir_liberado(estado, ident)
    if no["tipo"] != "verificacao":
        raise ErroTrilha("o nó %s não é de verificação" % ident)
    falhas = _falhas_do_no(estado, pasta, ident, hoje=(momento or agora())[:10])
    if falhas:
        _marcar(estado, ident, "falhou", 0)
    else:
        _marcar(estado, ident, "verificado", evidencias.VERIFICADO)
    _gravar(pasta, estado, {"tipo": "verificacao", "no": ident, "operacao": no["nome"], "ator": _ator(modelo),
                            "nivel": 0 if falhas else evidencias.VERIFICADO,
                            "evidencias": [{"tipo": "regras", "ferramenta": "verificador", "falhas": falhas}]}, momento)
    return falhas


def previa(pasta, tipo):
    if tipo not in entregaveis.GERADORES:
        raise ErroTrilha("tipo de documento desconhecido: %s" % tipo)
    estado = carregar(pasta)
    texto = entregaveis.gerar(tipo, estado)
    portao = next(g for g, docs in DOCUMENTOS.items() if any(d[0] == tipo for d in docs))
    nos = _nos(estado)
    if not dag_mod.concluido(DAG[portao], nos.get(portao)):
        pendentes = [d for d in DAG[portao]["depende_de"] if not dag_mod.concluido(DAG[d], nos.get(d))]
        if pendentes:
            texto = "> RASCUNHO: a verificação %s ainda não foi aprovada. Este documento não pode ser aprovado.\n\n%s" % (
                ", ".join(pendentes), texto)
    return texto


def mostrar(pasta, bloco=None):
    """Leitura do estado (ou de um bloco), para o assistente conferir o que está gravado."""
    estado = carregar(pasta)
    if bloco is not None:
        if bloco in BLOCOS and bloco not in estado:
            return "[]" if bloco in LISTAS_COM_ID or bloco in ("raci", "atribuicao") else "{}"
        if bloco not in estado:
            raise ErroTrilha("bloco ausente no estado: %r. Presentes: %s" % (bloco, ", ".join(sorted(estado))))
        estado = estado[bloco]
    return json.dumps(estado, ensure_ascii=False, indent=2, sort_keys=True)


def aprovar(pasta, portao, por, modelo=None, momento=None, em_nome_de=None, papel=None):
    """Portão: gera os documentos, registra a aprovação nominal e avança a etapa.

    por: quem declarou a aprovação. em_nome_de: o cargo ou a pessoa que ela representa (padrão: ela mesma).
    papel: só no aceite do Termo de Transição (GT), 'beneficio' ou 'governanca'.
    """
    if not por or not por.strip():
        raise ErroTrilha("informe quem aprova (--por)")
    if portao == "GT" and papel not in PAPEIS_DO_ACEITE:
        raise ErroTrilha("no aceite da transição, informe o papel de quem aceita: --papel beneficio ou --papel governanca")
    if portao != "GT" and papel is not None:
        raise ErroTrilha("--papel só vale para o aceite da transição (GT)")
    em_nome_de = (em_nome_de or por).strip()
    estado = _carregar_conferido(pasta)
    no = _exigir_liberado(estado, portao)
    if no["tipo"] != "portao":
        raise ErroTrilha("o nó %s não é um portão" % portao)
    for dep in no["depende_de"]:
        falhas = _falhas_do_no(estado, pasta, dep, hoje=(momento or agora())[:10])
        if falhas:
            raise ErroTrilha("a verificação %s deixou de passar (%d falha(s)); rode-a de novo" % (dep, len(falhas)))
    momento = momento or agora()
    aprovados = []
    for tipo, sub, nome in DOCUMENTOS[portao]:
        versao = 1 + sum(1 for d in estado.get("documentos", []) if d.get("tipo") == tipo)
        relativo = "%s/%s-v%d.md" % (sub, nome, versao)
        destino = Path(pasta) / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(entregaveis.gerar(tipo, estado), encoding="utf-8")
        documento = {"id": "DOC-%d" % (len(estado.get("documentos", [])) + 1), "tipo": tipo, "versao": versao,
                     "arquivo": relativo, "sha256": sha256_arquivo(destino), "aprovado_por": por.strip(),
                     "em_nome_de": em_nome_de, "aprovado_em": momento[:10]}
        if papel:
            documento["aceites"] = {papel: {"por": por.strip(), "em_nome_de": em_nome_de, "em": momento[:10]}}
        if tipo == "proposta_de_valor":
            documento["referencia"] = {
                i["id"]: {"linha_de_base": (i.get("linha_de_base") or {}).get("valor"),
                          "meta": (i.get("meta") or {}).get("valor")}
                for i in estado.get("indicadores", [])}
        estado.setdefault("documentos", []).append(documento)
        aprovados.append(documento)
    _marcar(estado, portao, "aprovado", "H")
    if portao in ENCERRA_ETAPA:
        estado["projeto"]["etapa_atual"] = ETAPAS[indice_etapa(no["etapa"]) + 1]
    for posicao, documento in enumerate(aprovados):
        registro = {"tipo": "aprovacao", "no": portao, "operacao": no["nome"], "ator": _ator(modelo),
                    "aprovado_por": por.strip(), "em_nome_de": em_nome_de, "papel": papel,
                    "documento": documento["id"],
                    "saidas": {"sha256": documento["sha256"], "arquivo": documento["arquivo"]}}
        if posicao == len(aprovados) - 1:
            _gravar(pasta, estado, registro, momento)
        else:
            evidencias.registrar(Path(pasta) / ARQUIVO_EVIDENCIAS, dict(registro, momento=momento,
                                                                       projeto=estado["projeto"]["id"]))
    return aprovados


def aceitar(pasta, papel, por, modelo=None, momento=None, em_nome_de=None):
    """Segundo aceite do Termo de Transição, pelo papel que ainda não aceitou."""
    if papel not in PAPEIS_DO_ACEITE:
        raise ErroTrilha("papel inválido: use beneficio ou governanca")
    if not por or not por.strip():
        raise ErroTrilha("informe quem aceita (--por)")
    estado = _carregar_conferido(pasta)
    termo = _termo(estado)
    if termo is None:
        raise ErroTrilha("ainda não há Termo de Transição; o primeiro aceite é feito com 'aprovar --portao GT'")
    if estado["projeto"]["etapa_atual"] == "encerrado":
        raise ErroTrilha("o projeto está encerrado")
    if papel in (termo.get("aceites") or {}):
        raise ErroTrilha("o Termo já tem o aceite do papel %s" % papel)
    if sha256_arquivo(Path(pasta) / termo["arquivo"]) != termo["sha256"]:
        raise ErroTrilha("o arquivo do Termo de Transição foi alterado depois do primeiro aceite")
    momento = momento or agora()
    em_nome_de = (em_nome_de or por).strip()
    termo.setdefault("aceites", {})[papel] = {"por": por.strip(), "em_nome_de": em_nome_de, "em": momento[:10]}
    nos = _nos(estado)
    if "V4" in nos and dag_mod.concluido(DAG["V4"], nos["V4"]):
        nos["V4"]["estado"] = "invalidado"
    _gravar(pasta, estado, {"tipo": "aceite", "no": "GT", "operacao": DAG["GT"]["nome"], "ator": _ator(modelo),
                            "aprovado_por": por.strip(), "em_nome_de": em_nome_de, "papel": papel,
                            "documento": termo["id"], "saidas": {"sha256": termo["sha256"], "arquivo": termo["arquivo"]}},
            momento)
    return termo


def ocorrencia(pasta, texto, modelo=None, momento=None):
    """Registra, só na trilha de evidências, um fato da conversa que não vai para os documentos
    (por exemplo, um pedido recusado ou uma etapa adiada). Não altera o estado."""
    if not texto or not texto.strip():
        raise ErroTrilha("informe o texto da ocorrência")
    estado = _carregar_conferido(pasta)
    return _gravar(pasta, estado, {"tipo": "ocorrencia", "ator": _ator(modelo), "texto": texto.strip()}, momento)


def status(pasta):
    estado = carregar(pasta)
    nos = _nos(estado)
    etapa = estado["projeto"]["etapa_atual"]
    linhas = ["projeto: %s (%s)" % (estado["projeto"].get("nome"), estado["projeto"].get("id")),
              "etapa atual: %s" % etapa, "", "nós da etapa e nós transversais (S, VT, GT):"]
    for ident, no in DAG.items():
        if no["etapa"] == etapa or (no["etapa"] == dag_mod.TRANSVERSAL and etapa != "encerrado"):
            situacao = nos.get(ident, {}).get("estado", "pendente")
            if ident == "GT" and situacao == "aprovado":
                situacao = "aceite %d/2" % len((_termo(estado) or {}).get("aceites") or {})
            linhas.append("  %-3s %-11s %-10s %s" % (ident, no["tipo"], situacao, no["nome"]))
    linhas += ["", "liberados agora: %s" % (", ".join(dag_mod.liberados(DAG, nos)) or "nenhum")]
    registrado = _estado_registrado(pasta)
    if registrado is not None and registrado != sha256_objeto(estado):
        linhas += ["ATENÇÃO: o projeto.json foi alterado fora do orquestrador; os comandos que gravam vão recusar"]
    abertas = [p for p in estado.get("premissas", []) if p.get("situacao") == "aberta"]
    linhas.append("premissas em aberto: %d (%d bloqueante(s))" % (len(abertas), sum(1 for p in abertas if p.get("bloqueante"))))
    linhas += ["ATENÇÃO: %s; pergunte à pessoa a situação" % aviso for aviso in _avisos(estado)]
    falhas = verificador.verificar(estado, pasta=pasta, exigir_ficticio=dentro_do_repositorio(pasta))
    linhas.append("pendências apontadas pelo verificador: %d" % len(falhas))
    linhas += ["  %-3s %-26s %s" % (f["regra"], f["item"], f["motivo"]) for f in falhas]
    ok, mensagem, ultimo = evidencias.verificar_cadeia(Path(pasta) / ARQUIVO_EVIDENCIAS)
    linhas += ["", "evidências: %s" % mensagem, "último hash: %s" % ultimo]
    return "\n".join(linhas)


# ---------------------------------------------------------------- linha de comando

def _ler_json(caminho):
    texto = sys.stdin.read() if caminho == "-" else Path(caminho).read_text(encoding="utf-8")
    try:
        return json.loads(texto)
    except ValueError as erro:
        raise ErroTrilha("proposta não é JSON válido: %s" % erro)


def main(argv=None):
    p = argparse.ArgumentParser(prog="tools.trilha", description="Orquestrador da Trilha de Valor")
    sub = p.add_subparsers(dest="comando", required=True)

    def comando(nome):
        c = sub.add_parser(nome)
        c.add_argument("pasta")
        c.add_argument("--modelo")
        return c

    c = comando("iniciar"); c.add_argument("--id", required=True); c.add_argument("--nome", required=True)
    c.add_argument("--real", action="store_true", help="projeto com dados reais (fora do repositório)")
    comando("status")
    c = comando("aplicar"); c.add_argument("--no", required=True); c.add_argument("--arquivo", required=True)
    c = comando("verificar"); c.add_argument("--no", required=True)
    comando("calcular")
    c = comando("previa"); c.add_argument("--tipo", required=True, choices=sorted(entregaveis.GERADORES))
    c = comando("mostrar"); c.add_argument("--bloco")
    c = comando("aprovar"); c.add_argument("--portao", required=True); c.add_argument("--por", required=True)
    c.add_argument("--em-nome-de"); c.add_argument("--papel", choices=PAPEIS_DO_ACEITE)
    c = comando("aceitar"); c.add_argument("--papel", required=True, choices=PAPEIS_DO_ACEITE)
    c.add_argument("--por", required=True); c.add_argument("--em-nome-de")
    c = comando("ocorrencia"); c.add_argument("--texto", required=True)
    a = p.parse_args(argv)

    try:
        if a.comando == "iniciar":
            iniciar(a.pasta, a.id, a.nome, ficticio=not a.real, modelo=a.modelo)
            print("projeto criado em %s; etapa: definicao; liberado: D1" % a.pasta)
        elif a.comando == "status":
            print(status(a.pasta))
        elif a.comando == "aplicar":
            r = aplicar(a.pasta, a.no, _ler_json(a.arquivo), modelo=a.modelo)
            print("nó %s registrado" % r["no"])
            if r["invalidados"]:
                print("verificações invalidadas, a refazer: %s" % ", ".join(r["invalidados"]))
            print("liberados agora: %s" % (", ".join(r["liberados"]) or "nenhum"))
        elif a.comando == "verificar":
            falhas = verificar(a.pasta, a.no, modelo=a.modelo)
            for f in falhas:
                print("%-3s %-26s %s" % (f["regra"], f["item"], f["motivo"]))
            print("verificação %s: %s" % (a.no, "APROVADA" if not falhas else "REPROVADA (%d falha(s))" % len(falhas)))
            return 1 if falhas else 0
        elif a.comando == "calcular":
            calcular(a.pasta, modelo=a.modelo)
            print("\n".join(calcular.detalhes))
        elif a.comando == "aceitar":
            termo = aceitar(a.pasta, a.papel, a.por, modelo=a.modelo, em_nome_de=a.em_nome_de)
            print("aceite registrado no %s; aceites: %s" % (termo["id"], ", ".join(sorted(termo["aceites"]))))
        elif a.comando == "ocorrencia":
            print("ocorrência registrada na trilha de evidências (registro %d)" % ocorrencia(a.pasta, a.texto, modelo=a.modelo)["seq"])
        elif a.comando == "mostrar":
            print(mostrar(a.pasta, a.bloco))
        elif a.comando == "previa":
            print(previa(a.pasta, a.tipo))
        elif a.comando == "aprovar":
            for d in aprovar(a.pasta, a.portao, a.por, modelo=a.modelo, em_nome_de=a.em_nome_de, papel=a.papel):
                print("aprovado: %s (%s), sha256 %s" % (d["arquivo"], d["id"], d["sha256"]))
            print("etapa atual: %s" % carregar(a.pasta)["projeto"]["etapa_atual"])
    except ErroTrilha as erro:
        print("recusado: %s" % erro)
        return 1
    except (OSError, ValueError) as erro:
        print("erro: %s" % erro)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
