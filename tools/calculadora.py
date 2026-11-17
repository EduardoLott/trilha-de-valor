"""Calculadora da Trilha de Valor.

Realização da meta = (resultado - linha de base) / (meta - linha de base).
Usa aritmética exata (Fraction). As contas do assistente passam sempre por aqui.

Uso: python3 -m tools.calculadora <linha_de_base> <meta> <resultado>
"""
import sys
from fractions import Fraction

VERSAO = "0.1.0"
NOME = "calculadora@" + VERSAO

CLASSES = ("nao_medido", "nao_realizado", "parcial", "realizado")


class ErroCalculo(ValueError):
    """Entrada inválida para a calculadora."""


def fracao(valor):
    """Converte texto, inteiro ou Fraction em Fraction. Recusa float e bool."""
    if isinstance(valor, bool) or isinstance(valor, float):
        raise ErroCalculo("use texto ou inteiro, não %s: %r" % (type(valor).__name__, valor))
    if isinstance(valor, (int, Fraction)):
        return Fraction(valor)
    if isinstance(valor, str):
        try:
            return Fraction(valor.strip().replace(",", "."))
        except (ValueError, ZeroDivisionError):
            raise ErroCalculo("valor numérico inválido: %r" % valor)
    raise ErroCalculo("tipo não aceito: %r" % (valor,))


def realizacao(linha_de_base, meta, resultado):
    """Fração da meta que foi realizada. Vale para maior ou menor é melhor."""
    base, alvo, obtido = fracao(linha_de_base), fracao(meta), fracao(resultado)
    if alvo == base:
        raise ErroCalculo("meta igual à linha de base: realização indefinida")
    return (obtido - base) / (alvo - base)


def classificar(valor, realizado_a_partir_de="1", parcial_a_partir_de="1/2"):
    """Classifica a realização conforme as faixas do projeto."""
    if valor is None:
        return "nao_medido"
    r = fracao(valor)
    alto, baixo = fracao(realizado_a_partir_de), fracao(parcial_a_partir_de)
    if baixo > alto:
        raise ErroCalculo("faixa de parcial acima da faixa de realizado")
    if r >= alto:
        return "realizado"
    if r >= baixo:
        return "parcial"
    return "nao_realizado"


def texto(valor):
    """Forma canônica gravada no estado: '2/3', '1', '-1/2'."""
    return str(fracao(valor))


def percentual(valor):
    """Forma de exibição, arredondada: '67%'."""
    return "%d%%" % round(fracao(valor) * 100)


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    try:
        r = realizacao(*argv)
    except ErroCalculo as erro:
        print("erro:", erro)
        return 1
    print("realizacao=%s (%s) classificacao=%s" % (texto(r), percentual(r), classificar(r)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
