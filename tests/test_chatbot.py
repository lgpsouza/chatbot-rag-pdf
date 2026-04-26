import importlib
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ── pdf_loader ────────────────────────────────────────────────────────────────

def test_carregar_pdfs_vazio(tmp_path, monkeypatch):
    import pdf_loader
    monkeypatch.setattr(pdf_loader, "DATA_DIR", tmp_path)
    resultado = pdf_loader.carregar_pdfs()
    assert resultado == []


def test_carregar_pdfs_retorna_documentos(tmp_path, monkeypatch):
    import pdf_loader
    from langchain_core.documents import Document

    pdf_fake = tmp_path / "teste.pdf"
    pdf_fake.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setattr(pdf_loader, "DATA_DIR", tmp_path)

    chunk = Document(page_content="Conteúdo do documento de teste.", metadata={})
    with patch("pdf_loader.PyPDFLoader") as mock_loader:
        mock_loader.return_value.load.return_value = [chunk]
        resultado = pdf_loader.carregar_pdfs()

    assert len(resultado) > 0
    assert resultado[0].page_content.strip() != ""


def test_pdf_scan_sem_texto_emite_aviso(tmp_path, monkeypatch):
    import pdf_loader
    from langchain_core.documents import Document

    pdf_fake = tmp_path / "scan.pdf"
    pdf_fake.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setattr(pdf_loader, "DATA_DIR", tmp_path)

    chunk_vazio = Document(page_content="   ", metadata={})
    with patch("pdf_loader.PyPDFLoader") as mock_loader, \
         patch("pdf_loader.RecursiveCharacterTextSplitter") as mock_splitter:
        mock_loader.return_value.load.return_value = [chunk_vazio]
        mock_splitter.return_value.split_documents.return_value = [chunk_vazio]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            resultado = pdf_loader.carregar_pdfs()
            assert any("chunk(s) vazio(s)" in str(x.message) for x in w)

    assert resultado == []


def test_pdf_malformado_emite_aviso_e_continua(tmp_path, monkeypatch):
    import pdf_loader
    from langchain_core.documents import Document

    pdf_ok = tmp_path / "valido.pdf"
    pdf_ok.write_bytes(b"%PDF-1.4 fake")
    pdf_mal = tmp_path / "corrompido.pdf"
    pdf_mal.write_bytes(b"nao e um pdf")

    monkeypatch.setattr(pdf_loader, "DATA_DIR", tmp_path)

    chunk = Document(page_content="Conteúdo válido.", metadata={})

    def loader_seletivo(path):
        mock = MagicMock()
        if "corrompido" in path:
            mock.load.side_effect = Exception("PDF inválido")
        else:
            mock.load.return_value = [chunk]
        return mock

    with patch("pdf_loader.PyPDFLoader", side_effect=loader_seletivo), \
         warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        resultado = pdf_loader.carregar_pdfs()
        assert any("falha ao processar" in str(x.message) for x in w)

    assert len(resultado) == 1
    assert resultado[0].page_content == "Conteúdo válido."


# ── chatbot ───────────────────────────────────────────────────────────────────

def test_chatbot_sem_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import chatbot as chatbot_module
    importlib.reload(chatbot_module)
    with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
        chatbot_module.Chatbot()


def test_perguntar_retorna_string(monkeypatch):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "Resposta simulada."

    mock_vectorstore = MagicMock()
    mock_vectorstore.as_retriever.return_value = MagicMock()

    import chatbot as chatbot_module
    importlib.reload(chatbot_module)

    with patch("chatbot.construir_vectorstore", return_value=mock_vectorstore), \
         patch("chatbot.ChatOpenAI"), \
         patch.object(chatbot_module.Chatbot, "__init__", lambda self: None):
        bot = chatbot_module.Chatbot()
        bot.chain = mock_chain
        resposta = bot.perguntar("Qual é o conteúdo?")

    assert isinstance(resposta, str)
    assert resposta != ""


def test_perguntar_nao_retorna_vazio_em_contexto_pobre(monkeypatch):
    """Chain com contexto sem informação útil deve retornar string, não vazio."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = (
        "Não encontrei informações suficientes nos documentos para responder."
    )

    import chatbot as chatbot_module
    importlib.reload(chatbot_module)

    with patch("chatbot.construir_vectorstore", return_value=MagicMock()), \
         patch("chatbot.ChatOpenAI"), \
         patch.object(chatbot_module.Chatbot, "__init__", lambda self: None):
        bot = chatbot_module.Chatbot()
        bot.chain = mock_chain
        resposta = bot.perguntar("Qual é a cor do céu em Marte?")

    assert isinstance(resposta, str)
    assert len(resposta) > 0


def test_vectorstore_existente_e_reutilizado(tmp_path, monkeypatch):
    """vectorstore populado deve ser reutilizado sem chamar carregar_pdfs."""
    import embeddings as emb_module
    from langchain_community.vectorstores import Chroma

    vs_dir = tmp_path / "vector_store"
    vs_dir.mkdir()
    (vs_dir / "chroma.sqlite3").write_bytes(b"fake")
    monkeypatch.setattr(emb_module, "VECTOR_STORE_DIR", vs_dir)

    with patch("embeddings.Chroma") as mock_chroma, \
         patch("embeddings.carregar_pdfs") as mock_loader:
        mock_chroma.return_value = MagicMock(spec=Chroma)
        emb_module.construir_vectorstore()
        mock_loader.assert_not_called()


def test_vectorstore_novo_emite_aviso_de_custo(tmp_path, monkeypatch):
    """Geração de novos embeddings deve emitir aviso de custo."""
    import embeddings as emb_module
    from langchain_core.documents import Document

    vs_dir = tmp_path / "vector_store"
    monkeypatch.setattr(emb_module, "VECTOR_STORE_DIR", vs_dir)

    doc = Document(page_content="Texto de teste.", metadata={})
    with patch("embeddings.carregar_pdfs", return_value=[doc]), \
         patch("embeddings.Chroma") as mock_chroma, \
         patch("embeddings.OpenAIEmbeddings"), \
         warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        mock_chroma.from_documents.return_value = MagicMock()
        emb_module.construir_vectorstore()
        assert any("consome créditos" in str(x.message) for x in w)


def test_vectorstore_vazio_emite_aviso(tmp_path, monkeypatch):
    """vector_store/ existente mas vazio deve emitir warning."""
    import embeddings as emb_module

    vs_vazio = tmp_path / "vector_store"
    vs_vazio.mkdir()
    monkeypatch.setattr(emb_module, "VECTOR_STORE_DIR", vs_vazio)

    with patch("embeddings.carregar_pdfs", return_value=[]), \
         warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        with pytest.raises(ValueError):
            emb_module.construir_vectorstore()
        assert any("vazio" in str(x.message) for x in w)
