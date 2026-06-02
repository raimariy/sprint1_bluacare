"""
red_flags.py

Detecta red flags clínicas na mensagem do usuário.
Camada de segurança independente do LLM — baseada em regras.
Executa ANTES de qualquer chamada ao modelo.
"""

import re
from dataclasses import dataclass


@dataclass
class ResultadoRedFlag:
    """Resultado da verificação de red flag."""
    detectada: bool
    categoria: str | None
    descricao: str | None
    nivel_urgencia: str  # "emergencia" | "urgente" | "rotina"


# Padrões por categoria clínica
PADROES_RED_FLAG = {
    "cardiaco": {
        "nivel": "emergencia",
        "descricao": "Possível síndrome coronariana aguda",
        "padroes": [
            r"dor.{0,25}peito.{0,40}(bra[cç]o|mandíbula|costas|pescoço)",
            r"(bra[cç]o|mandíbula).{0,40}dor.{0,25}peito",
            r"dor.{0,20}peito.{0,30}(suor|falta de ar|tontura)",
            r"aperto.{0,20}(peito|tórax)",
            r"infarto",
        ],
    },
    "neurologico": {
        "nivel": "emergencia",
        "descricao": "Possível AVC ou emergência neurológica",
        "padroes": [
            r"(rosto|face).{0,20}(caiu|caído|torto|paralis)",
            r"(bra[cç]o|perna).{0,20}(fraco|dormeu|paralis).{0,15}(repente|súbit)",
            r"não consigo (falar|me expressar|formar)",
            r"fala.{0,15}(embaralhad|estranha|mudou)",
            r"(pior|maior|terrível).{0,15}dor de cabe[cç]a.{0,15}(vida|sempre|já)",
            r"perdi.{0,10}(consciência|os sentidos)",
            r"avc|derrame",
        ],
    },
    "respiratorio": {
        "nivel": "emergencia",
        "descricao": "Comprometimento respiratório grave",
        "padroes": [
            r"spo2.{0,15}(8[0-9]|9[01])\b",
            r"saturação.{0,15}(8[0-9]|9[01])\b",
            r"(8[0-9]|9[01]).{0,10}(spo2|saturação)",
            r"caiu.{0,15}(8[0-9])\b",
            r"falta de ar.{0,20}repous",
            r"não consigo (respirar|pegar ar)",
            r"sufocando|sufocamento",
            r"lábios? (azul|roxa|liláz)",
        ],
    },
    "outros": {
        "nivel": "emergencia",
        "descricao": "Situação de emergência",
        "padroes": [
            r"convuls",
            r"sangramento.{0,20}(não para|intenso|muito)",
            r"overdose|intoxica[cç]ão",
            r"(engasgou|engasgando).{0,20}(não respira|azul)",
            r"anafilax|alergia.{0,20}(grave|severa|falta de ar)",
        ],
    },
}


def verificar_red_flag(mensagem: str) -> ResultadoRedFlag:
    """
    Verifica se a mensagem contém red flags clínicas.

    Args:
        mensagem: texto do usuário

    Returns:
        ResultadoRedFlag com resultado da verificação
    """
    mensagem_lower = mensagem.lower()

    for categoria, config in PADROES_RED_FLAG.items():
        for padrao in config["padroes"]:
            if re.search(padrao, mensagem_lower):
                return ResultadoRedFlag(
                    detectada=True,
                    categoria=categoria,
                    descricao=config["descricao"],
                    nivel_urgencia=config["nivel"],
                )

    return ResultadoRedFlag(
        detectada=False,
        categoria=None,
        descricao=None,
        nivel_urgencia="rotina",
    )