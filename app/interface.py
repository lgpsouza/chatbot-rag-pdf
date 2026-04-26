import shutil
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from chatbot import Chatbot
from embeddings import VECTOR_STORE_DIR
from pdf_loader import DATA_DIR, validar_pdf

st.set_page_config(page_title="Chatbot RAG", page_icon="🤖", layout="centered")

DATA_DIR.mkdir(parents=True, exist_ok=True)

MAX_PDF_MB = 50


# ── Barra lateral ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Carregar PDFs")

    uploaded_files = st.file_uploader(
        "Selecione arquivos PDF",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        if "saved_files" not in st.session_state:
            st.session_state.saved_files = set()

        novos = [
            f for f in uploaded_files
            if Path(f.name).name not in st.session_state.saved_files
        ]
        salvos = 0
        for f in novos:
            nome_seguro = Path(f.name).name
            conteudo = f.getvalue()
            if len(conteudo) > MAX_PDF_MB * 1024 * 1024:
                st.warning(f"⚠️ {nome_seguro}: excede o limite de {MAX_PDF_MB} MB e foi ignorado.")
                st.session_state.saved_files.add(nome_seguro)
                continue
            (DATA_DIR / nome_seguro).write_bytes(conteudo)
            erro = validar_pdf(DATA_DIR / nome_seguro)
            if erro:
                st.warning(f"⚠️ {nome_seguro}: {erro}. Arquivo removido.")
                (DATA_DIR / nome_seguro).unlink(missing_ok=True)
                st.session_state.saved_files.add(nome_seguro)
                continue
            st.session_state.saved_files.add(nome_seguro)
            salvos += 1

        if salvos:
            st.session_state.precisa_reindexar = True
            st.success(f"✅ {salvos} arquivo(s) salvo(s) em data/")

    st.divider()

    st.subheader("Documentos indexados")

    if "validados" not in st.session_state:
        st.session_state.validados = set()

    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    for pdf in pdfs:
        if pdf.name not in st.session_state.validados:
            erro = validar_pdf(pdf)
            if erro:
                st.warning(f"⚠️ {pdf.name}: {erro}. Arquivo removido.")
                pdf.unlink(missing_ok=True)
                st.session_state.precisa_reindexar = True
                continue
            st.session_state.validados.add(pdf.name)

    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    if pdfs:
        for pdf in pdfs:
            st.markdown(f"- 📄 {pdf.name}")
    else:
        st.info("Nenhum PDF encontrado em data/")

    st.divider()

    vs_ok = VECTOR_STORE_DIR.exists() and any(VECTOR_STORE_DIR.iterdir())
    st.markdown("**Vectorstore:** " + ("✅ carregado" if vs_ok else "⚠️ não inicializado"))

    st.divider()

    # Destaca o botão quando há PDFs sem vectorstore (inclui refresh de página)
    precisa_reindexar = (
        st.session_state.get("precisa_reindexar", False)
        or (bool(pdfs) and not vs_ok)
    )

    if st.button(
        "🔄 Reindexar documentos",
        use_container_width=True,
        type="primary" if precisa_reindexar else "secondary",
        disabled=not pdfs,
    ):
        try:
            if VECTOR_STORE_DIR.exists():
                shutil.rmtree(VECTOR_STORE_DIR)
        except OSError as e:
            st.error(f"Erro ao apagar vectorstore: {e}")
            st.stop()
        st.cache_resource.clear()
        st.session_state.precisa_reindexar = False
        st.rerun()

    if st.button("🗑️ Limpar histórico", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── Chatbot ───────────────────────────────────────────────────────────────────

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
    pergunta_limpa = pergunta.strip()
    if not pergunta_limpa:
        st.warning("Por favor, digite uma pergunta válida.")
    else:
        st.session_state.messages.append({"role": "user", "content": pergunta_limpa})
        with st.chat_message("user"):
            st.markdown(pergunta_limpa)

        with st.chat_message("assistant"):
            with st.spinner("Buscando resposta nos documentos..."):
                resposta = bot.perguntar(pergunta_limpa)
            st.markdown(resposta)

        st.session_state.messages.append({"role": "assistant", "content": resposta})
