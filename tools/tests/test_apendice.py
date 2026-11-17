import unittest

from tools import apendice


class Apendice(unittest.TestCase):
    def test_tabela_traz_os_cinco_documentos_e_secoes_do_codigo(self):
        t = apendice.tabela_documentos()
        for titulo in ("Proposta de Valor do Projeto", "Relatório de Monitoramento de Valor",
                       "Termo de Transição para a Operação", "Relatório de Benefícios", "Registro de Lições Aprendidas"):
            self.assertIn(titulo, t)
        for secao in ("Matriz RACI", "Cadência", "Quadro comparativo", "Lições e ações", "Calendário de medição"):
            self.assertIn(secao, t)
        self.assertIn("Indicadores não medidos (quando houver)", t)
        self.assertIn("quem assume o acompanhamento", t)

    def test_exemplo_usa_a_calculadora(self):
        t = apendice.tabela_exemplo()
        self.assertIn("| 1 | 10 | 7 | 8 | 67% | parcial |", t)
        self.assertIn("| 3 | 10 | 7 | 7 | 100% | realizado |", t)

    def test_secoes_nao_repetem(self):
        for _, tipo, _m in apendice.DOCUMENTOS:
            s = [x.replace(" (quando houver)", "") for x in apendice.secoes(tipo)]
            self.assertEqual(len(s), len(set(s)), tipo)


if __name__ == "__main__":
    unittest.main()
