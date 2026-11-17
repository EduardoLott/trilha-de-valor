"""Registro de evidências: JSONL só de acréscimo, encadeado por SHA-256.

hash = SHA-256(hash_anterior + registro em JSON canônico, sem o campo 'hash').
A cadeia detecta adulteração, mas não a impede: o último hash precisa ser
guardado fora do alcance do agente (por exemplo, em um commit do git).
"""
import hashlib
import json
from pathlib import Path

from .estado import canonico

GENESE = "0" * 64

# Níveis de garantia de uma evidência
ALEGADO, EXECUTADO, VERIFICADO, PROPRIEDADES, PROVADO = 0, 1, 2, 3, 4


def _hash(hash_anterior, registro):
    corpo = {chave: valor for chave, valor in registro.items() if chave != "hash"}
    return hashlib.sha256(hash_anterior.encode("ascii") + canonico(corpo)).hexdigest()


def ler(caminho):
    caminho = Path(caminho)
    if not caminho.exists():
        return []
    with open(caminho, encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo if linha.strip()]


def registrar(caminho, registro):
    """Acrescenta um registro à cadeia e o devolve com seq, hash_anterior e hash."""
    anteriores = ler(caminho)
    novo = dict(registro)
    novo["seq"] = len(anteriores) + 1
    novo["hash_anterior"] = anteriores[-1]["hash"] if anteriores else GENESE
    novo["hash"] = _hash(novo["hash_anterior"], novo)
    with open(caminho, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(novo, ensure_ascii=False, sort_keys=True) + "\n")
    return novo


def verificar_cadeia(caminho):
    """Devolve (ok, mensagem, ultimo_hash)."""
    try:
        registros = ler(caminho)
    except ValueError as erro:
        return False, "registro ilegível: %s" % erro, None
    if not registros:
        return False, "registro de evidências vazio ou ausente", None
    anterior = GENESE
    for posicao, registro in enumerate(registros, 1):
        if registro.get("seq") != posicao:
            return False, "sequência quebrada no registro %d" % posicao, None
        if registro.get("hash_anterior") != anterior:
            return False, "encadeamento quebrado no registro %d" % posicao, None
        if registro.get("hash") != _hash(anterior, registro):
            return False, "conteúdo alterado no registro %d" % posicao, None
        anterior = registro["hash"]
    return True, "%d registros íntegros" % len(registros), anterior
