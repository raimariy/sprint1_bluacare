"""
streamlit_app.py

Interface de interação do BluaDiagnostics.
Execute: streamlit run app/streamlit_app.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from src.graph.builder import build_graph, estado_inicial
from src.guardrails.moderation import aplicar_guardrails
from src.guardrails.red_flags import verificar_red_flag

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="BluaDiagnostics",
    page_icon="🩺",
    layout="centered",
)

# ============================================================
# INICIALIZAÇÃO DO ESTADO DA SESSÃO
# ============================================================
if "historico" not in st.session_state:
    st.session_state.historico = []

if "grafo" not in st.session_state:
    st.session_state.grafo = build_graph()

if "escalada_ativada" not in st.session_state:
    st.session_state.escalada_ativada = False

if "paciente_id" not in st.session_state:
    st.session_state.paciente_id = None

# ============================================================
# CABEÇALHO
# ============================================================
st.title("🩺 BluaDiagnostics")
st.caption("Assistente de saúde digital")
st.divider()

# ============================================================
# SIDEBAR — informações e controles
# ============================================================
with st.sidebar:
    st.header("⚙️ Configurações")

    paciente_id = st.text_input(
        "ID do Beneficiário (opcional)",
        placeholder="Ex: CP-00123",
        help="Informe seu ID Care Plus para personalizar o atendimento",
    )
    if paciente_id:
        st.session_state.paciente_id = paciente_id
        st.success(f"Beneficiário: {paciente_id}")

    st.divider()

    st.header("📊 Sessão atual")
    st.metric("Mensagens", len(st.session_state.historico))

    if st.session_state.escalada_ativada:
        st.error("⚠️ Escalada ativada nesta sessão")

    st.divider()

    if st.button("🔄 Nova conversa", use_container_width=True):
        st.session_state.historico = []
        st.session_state.escalada_ativada = False
        st.session_state.paciente_id = None
        st.rerun()

    st.divider()

    st.header("🚨 Emergências")
    st.error("SAMU: **192**")
    st.warning("Bombeiros: **193**")

    st.divider()
    st.caption("BluaDiagnostics v1.0 · Sprint 2\nFIAP Challenge 2026.1")

# ============================================================
# EXIBE HISTÓRICO DA CONVERSA
# ============================================================
if not st.session_state.historico:
    with st.chat_message("assistant"):
        st.markdown(
            "Olá! Sou o **BluaAssistente** 👋\n\n"
            "Estou aqui para te ajudar com:\n"
            "- 🔍 Triagem de sintomas\n"
            "- 💊 Verificação de medicamentos\n"
            "- 📅 Agendamento de teleconsultas\n"
            "- ❓ Dúvidas de saúde\n\n"
            "Como posso te ajudar hoje?"
        )

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================================
# INPUT DO USUÁRIO
# ============================================================
if st.session_state.escalada_ativada:
    st.error(
        "⚠️ Esta conversa foi encerrada por uma situação de emergência. "
        "Clique em **Nova conversa** para iniciar um novo atendimento."
    )
else:
    prompt = st.chat_input("Digite sua mensagem...")

    if prompt:
        # Exibe mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.historico.append({
            "role": "user",
            "content": prompt,
        })

        # Processa a resposta
        with st.chat_message("assistant"):
            with st.spinner("Processando..."):

                # 1. Aplica guardrails
                moderacao = aplicar_guardrails(prompt)

                if moderacao and not moderacao.aprovado:
                    resposta = moderacao.resposta_sugerida
                    agente = "guardrail"
                    rag_usado = False

                else:
                    # 2. Executa pelo grafo
                    try:
                        # ✅ FIX: monta o estado manualmente para incluir o histórico
                        # (sem o histórico, o agente não lembra o que já perguntou
                        #  e acaba repetindo perguntas ou respondendo em inglês)
                        from src.graph.state import BluaState

                        # Histórico EXCLUINDO a mensagem atual (já adicionada acima)
                        # para não duplicar — passamos só as anteriores
                        historico_anterior = st.session_state.historico[:-1]

                        estado = BluaState(
                            mensagem_atual=prompt,
                            historico=historico_anterior,  
                            paciente_id=st.session_state.paciente_id,
                            sintomas_coletados=[],
                            urgencia="rotina",
                            red_flag_detectada=False,
                            escalada_ativada=False,
                            triagem_encerrada=False,
                            contexto_rag="",
                            intencao="triagem",
                            proxima_acao="triagem",
                            resposta_final="",
                            agente_usado="",
                        )

                        resultado = st.session_state.grafo.invoke(estado)

                        resposta = resultado.get("resposta_final", "")
                        agente = resultado.get("agente_usado", "")
                        rag_usado = resultado.get("contexto_rag", "") != ""

                        # Verifica escalada
                        if resultado.get("escalada_ativada"):
                            st.session_state.escalada_ativada = True

                    except Exception as e:
                        resposta = f"Ocorreu um erro. Por favor, tente novamente. ({str(e)[:80]})"
                        agente = "erro"
                        rag_usado = False

                # Exibe resposta
                st.markdown(resposta)

                # Exibe metadados em expander
                with st.expander("🔍 Detalhes do processamento", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Agente usado", agente)
                    with col2:
                        st.metric("RAG", "✅ Sim" if rag_usado else "❌ Não")

                # Alerta visual para escalada
                if st.session_state.escalada_ativada:
                    st.error(
                        "⚠️ **ATENÇÃO:** Situação de emergência detectada. "
                        "Ligue imediatamente para o **SAMU (192)**."
                    )

        st.session_state.historico.append({
            "role": "assistant",
            "content": resposta,
        })

        st.rerun()