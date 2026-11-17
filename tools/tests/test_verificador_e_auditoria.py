import copy
import tempfile
import unittest
from pathlib import Path

from tools import auditar, estado as est, evidencias, exemplo, verificador


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name) / "exemplo"
        self.ultimo = exemplo.gerar(self.pasta)
        self.estado = est.carregar(self.pasta)

    def tearDown(self):
        self.tmp.cleanup()

    def regras(self, estado, **kw):
        return {f["regra"] for f in verificador.verificar(estado, **kw)}

    def mutado(self):
        return copy.deepcopy(self.estado)


class Verificador(Base):
    def test_exemplo_passa(self):
        self.assertEqual(verificador.verificar(self.estado, pasta=self.pasta), [])

    def test_resultado_do_exemplo(self):
        self.assertEqual(self.estado["resultados"][0]["realizacao"], "2/3")
        self.assertEqual(self.estado["resultados"][0]["classificacao"], "parcial")

    def test_cada_regra_dispara(self):
        def c1(e): e["papeis"]["governanca"] = ""
        def c2(e): e["beneficios"][0]["responsavel"] = ""
        def c2b(e): e["beneficios"][0]["indicadores"] = ["IND-2"]
        def c3(e): e["indicadores"][0]["fonte"] = ""
        def c4(e): e["indicadores"][1]["linha_de_base"] = {}
        def c5(e): e["indicadores"][0]["metodo_comprovacao"] = "achismo"
        def c6(e): e["raci"][0]["governanca"] = "A"
        def c7(e): e["indicadores"][0]["datas_medicao"] = []
        def i1(e): e["indicadores"][1]["meta"]["valor"] = "0"
        def i2(e): e["indicadores"][1]["sentido"] = "menor_melhor"
        def i3(e): e["indicadores"][0]["meta"]["origem"] = "agente"
        def i3b(e): e["medicoes"][0]["origem"] = "premissa"
        def i4(e): e["premissas"][0]["bloqueante"] = True
        def i6(e): e["documentos"] = [d for d in e["documentos"] if d["tipo"] != "relatorio_beneficios"]
        def i7(e): e["beneficios"][0]["objetivo"] = "OBJ-9"
        def i8(e): e["projeto"]["ficticio"] = False
        def k1(e):
            e["indicadores"].append(dict(e["indicadores"][1], id="IND-3"))
            e["medicoes"].append(dict(e["medicoes"][0], id="MED-2", indicador="IND-3"))
        def k2(e): e["indicadores"][0]["meta"]["valor"] = "8"
        def k3(e): e["atribuicao"] = []
        def k4(e): e["resultados"][0]["realizacao"] = "7/10"
        def k4b(e): e["resultados"][0]["classificacao"] = "realizado"

        casos = [("C1", c1), ("C2", c2), ("C2", c2b), ("C3", c3), ("C4", c4), ("C5", c5), ("C6", c6), ("C7", c7),
                 ("I1", i1), ("I2", i2), ("I3", i3), ("I3", i3b), ("I4", i4), ("I6", i6), ("I7", i7), ("I8", i8),
                 ("K1", k1), ("K2", k2), ("K3", k3), ("K4", k4), ("K4", k4b)]
        for regra, mutacao in casos:
            e = self.mutado()
            mutacao(e)
            self.assertIn(regra, self.regras(e), "a regra %s não disparou em %s" % (regra, mutacao.__name__))

    def test_mudanca_de_meta_com_decisao_passa_em_k2(self):
        e = self.mutado()
        e["indicadores"][0]["meta"]["valor"] = "8"
        e["decisoes"].append({"id": "DEC-2", "data": "2026-05-02", "tipo": "revisao_meta", "afeta": ["IND-1"],
                              "antes": "7", "depois": "8", "justificativa": "fictícia", "decidido_por": "x"})
        self.assertNotIn("K2", self.regras(e))
        self.assertIn("K4", self.regras(e))  # o resultado gravado deixou de valer

    def test_documento_alterado_dispara_i5(self):
        arquivo = self.pasta / self.estado["documentos"][0]["arquivo"]
        arquivo.write_text(arquivo.read_text(encoding="utf-8") + "\nlinha a mais\n", encoding="utf-8")
        self.assertIn("I5", self.regras(self.estado, pasta=self.pasta))

    def test_linha_de_base_com_plano_passa(self):
        e = self.mutado()
        e["indicadores"][1]["linha_de_base"] = {"plano": {"como": "medir por 2 meses", "data": "2026-03-31"}}
        e["documentos"][0]["referencia"]["IND-2"]["linha_de_base"] = None
        self.assertEqual(self.regras(e), set())


class Auditoria(Base):
    def criterios(self, **kw):
        return {f["criterio"] for f in auditar.auditar(self.pasta, **kw)["falhas"]}

    def test_exemplo_aprovado_com_ancora(self):
        relatorio = auditar.auditar(self.pasta, ancora=self.ultimo)
        self.assertTrue(relatorio["aprovado"], relatorio["falhas"])
        self.assertEqual(relatorio["avisos"], [])

    def test_sem_ancora_avisa(self):
        relatorio = auditar.auditar(self.pasta)
        self.assertTrue(relatorio["aprovado"])
        self.assertEqual(len(relatorio["avisos"]), 1)

    def test_ancora_errada_rejeita(self):
        self.assertIn("A4", self.criterios(ancora="0" * 64))

    def test_estado_editado_por_fora_rejeita(self):
        e = self.mutado()
        e["resultados"][0]["realizacao"] = "1"
        e["resultados"][0]["classificacao"] = "realizado"
        est.salvar(self.pasta, e)
        criterios = self.criterios(ancora=self.ultimo)
        self.assertIn("A5", criterios)
        self.assertIn("A6", criterios)

    def test_edicao_coerente_mas_nao_registrada_rejeita(self):
        e = self.mutado()
        e["projeto"]["descricao"] = "texto trocado sem registro"
        est.salvar(self.pasta, e)
        self.assertEqual(self.criterios(ancora=self.ultimo), {"A5"})

    def test_registro_adulterado_rejeita(self):
        log = self.pasta / est.ARQUIVO_EVIDENCIAS
        log.write_text(log.read_text(encoding="utf-8").replace("Gerente de Controladoria", "Outra Pessoa", 1),
                       encoding="utf-8")
        self.assertIn("A4", self.criterios(ancora=self.ultimo))

    def test_no_pulado_rejeita(self):
        e = self.mutado()
        e["execucao"]["nos"] = [n for n in e["execucao"]["nos"] if n["id"] != "V3"]
        est.salvar(self.pasta, e)
        self.assertIn("A2", self.criterios())

    def test_nivel_declarado_sem_evidencia_rejeita(self):
        e = self.mutado()
        for no in e["execucao"]["nos"]:
            if no["id"] == "D1":
                no["nivel_alcancado"] = 4
        est.salvar(self.pasta, e)
        self.assertIn("A3", self.criterios())

    def test_documento_sem_aprovacao_registrada_rejeita(self):
        e = self.mutado()
        e["documentos"][2]["aprovado_por"] = "Outra Pessoa"
        est.salvar(self.pasta, e)
        self.assertIn("A7", self.criterios())

    def test_geracao_e_reproduzivel(self):
        outra = Path(self.tmp.name) / "outra"
        self.assertEqual(exemplo.gerar(outra), self.ultimo)
        self.assertEqual(len(evidencias.ler(outra / est.ARQUIVO_EVIDENCIAS)), 22)

    def test_exemplo_nao_apaga_pasta_alheia(self):
        alheia = Path(self.tmp.name) / "alheia"
        alheia.mkdir()
        (alheia / "importante.txt").write_text("não apagar", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            exemplo.gerar(alheia)
        self.assertTrue((alheia / "importante.txt").exists())


if __name__ == "__main__":
    unittest.main()
