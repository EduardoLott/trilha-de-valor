import tempfile
import unittest
from pathlib import Path

from tools import comparar, estado as est, exemplo, trilha


class Comparar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.a, self.b = Path(self.tmp.name) / "exec-1", Path(self.tmp.name) / "exec-2"
        exemplo.gerar(self.a, ate="sustentacao")
        exemplo.gerar(self.b, ate="sustentacao")

    def tearDown(self):
        self.tmp.cleanup()

    def test_execucoes_iguais(self):
        texto, tudo_igual = comparar.relatorio([self.a, self.b])
        self.assertTrue(tudo_igual)
        self.assertNotIn("**NÃO**", texto)
        self.assertIn("2026-09-30 / 10 / 7 / 7 / 1 / realizado", texto)
        self.assertEqual(comparar.resumo(self.a)["etapa"], "encerrado")

    def test_etapa_e_contas_diferentes_sao_apontadas(self):
        exemplo.gerar(self.b, ate="monitoramento")
        trilha.aplicar(self.b, "B1", exemplo.PROPOSTAS["B1"])
        trilha.aplicar(self.b, "B2", {"medicoes": [dict(exemplo.PROPOSTAS["B2"]["medicoes"][0], valor="9")]})
        trilha.calcular(self.b)
        resumos, iguais = comparar.comparar([self.a, self.b])
        self.assertFalse(iguais["contas"])
        self.assertFalse(iguais["etapa"])
        self.assertFalse(iguais["documentos"])
        self.assertEqual(comparar.main([str(self.a), str(self.b)]), 1)

    def test_estado_adulterado_aparece_na_auditoria(self):
        e = est.carregar(self.b)
        e["resultados"][0]["classificacao"] = "realizado"
        est.salvar(self.b, e)
        resumos, iguais = comparar.comparar([self.a, self.b])
        self.assertFalse(iguais["auditoria"])
        self.assertEqual(resumos[1]["auditoria"], "rejeitada")


if __name__ == "__main__":
    unittest.main()
