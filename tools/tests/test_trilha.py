"""Testes do orquestrador: o que ele recusa e o que ele garante."""
import tempfile
import unittest
from pathlib import Path

from tools import auditar, estado as est, evidencias, exemplo, trilha

P = exemplo.PROPOSTAS


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name) / "projeto"

    def tearDown(self):
        self.tmp.cleanup()

    def iniciar(self):
        trilha.iniciar(self.pasta, "exemplo-ficticio", "Teste", ficticio=True)

    def definicao(self):
        self.iniciar()
        for no in ("D1", "D2", "D3", "D4", "D5"):
            trilha.aplicar(self.pasta, no, P[no])

    def estado(self):
        return est.carregar(self.pasta)

    def no(self, ident):
        return next((n for n in self.estado()["execucao"]["nos"] if n["id"] == ident), {})


class Ordem(Base):
    def test_comeca_em_d1(self):
        self.iniciar()
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aplicar(self.pasta, "D2", P["D2"])
        resposta = trilha.aplicar(self.pasta, "D1", P["D1"])
        self.assertEqual(resposta["liberados"], ["D2"])

    def test_no_de_outra_etapa_e_recusado(self):
        self.iniciar()
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aplicar(self.pasta, "B2", P["B2"])

    def test_portao_sem_verificacao_e_recusado(self):
        self.definicao()
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aprovar(self.pasta, "G1", "Gerente")
        self.assertEqual(self.estado()["projeto"]["etapa_atual"], "definicao")

    def test_aprovacao_exige_nome(self):
        self.definicao()
        trilha.verificar(self.pasta, "V1")
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aprovar(self.pasta, "G1", "  ")

    def test_ja_existe_projeto(self):
        self.iniciar()
        with self.assertRaises(trilha.ErroTrilha):
            self.iniciar()


class Protecao(Base):
    def test_agente_nao_grava_resultado_documento_nem_execucao(self):
        self.iniciar()
        for bloco in ("resultados", "documentos", "execucao"):
            with self.assertRaises(trilha.ErroTrilha):
                trilha.aplicar(self.pasta, "D1", {bloco: []})

    def test_agente_nao_muda_etapa_nem_marca_de_ficticio(self):
        self.iniciar()
        for campo, valor in (("etapa_atual", "mensuracao"), ("ficticio", False), ("id", "outro")):
            with self.assertRaises(trilha.ErroTrilha):
                trilha.aplicar(self.pasta, "D1", {"projeto": {campo: valor}})

    def test_proposta_vazia_e_recusada(self):
        self.iniciar()
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aplicar(self.pasta, "D1", {})

    def test_projeto_real_dentro_do_repositorio_e_recusado(self):
        dentro = trilha.RAIZ / "projetos" / "nao-criar-este-teste"
        with self.assertRaises(trilha.ErroTrilha):
            trilha.iniciar(dentro, "real", "Real", ficticio=False)
        self.assertFalse(dentro.exists())

    def test_projeto_real_fora_do_repositorio_e_aceito(self):
        trilha.iniciar(self.pasta, "real", "Real", ficticio=False)
        self.assertFalse(self.estado()["projeto"]["ficticio"])


class Verificacao(Base):
    def test_verificacao_reprovada_bloqueia_o_portao(self):
        self.iniciar()
        for no in ("D1", "D2", "D3", "D4"):
            trilha.aplicar(self.pasta, no, P[no])
        trilha.aplicar(self.pasta, "D5", {"papeis": {"projeto": "Gerente do Projeto"}})
        falhas = trilha.verificar(self.pasta, "V1")
        self.assertTrue({"C1", "C6"} <= {f["regra"] for f in falhas})
        self.assertEqual(self.no("V1")["estado"], "falhou")
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aprovar(self.pasta, "G1", "Gerente")
        trilha.aplicar(self.pasta, "D5", P["D5"])
        self.assertEqual(trilha.verificar(self.pasta, "V1"), [])
        trilha.aprovar(self.pasta, "G1", "Gerente")
        self.assertEqual(self.estado()["projeto"]["etapa_atual"], "monitoramento")

    def test_retrabalho_invalida_a_verificacao(self):
        self.definicao()
        trilha.verificar(self.pasta, "V1")
        resposta = trilha.aplicar(self.pasta, "D4", {"indicadores": [{"id": "IND-1", "meta": {"valor": "6"}}]})
        self.assertEqual(resposta["invalidados"], ["V1"])
        self.assertEqual(self.no("V1")["estado"], "invalidado")
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aprovar(self.pasta, "G1", "Gerente")

    def test_numero_sem_origem_nao_passa(self):
        self.definicao()
        trilha.aplicar(self.pasta, "D4", {"indicadores": [{"id": "IND-1", "meta": {"valor": "6", "origem": "agente"}}]})
        self.assertIn("I3", {f["regra"] for f in trilha.verificar(self.pasta, "V1")})

    def test_meta_com_plano_passa_em_v1_mas_nao_em_v2(self):
        self.definicao()
        so_plano = {"plano": {"como": "O responsável pelo benefício define", "data": "2026-02-28"}}
        with self.assertRaises(trilha.ErroTrilha):  # já havia valor: valor e plano juntos são recusados
            trilha.aplicar(self.pasta, "D4", {"indicadores": [{"id": "IND-2", "meta": so_plano}]})
        plano = dict(so_plano, valor=None)
        trilha.aplicar(self.pasta, "D4", {"indicadores": [{"id": "IND-2", "meta": plano}]})
        self.assertEqual(trilha.verificar(self.pasta, "V1"), [])
        self.assertIn("a definir até 2026-02-28", trilha.previa(self.pasta, "proposta_de_valor"))
        trilha.aplicar(self.pasta, "D4", {"indicadores": [{"id": "IND-1", "meta": plano}]})
        self.assertEqual(trilha.verificar(self.pasta, "V1"), [])
        trilha.aprovar(self.pasta, "G1", "Gerente")
        for no in ("M1", "M2", "M3", "M4", "M5"):
            trilha.aplicar(self.pasta, no, P[no])
        motivos = [f["motivo"] for f in trilha.verificar(self.pasta, "V2")]
        self.assertTrue(any("meta precisa estar definida" in m for m in motivos), motivos)

    def test_meta_ausente_reprova_com_mensagem_util(self):
        self.definicao()
        trilha.aplicar(self.pasta, "D4", {"indicadores": [{"id": "IND-2", "meta": None}]})
        motivos = [f["motivo"] for f in trilha.verificar(self.pasta, "V1")]
        self.assertTrue(any("plano com 'como' e 'data'" in m for m in motivos), motivos)

    def test_proposta_malformada_e_recusada_na_hora(self):
        self.definicao()
        ruins = [
            {"bloco_inventado": 1},
            {"anotacoes": ["texto solto"]},
            {"indicadores": [{"id": "IND-2", "situacao": "suspenso"}]},
            {"indicadores": [{"id": "IND-2", "tipo": "financeiro"}]},
            {"indicadores": [{"id": "IND-2", "meta": {"plano": {"como": "sem data"}}}]},
            {"indicadores": [{"id": "IND-2", "meta": "80"}]},
            {"premissas": [{"id": "PRE-1", "situacao": "talvez"}]},
            {"premissas": [{"id": "PRE-1", "criada_por": "sistema"}]},
            {"anotacoes": [{"id": "NOTA-5", "no": "D4", "texto": "sem autoria"}]},
            {"riscos": [{"id": "RIS-1", "tipo": "risco", "descricao": "sem autoria"}]},
            {"decisoes": [{"id": "DEC-9", "tipo": "outra", "descricao": "x", "redacao": "assistente"}]},
            {"premissas": [{"id": "PRE-9", "texto": "sem criada_por", "situacao": "aberta"}]},
            {"transicao": {"data": "2026-06-30"}},
            {"anotacoes": [{"id": "NOTA-5", "no": "D4", "texto": "x", "redacao": "assistente"}]},
            {"nao_medidos": [{"id": "NM-9", "indicador": "IND-2", "motivo": "sem data"}]},
        ]
        antes = self.estado()
        for proposta in ruins:
            with self.assertRaises(trilha.ErroTrilha, msg=str(proposta)):
                trilha.aplicar(self.pasta, "D4", proposta)
        self.assertEqual(self.estado(), antes)

    def test_previa_marca_rascunho_antes_da_verificacao(self):
        self.definicao()
        self.assertTrue(trilha.previa(self.pasta, "proposta_de_valor").startswith("> RASCUNHO"))
        trilha.verificar(self.pasta, "V1")
        self.assertFalse(trilha.previa(self.pasta, "proposta_de_valor").startswith("> RASCUNHO"))

    def test_mostrar(self):
        self.definicao()
        self.assertIn('"IND-1"', trilha.mostrar(self.pasta, "indicadores"))
        self.assertEqual(trilha.mostrar(self.pasta, "licoes"), "[]")
        with self.assertRaises(trilha.ErroTrilha):
            trilha.mostrar(self.pasta, "nao_existe")
        trilha.aplicar(self.pasta, "D4", {"indicadores": [{"id": "IND-2", "meta": {
            "valor": None, "plano": {"como": "definir", "data": "2000-01-01"}}}]})
        self.assertIn("ATENÇÃO: o plano de meta do IND-2 venceu", trilha.status(self.pasta))
        trilha.aplicar(self.pasta, "D5", {"anotacoes": [{"redacao": "pessoa", "id": "NOTA-7", "no": "D5", "texto": "Fontes acessíveis."}]})
        self.assertIn("- Fontes acessíveis.", trilha.previa(self.pasta, "proposta_de_valor"))
        trilha.aplicar(self.pasta, "D5", {"anotacoes": [{"id": "NOTA-8", "no": "D5", "texto": "Resumo do assistente.",
                                                         "redacao": "assistente", "confirmado_por": "Ana (fictícia)"}]})
        texto = trilha.previa(self.pasta, "proposta_de_valor")
        self.assertIn("- Resumo do assistente. *(redação do assistente, confirmada por Ana (fictícia))*", texto)
        self.assertIn("presumida pelo assistente", texto)

    def test_mesclar_por_id_preserva_os_demais_campos(self):
        self.definicao()
        ind = self.estado()["indicadores"][0]
        self.assertEqual(ind["nome"], "Tempo de fechamento mensal")
        self.assertEqual(ind["meta"]["valor"], "7")
        self.assertEqual(len(self.estado()["indicadores"]), 2)


class PontaAPonta(Base):
    def setUp(self):
        super().setUp()
        self.ultimo = exemplo.gerar(self.pasta)

    def test_auditoria_aprova(self):
        relatorio = auditar.auditar(self.pasta, ancora=self.ultimo)
        self.assertTrue(relatorio["aprovado"], relatorio["falhas"])
        e = self.estado()
        self.assertEqual(e["projeto"]["etapa_atual"], "sustentacao")
        self.assertEqual([d["tipo"] for d in e["documentos"]],
                         ["proposta_de_valor", "relatorio_monitoramento", "relatorio_beneficios"])
        self.assertEqual(e["resultados"][0]["realizacao"], "2/3")

    def test_relatorio_traz_o_resultado_da_calculadora(self):
        texto = (self.pasta / "03-mensuracao/relatorio-beneficios-v1.md").read_text(encoding="utf-8")
        self.assertIn("| Tempo de fechamento mensal | 10 | 7 | 8 em 2026-07-31 | 2/3 (67%) | parcial |", texto)

    def test_todo_registro_traz_modelo_e_hash_do_estado(self):
        for registro in evidencias.ler(self.pasta / est.ARQUIVO_EVIDENCIAS):
            self.assertIn("modelo", registro["ator"])
            self.assertIn("estado_sha256", registro)

    def test_etapa_aprovada_nao_aceita_alteracao(self):
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aplicar(self.pasta, "D4", {"indicadores": [{"id": "IND-1", "meta": {"valor": "9"}}]})

    def test_nova_medicao_refaz_o_calculo(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        for no in ("B1", "B2", "B3"):
            trilha.aplicar(outra, no, P[no])
        trilha.calcular(outra)
        resposta = trilha.aplicar(outra, "B2", {"medicoes": [dict(P["B2"]["medicoes"][0], valor="7")]})
        self.assertEqual(resposta["invalidados"], ["B4"])
        self.assertEqual(est.carregar(outra)["resultados"], [])
        self.assertEqual(trilha.calcular(outra)[0]["classificacao"], "realizado")

    def test_resultado_sem_decisao_reprova_v3(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        for no in ("B1", "B2", "B3"):
            trilha.aplicar(outra, no, P[no])
        trilha.calcular(outra)
        trilha.aplicar(outra, "B5", {"anotacoes": [{"redacao": "pessoa", "id": "NOTA-9", "no": "B5", "texto": "sem decisão"}]})
        self.assertIn("B5", {f["regra"] for f in trilha.verificar(outra, "V3")})

    def test_indicador_de_resultado_sem_medicao_exige_motivo(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        trilha.aplicar(outra, "B1", P["B1"])
        trilha.aplicar(outra, "B2", {"anotacoes": [{"redacao": "pessoa", "id": "NOTA-9", "no": "B2", "texto": "sem dado"}]})
        with self.assertRaises(trilha.ErroTrilha):
            trilha.calcular(outra)

    def test_nao_medido_aparece_no_relatorio(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        trilha.aplicar(outra, "B1", P["B1"])
        trilha.aplicar(outra, "B2", dict(P["B2"], nao_medidos=[{
            "id": "NM-3", "indicador": "IND-2", "data": "2026-07-31", "motivo": "Relatório não extraído.",
            "redacao": "assistente", "confirmado_por": "Ana (fictícia)",
            "plano": "Extrair até 2026-08-15"}]))
        trilha.aplicar(outra, "B3", P["B3"])
        trilha.calcular(outra)
        self.assertIn("linha de base 10, meta 7, resultado 8", trilha.calcular.detalhes[0])
        trilha.aplicar(outra, "B5", P["B5"])
        self.assertEqual(trilha.verificar(outra, "V3"), [])
        texto = trilha.previa(outra, "relatorio_beneficios")
        self.assertIn("## Indicadores não medidos", texto)
        self.assertIn("| IND-2 | 2026-07-31 | Relatório não extraído. | Extrair até 2026-08-15 |", texto)
        self.assertIn("*Redação do assistente, confirmada pela pessoa indicada: NM-3 (Ana (fictícia)).*", texto)
        self.assertIn("Como ler este documento", texto)

    def test_premissa_contrariada_aparece_no_relatorio(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        trilha.aplicar(outra, "B1", {"premissas": [{"id": "PRE-1", "situacao": "contrariada"}]})
        self.assertIn("PRE-1 (CONTRARIADA, presumida pelo assistente)", trilha.previa(outra, "relatorio_beneficios"))

    def test_sustentacao_transversal_ate_o_encerramento(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="definicao")
        with self.assertRaises(trilha.ErroTrilha):  # transição só depois do Monitoramento
            trilha.aplicar(outra, "S2", P["S2"])
        trilha.aplicar(outra, "S1", P["S1"])  # papéis: liberado desde a Proposta aprovada
        self.assertEqual(est.carregar(outra)["projeto"]["etapa_atual"], "monitoramento")

        ultimo = exemplo.gerar(outra, ate="sustentacao")
        e = est.carregar(outra)
        self.assertEqual(e["projeto"]["etapa_atual"], "encerrado")
        self.assertEqual([d["tipo"] for d in e["documentos"]],
                         ["proposta_de_valor", "relatorio_monitoramento", "termo_transicao", "relatorio_beneficios",
                          "licoes_aprendidas"])
        relatorio = auditar.auditar(outra, ancora=ultimo)
        self.assertTrue(relatorio["aprovado"], relatorio["falhas"])
        with self.assertRaises(trilha.ErroTrilha):  # encerrado não aceita mais nada
            trilha.aplicar(outra, "S1", P["S1"])

    def test_aceite_da_transicao_nao_muda_a_etapa(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        trilha.aplicar(outra, "S2", {"transicao": {"data": "2026-06-30", "redacao": "pessoa"}})
        regras = [f["item"] for f in trilha.verificar(outra, "VT")]
        self.assertIn("transicao.recebido_por", regras)
        trilha.aplicar(outra, "S2", P["S2"])
        self.assertEqual(trilha.verificar(outra, "VT"), [])
        with self.assertRaises(trilha.ErroTrilha):  # o aceite precisa dizer de qual papel
            trilha.aprovar(outra, "GT", "Gerente de Controladoria")
        with self.assertRaises(trilha.ErroTrilha):  # ainda não há Termo
            trilha.aceitar(outra, "governanca", "Escritório de Projetos")
        trilha.aprovar(outra, "GT", "Ana (fictícia)", em_nome_de="Gerente de Controladoria", papel="beneficio")
        termo = est.carregar(outra)["documentos"][-1]
        self.assertEqual((termo["aprovado_por"], termo["em_nome_de"]), ("Ana (fictícia)", "Gerente de Controladoria"))
        self.assertIn("aceite do responsável pela governança", trilha.status(outra))
        self.assertIn("aceite 1/2", trilha.status(outra))
        with self.assertRaises(trilha.ErroTrilha):  # mesmo papel duas vezes
            trilha.aceitar(outra, "beneficio", "Outra")
        trilha.aceitar(outra, "governanca", "Escritório de Projetos")
        self.assertNotIn("aceite do responsável pela governança", trilha.status(outra))
        self.assertTrue(auditar.auditar(outra)["aprovado"])
        self.assertEqual(est.carregar(outra)["projeto"]["etapa_atual"], "mensuracao")
        self.assertIn("Quem assume o acompanhamento: Gerente de Controladoria",
                      (outra / "04-sustentacao/termo-transicao-v1.md").read_text(encoding="utf-8"))

    def test_licao_sem_acao_e_catalogo_incompleto_reprovam_v4(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="mensuracao")
        for no in ("S1", "S2"):
            trilha.aplicar(outra, no, P[no])
        trilha.verificar(outra, "VT")
        trilha.aprovar(outra, "GT", "Gerente", papel="beneficio")
        trilha.aplicar(outra, "S3", {"licoes": [{"id": "LIC-1", "etapa": "mensuracao", "licao": "Algo", "redacao": "pessoa"}]})
        trilha.aplicar(outra, "S4", {"catalogo": [P["S4"]["catalogo"][0]]})
        falhas = trilha.verificar(outra, "V4")
        self.assertEqual({f["regra"] for f in falhas}, {"S2", "S3", "S4"})
        self.assertIn("aceite.governanca", [f["item"] for f in falhas])
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aprovar(outra, "G4", "Gerente")

    def test_leituras_acumulam_por_id(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="definicao")
        for no in ("M1", "M2"):
            trilha.aplicar(outra, no, P[no])
        trilha.aplicar(outra, "M2", {"monitoramento": {"leituras": [
            {"id": "LEI-2", "indicador": "IND-2", "data": "2026-07-31", "valor": "70", "origem": "pessoa",
             "informado_por": "Coordenador de Contabilidade"}]}})
        e = est.carregar(outra)
        self.assertEqual([l["id"] for l in e["monitoramento"]["leituras"]], ["LEI-1", "LEI-2"])
        self.assertEqual(e["monitoramento"]["cadencia"]["revisao_valor"], "mensal")

    def test_medicao_prevista_sem_registro_reprova_v3(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        trilha.aplicar(outra, "B1", P["B1"])
        trilha.aplicar(outra, "B2", {"medicoes": P["B2"]["medicoes"][:1]})
        trilha.aplicar(outra, "B3", P["B3"])
        trilha.calcular(outra)
        trilha.aplicar(outra, "B5", P["B5"])
        motivos = [f["motivo"] for f in trilha.verificar(outra, "V3")]
        self.assertEqual(len([m for m in motivos if "não foi realizada nem justificada" in m]), 2, motivos)

    def test_relatorio_so_depois_da_ultima_medicao_prevista(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        for no in ("B1", "B2", "B3"):
            trilha.aplicar(outra, no, P[no])
        trilha.calcular(outra)
        trilha.aplicar(outra, "B5", P["B5"])
        cedo = trilha.verificar(outra, "V3", momento="2026-08-10T12:00:00+00:00")
        self.assertEqual(len([f for f in cedo if "só é aprovado depois da última medição" in f["motivo"]]), 1, cedo)
        with self.assertRaises(trilha.ErroTrilha):
            trilha.aprovar(outra, "G3", "Gerente", momento="2026-08-10T12:00:00+00:00")
        self.assertEqual(trilha.verificar(outra, "V3", momento="2026-10-05T12:00:00+00:00"), [])
        trilha.aprovar(outra, "G3", "Gerente", momento="2026-10-05T12:00:00+00:00")
        e = est.carregar(outra)
        self.assertEqual([r["realizacao"] for r in e["resultados"]], ["2/3", "2/3", "1"])
        self.assertEqual([r["classificacao"] for r in e["resultados"]], ["parcial", "parcial", "realizado"])

    def test_mudanca_de_escopo_exige_o_gatilho(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="definicao")
        for no in ("M1", "M2", "M3"):
            trilha.aplicar(outra, no, P[no])
        sem = dict(P["M4"]["decisoes"][0]); sem.pop("gatilho")
        trilha.aplicar(outra, "M4", {"decisoes": [sem]})
        trilha.aplicar(outra, "M5", P["M5"])
        self.assertIn("M4", {f["regra"] for f in trilha.verificar(outra, "V2")})
        trilha.aplicar(outra, "M4", {"decisoes": [{"id": "DEC-1", "gatilho": {
            "altera_valor": True, "novas_dependencias": False, "alinhada": True}}]})
        self.assertIn("M4", {f["regra"] for f in trilha.verificar(outra, "V2")})  # altera valor, mas 'afeta' vazio
        trilha.aplicar(outra, "M4", P["M4"])
        self.assertEqual(trilha.verificar(outra, "V2"), [])

    def test_avisos_de_datas_vencidas_e_transicao_pendente(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        texto = trilha.status(outra)
        self.assertIn("ATENÇÃO: a medição do IND-1 prevista para 2026-07-31 já passou", texto)
        self.assertIn("ATENÇÃO: o risco RIS-1 tinha prazo em 2026-07-31", texto)
        self.assertIn("a transição para a operação ainda não foi aceita", texto)
        trilha.aplicar(outra, "S1", {"riscos": [{"id": "RIS-1", "situacao": "concluido"}]})
        self.assertNotIn("RIS-1", trilha.status(outra))

    def test_anotacao_nao_invalida_e_ocorrencia_nao_muda_o_estado(self):
        outra = Path(self.tmp.name) / "outro"
        exemplo.gerar(outra, ate="monitoramento")
        trilha.aplicar(outra, "S2", P["S2"])
        trilha.verificar(outra, "VT")
        r = trilha.aplicar(outra, "S2", {"anotacoes": [{"redacao": "pessoa", "id": "NOTA-8", "no": "S2", "texto": "Transição registrada com atraso."}]})
        self.assertEqual(r["invalidados"], [])
        self.assertIn("Transição registrada com atraso.", trilha.previa(outra, "termo_transicao"))
        antes = est.carregar(outra)
        trilha.ocorrencia(outra, "A pessoa pediu para estimar a adoção; o pedido foi recusado.")
        self.assertEqual(est.carregar(outra), antes)
        ultimo = evidencias.ler(outra / est.ARQUIVO_EVIDENCIAS)[-1]
        self.assertEqual(ultimo["tipo"], "ocorrencia")
        self.assertTrue(auditar.auditar(outra)["aprovado"])
        self.assertEqual(trilha.mostrar(outra, "catalogo"), "[]")
        nova = Path(self.tmp.name) / "novo"
        trilha.iniciar(nova, "exemplo-ficticio", "T")
        self.assertEqual(trilha.mostrar(nova, "monitoramento"), "{}")

    def test_linha_de_comando(self):
        self.assertEqual(trilha.main(["mostrar", str(self.pasta), "--bloco", "papeis"]), 0)
        self.assertEqual(trilha.main(["status", str(self.pasta)]), 0)
        self.assertEqual(trilha.main(["previa", str(self.pasta), "--tipo", "relatorio_beneficios"]), 0)
        self.assertEqual(trilha.main(["aprovar", str(self.pasta), "--portao", "G4", "--por", "X"]), 1)


if __name__ == "__main__":
    unittest.main()
