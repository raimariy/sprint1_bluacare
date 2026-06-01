"""
schemas.py

Centraliza os JSON Schemas de todas as tools do BluaDiagnostics.
Usado para documentação, validação e function calling.
"""

# Schema da tool: consultar_historico_paciente
SCHEMA_CONSULTAR_HISTORICO = {
    "type": "function",
    "function": {
        "name": "consultar_historico_paciente",
        "description": (
            "Retorna o histórico clínico do beneficiário Care Plus: "
            "nome, idade, comorbidades, medicações em uso, últimas "
            "consultas e exames recentes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "paciente_id": {
                    "type": "string",
                    "description": "ID do beneficiário na rede Care Plus (ex: 'CP-00123')",
                },
                "janela_meses": {
                    "type": "integer",
                    "description": "Janela retroativa em meses. Default: 12.",
                    "default": 12,
                    "minimum": 1,
                    "maximum": 60,
                },
            },
            "required": ["paciente_id"],
        },
    },
}

# Schema da tool: verificar_interacoes_medicamentosas
SCHEMA_VERIFICAR_INTERACOES = {
    "type": "function",
    "function": {
        "name": "verificar_interacoes_medicamentosas",
        "description": (
            "Verifica interações entre medicamentos em uso e um novo "
            "medicamento. Retorna severidade (nenhuma/leve/moderada/grave) "
            "e recomendações clínicas."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "medicamentos_em_uso": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de medicamentos que o paciente já usa",
                    "minItems": 1,
                },
                "novo_medicamento": {
                    "type": "string",
                    "description": "Medicamento a verificar (ex: 'Ibuprofeno 400mg')",
                },
            },
            "required": ["medicamentos_em_uso", "novo_medicamento"],
        },
    },
}

# Schema da tool: agendar_teleconsulta
SCHEMA_AGENDAR_TELECONSULTA = {
    "type": "function",
    "function": {
        "name": "agendar_teleconsulta",
        "description": (
            "Agenda uma teleconsulta na especialidade indicada. "
            "Use quando o usuário solicitar agendamento ou quando "
            "a triagem indicar necessidade de consulta."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "paciente_id": {
                    "type": "string",
                    "description": "ID do beneficiário na rede Care Plus",
                },
                "especialidade": {
                    "type": "string",
                    "enum": [
                        "clinica_geral",
                        "cardiologia",
                        "dermatologia",
                        "pediatria",
                        "ginecologia",
                        "psiquiatria",
                        "ortopedia",
                        "oftalmologia",
                    ],
                    "description": "Especialidade médica para o agendamento",
                },
                "urgencia": {
                    "type": "string",
                    "enum": ["rotina", "urgente", "emergencia"],
                    "description": (
                        "'rotina' = até 5 dias | "
                        "'urgente' = mesmo dia | "
                        "'emergencia' = imediato"
                    ),
                },
                "motivo": {
                    "type": "string",
                    "description": "Breve descrição do motivo da consulta (opcional)",
                },
            },
            "required": ["paciente_id", "especialidade", "urgencia"],
        },
    },
}

# Lista com todos os schemas — útil para registrar tools no LLM
TODAS_AS_TOOLS = [
    SCHEMA_CONSULTAR_HISTORICO,
    SCHEMA_VERIFICAR_INTERACOES,
    SCHEMA_AGENDAR_TELECONSULTA,
]