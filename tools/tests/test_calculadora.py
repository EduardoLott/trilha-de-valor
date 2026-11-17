"""Testes por exemplo e de propriedades da calculadora.

As propriedades usam um gerador próprio com semente fixa (biblioteca padrão),
para que o resultado seja reproduzível.
"""
import random
import unittest
from fractions import Fraction

from tools import calculadora as c

CASOS = 500
ORDEM = {nome: posicao for posicao, nome in enumerate(c.CLASSES)}


def _fracao(rng):
    return Fraction(rng.randint(-10000, 10000), rng.randint(1, 100))


def _base_meta(rng):
    while True:
        base, meta = _fracao(rng), _fracao(rng)
        if base != meta:
            return base, meta


class Exemplos(unittest.TestCase):
    def test_caso_do_guia(self):
        r = c.realizacao("10", "7", "8")
        self.assertEqual(r, Fraction(2, 3))
        self.assertEqual(c.texto(r), "2/3")
        self.assertEqual(c.percentual(r), "67%")
        self.assertEqual(c.classificar(r), "parcial")

    def test_maior_melhor(self):
        self.assertEqual(c.realizacao("0", "80", "60"), Fraction(3, 4))

    def test_piora_e_negativa(self):
        r = c.realizacao("10", "7", "11")
        self.assertLess(r, 0)
        self.assertEqual(c.classificar(r), "nao_realizado")

    def test_fronteiras_das_faixas(self):
        self.assertEqual(c.classificar("1"), "realizado")
        self.assertEqual(c.classificar("1/2"), "parcial")
        self.assertEqual(c.classificar("0.5"), "parcial")
        self.assertEqual(c.classificar(Fraction(1, 2) - Fraction(1, 10**9)), "nao_realizado")
        self.assertEqual(c.classificar(None), "nao_medido")

    def test_decimal_com_virgula(self):
        self.assertEqual(c.fracao("7,5"), Fraction(15, 2))

    def test_meta_igual_a_base_e_erro(self):
        with self.assertRaises(c.ErroCalculo):
            c.realizacao("10", "10", "8")

    def test_recusa_float_bool_e_texto_invalido(self):
        for ruim in (0.1, True, "dez", "", None, "1/0"):
            with self.assertRaises(c.ErroCalculo):
                c.fracao(ruim)

    def test_faixas_invertidas(self):
        with self.assertRaises(c.ErroCalculo):
            c.classificar("1", realizado_a_partir_de="1/2", parcial_a_partir_de="1")


class Propriedades(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(20261109)

    def test_meta_da_um_e_base_da_zero(self):
        for _ in range(CASOS):
            base, meta = _base_meta(self.rng)
            self.assertEqual(c.realizacao(base, meta, meta), 1)
            self.assertEqual(c.realizacao(base, meta, base), 0)

    def test_invariancia_de_unidade(self):
        for _ in range(CASOS):
            base, meta = _base_meta(self.rng)
            x, desloc = _fracao(self.rng), _fracao(self.rng)
            escala = _fracao(self.rng) or Fraction(1)
            self.assertEqual(c.realizacao(base, meta, x),
                             c.realizacao(escala * base + desloc, escala * meta + desloc, escala * x + desloc))

    def test_aproximar_da_meta_aumenta_a_realizacao(self):
        for _ in range(CASOS):
            base, meta = _base_meta(self.rng)
            x1, x2 = sorted((_fracao(self.rng), _fracao(self.rng)))
            if x1 == x2:
                continue
            r1, r2 = c.realizacao(base, meta, x1), c.realizacao(base, meta, x2)
            if meta > base:
                self.assertLess(r1, r2)
            else:
                self.assertGreater(r1, r2)

    def test_classificacao_monotona_e_total(self):
        for _ in range(CASOS):
            r1, r2 = sorted((_fracao(self.rng) / 100, _fracao(self.rng) / 100))
            c1, c2 = c.classificar(r1), c.classificar(r2)
            self.assertIn(c1, ("nao_realizado", "parcial", "realizado"))
            self.assertLessEqual(ORDEM[c1], ORDEM[c2])

    def test_texto_ida_e_volta(self):
        for _ in range(CASOS):
            x = _fracao(self.rng)
            self.assertEqual(c.fracao(c.texto(x)), x)


if __name__ == "__main__":
    unittest.main()
