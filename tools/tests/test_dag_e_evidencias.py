import copy
import json
import random
import tempfile
import unittest
from pathlib import Path

from tools import dag, evidencias


class Dag(unittest.TestCase):
    def test_dag_da_trilha_e_valido(self):
        self.assertEqual(dag.validar(dag.DAG_TRILHA), [])

    def test_ordem_respeita_dependencias(self):
        posicao = {}
        for numero, onda in enumerate(dag.ondas(dag.DAG_TRILHA)):
            for ident in onda:
                posicao[ident] = numero
        self.assertEqual(set(posicao), set(dag.DAG_TRILHA))
        for ident, no in dag.DAG_TRILHA.items():
            for dep in no["depende_de"]:
                self.assertLess(posicao[dep], posicao[ident])

    def test_paralelismo_esperado(self):
        ondas = dag.ondas(dag.DAG_TRILHA)
        self.assertIn(["D3", "D5"], ondas)
        self.assertTrue(any({"M1", "S1"} <= set(o) for o in ondas))  # papéis: logo depois da Proposta
        self.assertTrue(any({"B1", "S2"} <= set(o) for o in ondas))  # transição: logo depois do Monitoramento
        self.assertTrue(any({"S3"} <= set(o) for o in ondas))

    def test_detecta_ciclo(self):
        ruim = copy.deepcopy(dag.DAG_TRILHA)
        ruim["D1"]["depende_de"] = ("D4",)
        self.assertTrue(any("ciclo" in p for p in dag.validar(ruim)))

    def test_detecta_dependencia_inexistente(self):
        ruim = copy.deepcopy(dag.DAG_TRILHA)
        ruim["D2"]["depende_de"] = ("X9",)
        self.assertTrue(any("inexistente" in p for p in dag.validar(ruim)))

    def test_portao_sem_verificacao(self):
        ruim = copy.deepcopy(dag.DAG_TRILHA)
        ruim["G1"]["depende_de"] = ("D4",)
        self.assertTrue(any("portão" in p for p in dag.validar(ruim)))

    def test_dois_nos_finais(self):
        ruim = copy.deepcopy(dag.DAG_TRILHA)
        ruim["Z1"] = dag._no("sustentacao", "execucao", "solto", ["G3"])
        self.assertTrue(any("único nó final" in p for p in dag.validar(ruim)))

    def test_executado_nao_libera_quando_exige_verificacao(self):
        feitos = {i: {"estado": "executado", "nivel_alcancado": 1} for i in ("D1", "D2", "D3", "D4", "D5")}
        self.assertEqual(dag.liberados(dag.DAG_TRILHA, feitos), ["V1"])
        feitos["V1"] = {"estado": "executado", "nivel_alcancado": 1}
        self.assertEqual(dag.liberados(dag.DAG_TRILHA, feitos), ["V1"])
        feitos["V1"] = {"estado": "verificado", "nivel_alcancado": 2}
        self.assertEqual(dag.liberados(dag.DAG_TRILHA, feitos), ["G1"])
        feitos["G1"] = {"estado": "verificado", "nivel_alcancado": 4}
        self.assertEqual(dag.liberados(dag.DAG_TRILHA, feitos), ["G1"])
        feitos["G1"] = {"estado": "aprovado"}
        self.assertEqual(dag.liberados(dag.DAG_TRILHA, feitos), ["M1", "S1"])

    def test_inicio(self):
        self.assertEqual(dag.liberados(dag.DAG_TRILHA, {}), ["D1"])


class Evidencias(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = Path(self.tmp.name) / "evidencias.jsonl"
        for n in range(5):
            evidencias.registrar(self.log, {"no": "D%d" % n, "nivel": 1, "texto": "ação"})

    def tearDown(self):
        self.tmp.cleanup()

    def _linhas(self):
        return self.log.read_text(encoding="utf-8").splitlines()

    def _gravar(self, linhas):
        self.log.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    def test_cadeia_integra(self):
        ok, _, ultimo = evidencias.verificar_cadeia(self.log)
        self.assertTrue(ok)
        self.assertEqual(ultimo, evidencias.ler(self.log)[-1]["hash"])

    def test_vazio_ou_ausente_reprova(self):
        self.assertFalse(evidencias.verificar_cadeia(Path(self.tmp.name) / "nao-existe.jsonl")[0])

    def test_qualquer_alteracao_e_detectada(self):
        rng = random.Random(7)
        original = self._linhas()
        for _ in range(50):
            linhas = list(original)
            alvo = rng.randrange(len(linhas))
            registro = json.loads(linhas[alvo])
            campo = rng.choice(["no", "nivel", "texto", "hash_anterior", "seq"])
            registro[campo] = "%s-x" % registro[campo]
            linhas[alvo] = json.dumps(registro, ensure_ascii=False, sort_keys=True)
            self._gravar(linhas)
            self.assertFalse(evidencias.verificar_cadeia(self.log)[0], "alteração não detectada em %s" % campo)

    def test_remocao_e_reordenacao_sao_detectadas(self):
        original = self._linhas()
        self._gravar(original[:2] + original[3:])
        self.assertFalse(evidencias.verificar_cadeia(self.log)[0])
        self._gravar([original[1], original[0]] + original[2:])
        self.assertFalse(evidencias.verificar_cadeia(self.log)[0])

    def test_truncar_o_fim_muda_o_ultimo_hash(self):
        _, _, antes = evidencias.verificar_cadeia(self.log)
        self._gravar(self._linhas()[:-1])
        ok, _, depois = evidencias.verificar_cadeia(self.log)
        self.assertTrue(ok)  # a cadeia sozinha não percebe: por isso existe a âncora externa
        self.assertNotEqual(antes, depois)


if __name__ == "__main__":
    unittest.main()
