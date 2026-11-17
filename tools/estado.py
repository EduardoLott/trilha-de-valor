"""Leitura, gravação e hash do estado do projeto (projeto.json)."""
import hashlib
import json
from pathlib import Path

VERSAO_ESQUEMA = "0.1"
ARQUIVO_ESTADO = "projeto.json"
ARQUIVO_EVIDENCIAS = "evidencias.jsonl"

ETAPAS = ("definicao", "monitoramento", "mensuracao", "sustentacao", "encerrado")


def canonico(objeto):
    """Serialização canônica: mesma entrada, mesmos bytes."""
    return json.dumps(objeto, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256_objeto(objeto):
    return hashlib.sha256(canonico(objeto)).hexdigest()


def sha256_arquivo(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def carregar(pasta):
    with open(Path(pasta) / ARQUIVO_ESTADO, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar(pasta, estado):
    caminho = Path(pasta) / ARQUIVO_ESTADO
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(estado, arquivo, ensure_ascii=False, indent=2, sort_keys=True)
        arquivo.write("\n")
    return sha256_objeto(estado)


def indice_etapa(etapa):
    return ETAPAS.index(etapa)
