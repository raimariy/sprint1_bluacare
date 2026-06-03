"""
triagem.py

Agente especializado em triagem clínica.
Coleta sintomas, analisa dados de wearables e detecta red flags.
"""

import os
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

# Prompt especializado do agente de triagem
PROMPT_TRIAGEM = """
Você é o agente de TRIAGEM CLÍNICA do BluaDiagnostics.
Responda SEMPRE em português brasileiro, sem exceções, independentemente do idioma da pergunta.

Sua função exclusiva é:
1. Coletar sintomas do beneficiário de forma estruturada (uma pergunta por vez)
2. Analisar dados de wearables quando fornecidos (SpO2, FC, temperatura)
3. Detectar red flags clínicas que exigem escalada imediata
4. Classificar a urgência: rotina | urgente | emergencia

REGRAS INEGOCIÁVEIS:
- NUNCA faça diagnóstico definitivo
- NUNCA prescreva medicamentos
- Se detectar red flag → retorne JSON com escalada_necessaria: true IMEDIATAMENTE
- Faça apenas UMA pergunta por vez
- NUNCA repita uma pergunta que já foi feita no histórico da conversa
- NUNCA repita o que o usuário acabou de dizer como resposta

RED FLAGS (escalar imediatamente):
- Dor no peito com irradiação para braço/mandíbula
- Falta de ar em repouso ou SpO2 < 90%
- Fraqueza/dormência súbita em um lado do corpo
- Alteração súbita de fala
- Perda de consciência
- Convulsão ativa

FORMATO DE RESPOSTA (sempre JSON válido, sem markdown):
{
  "mensagem_usuario": "texto empático para o usuário em português",
  "sintomas_coletados": ["lista", "de", "sintomas"],
  "red_flag_detectada": true | false,
  "escalada_necessaria": true | false,
  "urgencia": "rotina | urgente | emergencia",
  "proxima_pergunta": "próxima pergunta de triagem ou null se encerrado"
}
"""


def agente_triagem(mensagem: str, historico: list = [], contexto_rag: str = "") -> dict:
    """
    Executa o agente de triagem clínica.

    Args:
        mensagem: mensagem atual do usuário
        historico: histórico da conversa
        contexto_rag: documentos relevantes recuperados pelo RAG

    Returns:
        Dicionário com resultado estruturado da triagem
    """
    llm = ChatOpenAI(
        model="gpt-oss:20b-cloud",
        api_key=OLLAMA_API_KEY,
        base_url="https://ollama.com/v1",
        temperature=0.2,
        max_tokens=1024,
    )

    # Monta o contexto com RAG se disponível
    contexto = ""
    if contexto_rag:
        contexto = f"\n\n[Contexto clínico relevante da base de conhecimento]:\n{contexto_rag}"

    # Monta as mensagens
    mensagens = [SystemMessage(content=PROMPT_TRIAGEM + contexto)]

    # Adiciona histórico (garante que o agente lembre o que já foi perguntado)
    for msg in historico:
        if msg["role"] == "user":
            mensagens.append(HumanMessage(content=msg["content"]))
        else:
            from langchain_core.messages import AIMessage
            mensagens.append(AIMessage(content=msg["content"]))

    # Adiciona mensagem atual
    mensagens.append(HumanMessage(content=mensagem))

    try:
        resposta = llm.invoke(mensagens)
        conteudo = resposta.content

        # Tenta extrair JSON da resposta
        try:
            conteudo_limpo = conteudo.strip()
            if "```json" in conteudo_limpo:
                conteudo_limpo = conteudo_limpo.split("```json")[1].split("```")[0]
            elif "```" in conteudo_limpo:
                conteudo_limpo = conteudo_limpo.split("```")[1].split("```")[0]

            resultado = json.loads(conteudo_limpo)
        except json.JSONDecodeError:
            resultado = {
                "mensagem_usuario": conteudo,
                "sintomas_coletados": [],
                "red_flag_detectada": False,
                "escalada_necessaria": False,
                "urgencia": "rotina",
                "proxima_pergunta": None,
            }

    except Exception as e:
        resultado = {
            "mensagem_usuario": f"Desculpe, ocorreu um erro. Tente novamente. ({str(e)[:100]})",
            "sintomas_coletados": [],
            "red_flag_detectada": False,
            "escalada_necessaria": False,
            "urgencia": "rotina",
            "proxima_pergunta": None,
        }

    return resultado