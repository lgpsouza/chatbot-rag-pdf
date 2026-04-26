from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from chatbot import Chatbot

st.set_page_config(page_title="Chatbot RAG", page_icon="🤖", layout="centered")
st.title("Chatbot RAG — Documentos PDF")
st.caption("Faça perguntas sobre o conteúdo dos PDFs indexados.")


@st.cache_resource(show_spinner="Carregando documentos e vectorstore...")
def carregar_chatbot() -> Chatbot:
    return Chatbot()


try:
    bot = carregar_chatbot()
except EnvironmentError as e:
    st.cache_resource.clear()
    st.error(str(e))
    st.stop()
except ValueError as e:
    st.cache_resource.clear()
    st.warning(str(e))
    st.stop()
except Exception as e:
    st.cache_resource.clear()
    st.error(f"Erro inesperado ao inicializar o chatbot: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Digite sua pergunta..."):
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando resposta nos documentos..."):
            resposta = bot.perguntar(pergunta)
        st.markdown(resposta)

    st.session_state.messages.append({"role": "assistant", "content": resposta})
