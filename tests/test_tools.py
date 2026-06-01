"""
test_tools.py

Testes unitários das tools do BluaDiagnostics.
Execute: pytest tests/test_tools.py -v

Bônus Sprint 2 — suite de testes unitários.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.tools.consultar_historico_paciente import consultar_historico_paciente
from src.tools.verificar_interacoes_medicamentosas import verificar_interacoes_medicamentosas
from src.tools.agendar_teleconsulta import agendar_teleconsulta


# ============================================================
# TESTES: consultar_historico_paciente
# ============================================================

class TestConsultarHistorico:

    def test_paciente_existente_retorna_dados(self):
        """Paciente CP-00123 deve retornar dados completos."""
        resultado = consultar_historico_paciente("CP-00123")
        assert resultado["status"] == "sucesso"
        assert resultado["nome"] == "Maria Silva"
        assert resultado["idade"] == 34
        assert len(resultado["medicamentos_uso_continuo"]) > 0

    def test_paciente_inexistente_retorna_erro(self):
        """ID inválido deve retornar status de erro."""
        resultado = consultar_historico_paciente("CP-99999")
        assert resultado["status"] == "erro"
        assert "não encontrado" in resultado["mensagem"]

    def test_todos_pacientes_simulados(self):
        """Todos os 3 pacientes simulados devem retornar dados."""
        for pid in ["CP-00123", "CP-00456", "CP-00789"]:
            resultado = consultar_historico_paciente(pid)
            assert resultado["status"] == "sucesso"
            assert "nome" in resultado
            assert "idade" in resultado
            assert "comorbidades" in resultado

    def test_janela_meses_customizada(self):
        """Janela de meses customizada deve ser registrada."""
        resultado = consultar_historico_paciente("CP-00123", janela_meses=6)
        assert resultado["janela_meses"] == 6


# ============================================================
# TESTES: verificar_interacoes_medicamentosas
# ============================================================

class TestVerificarInteracoes:

    def test_losartana_ibuprofeno_moderada(self):
        """Losartana + Ibuprofeno deve retornar interação moderada."""
        resultado = verificar_interacoes_medicamentosas(
            medicamentos_em_uso=["Losartana 50mg"],
            novo_medicamento="Ibuprofeno 400mg",
        )
        assert resultado["status"] == "interacao_encontrada"
        assert resultado["severidade"] == "moderada"

    def test_metformina_dexametasona_grave(self):
        """Metformina + Dexametasona deve retornar interação grave."""
        resultado = verificar_interacoes_medicamentosas(
            medicamentos_em_uso=["Metformina 850mg"],
            novo_medicamento="Dexametasona 4mg",
        )
        assert resultado["status"] == "interacao_encontrada"
        assert resultado["severidade"] == "grave"

    def test_sem_interacao_conhecida(self):
        """Medicamentos sem interação devem retornar sem_interacao."""
        resultado = verificar_interacoes_medicamentosas(
            medicamentos_em_uso=["Vitamina C 500mg"],
            novo_medicamento="Paracetamol 500mg",
        )
        assert resultado["status"] == "sem_interacao"
        assert resultado["severidade"] == "nenhuma"

    def test_retorno_tem_recomendacao(self):
        """Toda interação encontrada deve ter recomendação."""
        resultado = verificar_interacoes_medicamentosas(
            medicamentos_em_uso=["Losartana 50mg"],
            novo_medicamento="Ibuprofeno 400mg",
        )
        assert "recomendacao" in resultado
        assert len(resultado["recomendacao"]) > 0


# ============================================================
# TESTES: agendar_teleconsulta
# ============================================================

class TestAgendarTeleconsulta:

    def test_agendamento_rotina(self):
        """Agendamento de rotina deve retornar status confirmado."""
        resultado = agendar_teleconsulta(
            paciente_id="CP-00123",
            especialidade="clinica_geral",
            urgencia="rotina",
        )
        assert resultado["status"] == "confirmado"
        assert "TC-" in resultado["codigo_consulta"]
        assert "link_acesso" in resultado

    def test_agendamento_urgente(self):
        """Agendamento urgente deve retornar confirmado."""
        resultado = agendar_teleconsulta(
            paciente_id="CP-00123",
            especialidade="cardiologia",
            urgencia="urgente",
        )
        assert resultado["status"] == "confirmado"
        assert resultado["urgencia"] == "urgente"

    def test_especialidade_invalida_retorna_erro(self):
        """Especialidade inválida deve retornar erro."""
        resultado = agendar_teleconsulta(
            paciente_id="CP-00123",
            especialidade="veterinaria",
            urgencia="rotina",
        )
        assert resultado["status"] == "erro"

    def test_urgencia_invalida_retorna_erro(self):
        """Urgência inválida deve retornar erro."""
        resultado = agendar_teleconsulta(
            paciente_id="CP-00123",
            especialidade="clinica_geral",
            urgencia="muito_urgente",
        )
        assert resultado["status"] == "erro"

    def test_motivo_opcional(self):
        """Motivo é opcional — deve funcionar sem ele."""
        resultado = agendar_teleconsulta(
            paciente_id="CP-00123",
            especialidade="clinica_geral",
            urgencia="rotina",
        )
        assert resultado["status"] == "confirmado"