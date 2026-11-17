"""Testes do painel: só lê o estado e mostra o que a calculadora gravou."""
import tempfile
import unittest
from pathlib import Path

from tools import estado as est, evidencias, exemplo, painel


class Painel(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name) / "exemplo"
        exemplo.gerar(self.pasta)

    def tearDown(self):
        self.tmp.cleanup()

    def test_nao_altera_estado_nem_evidencias(self):
        estado_antes = est.sha256_arquivo(self.pasta / est.ARQUIVO_ESTADO)
        registros = len(evidencias.ler(self.pasta / est.ARQUIVO_EVIDENCIAS))
        painel.gerar(self.pasta)
        self.assertEqual(est.sha256_arquivo(self.pasta / est.ARQUIVO_ESTADO), estado_antes)
        self.assertEqual(len(evidencias.ler(self.pasta / est.ARQUIVO_EVIDENCIAS)), registros)

    def test_mostra_realizacao_da_calculadora_e_hash_do_estado(self):
        texto = painel.gerar(self.pasta).read_text(encoding="utf-8")
        estado = est.carregar(self.pasta)
        self.assertIn("67%", texto)
        self.assertIn("100%", texto)
        self.assertIn(est.sha256_objeto(estado), texto)
        self.assertIn("Tempo de fechamento", texto)
        self.assertIn("dados fictícios", texto)

    def test_escapa_texto_da_pessoa(self):
        estado = est.carregar(self.pasta)
        estado["projeto"]["nome"] = "<script>alert(1)</script>"
        html = painel.gerar_html(estado)
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;script&gt;", html)

    def test_avisa_estado_editado_por_fora(self):
        estado = est.carregar(self.pasta)
        estado["projeto"]["nome"] = "Editado à mão"
        est.salvar(self.pasta, estado)
        self.assertIn("alterado fora do orquestrador", painel.gerar(self.pasta).read_text(encoding="utf-8"))

    def test_projeto_no_inicio_nao_quebra(self):
        pasta = Path(self.tmp.name) / "inicio"
        exemplo.gerar(pasta, ate="definicao")
        texto = painel.gerar(pasta).read_text(encoding="utf-8")
        self.assertIn("Painel de acompanhamento", texto)


if __name__ == "__main__":
    unittest.main()
