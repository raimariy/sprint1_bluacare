"""
moderation.py

Detecta tentativas de jailbreak e conteúdo inadequado.
Protege o sistema de manipulação de prompt e uso indevido.
"""

import re
from dataclasses import dataclass


@dataclass
class ResultadoModeracao:
    """Resultado da moderação de conteúdo."""
    aprovado: bool
    tipo_violacao: str | None
    resposta_sugerida: str | None


# Padrões de jailbreak
PADROES_JAILBREAK = [
    r"ignore (suas|as) instru[cç][õo]es",
    r"esqueça (tudo|suas|as) (instru[cç][õo]es|regras)",
    r"você (agora |é |será )?(um |uma )?(médico|doutor|dr\.?)",
    r"finja (ser|que é|que você é)",
    r"atue como (um |uma )?médico",
    r"sem (restrições|limites|regras)",
    r"modo (desenvolvedor|dev|deus|irrestrito)",
    r"dan mode|jailbreak|prompt injection",
    r"ignore (o |seu |seus )?(sistema|prompt|instrução)",
]

# Padrões de conteúdo perigoso
PADROES_PERIGOSOS = [
    r"(dosagem|quantidade|dose).{0,30}(matar|overdose|letal|fatal|morte)",
    r"(como|quero|vou).{0,20}(me matar|suicídio|acabar com a minha vida)",
    r"(paracetamol|ibuprofeno).{0,30}(matar|overdose|letal|fatal)",
    r"(matar|overdose|letal).{0,30}(paracetamol|ibuprofeno|remédio)",
    r"pode.{0,10}matar",
]


def moderar_mensagem(mensagem: str) -> ResultadoModeracao:
    """
    Verifica se a mensagem contém tentativas de jailbreak
    ou conteúdo perigoso.

    Args:
        mensagem: texto do usuário

    Returns:
        ResultadoModeracao com resultado da verificação
    """
    mensagem_lower = mensagem.lower()

    # Verifica jailbreak
    for padrao in PADROES_JAILBREAK:
        if re.search(padrao, mensagem_lower):
            return ResultadoModeracao(
                aprovado=False,
                tipo_violacao="jailbreak",
                resposta_sugerida=(
                    "Olá! Sou o BluaAssistente da Care Plus e estou aqui para "
                    "te ajudar com informações de saúde. Não consigo alterar "
                    "meu funcionamento, mas posso te ajudar com triagem de "
                    "sintomas ou agendamento de teleconsultas. "
                    "Como posso te ajudar?"
                ),
            )

    # Verifica conteúdo perigoso
    for padrao in PADROES_PERIGOSOS:
        if re.search(padrao, mensagem_lower):
            return ResultadoModeracao(
                aprovado=False,
                tipo_violacao="conteudo_perigoso",
                resposta_sugerida=(
                    "Percebi que você pode estar passando por um momento difícil. "
                    "Se precisar de apoio emocional, o CVV (Centro de Valorização "
                    "da Vida) está disponível 24h pelo telefone 188 ou "
                    "chat em cvv.org.br. "
                    "Estou aqui se quiser conversar sobre sua saúde."
                ),
            )

    return ResultadoModeracao(
        aprovado=True,
        tipo_violacao=None,
        resposta_sugerida=None,
    )


def aplicar_guardrails(mensagem: str) -> ResultadoModeracao | None:
    """
    Aplica todos os guardrails em sequência.
    Retorna o primeiro problema encontrado ou None se aprovado.

    Args:
        mensagem: texto do usuário

    Returns:
        ResultadoModeracao com violação ou None se aprovado
    """
    resultado = moderar_mensagem(mensagem)
    if not resultado.aprovado:
        return resultado
    return None