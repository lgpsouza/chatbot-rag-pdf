import importlib
import os
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from openai import APIError, APITimeoutError, RateLimitError


# ── pdf_loader ────────────────────────────────────────────────────────────────

def test_carregar_pdfs_vazio(tmp_path, monkeypatch):
    import pdf_loader
    monkeypatch.setattr(pdf_loader, "DATA_DIR", tmp_path)
    assert pdf_loader.carregar_pdfs() == []


def test_carregar_pdfs_retorna_documentos(tmp_path, monkeypatch):
    import pdf_loader
    from langchain_core.documents import Document

    (tmp_path / "teste.pdf").write_bytes(b"%PDF-1.4 fake")
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

    (tmp_path / "scan.pdf").write_bytes(b"%PDF-1.4 fake")
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

    (tmp_path / "valido.pdf").write_bytes(b"%PDF-1.4 fake")
    (tmp_path / "corrompido.pdf").write_bytes(b"nao e um pdf")
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


# ── embeddings ────────────────────────────────────────────────────────────────

def test_vectorstore_existente_e_reutilizado(tmp_path, monkeypatch):
    import embeddings as emb_module

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    vs_dir = tmp_path / "vector_store"
    vs_dir.mkdir()
    (vs_dir / "chroma.sqlite3").write_bytes(b"fake")
    (vs_dir / ".manifest.json").write_text("{}")
    monkeypatch.setattr(emb_module, "VECTOR_STORE_DIR", vs_dir)
    monkeypatch.setattr(emb_module, "DATA_DIR", data_dir)

    with patch("embeddings.Chroma") as mock_chroma, \
         patch("embeddings.carregar_pdfs") as mock_loader:
        mock_chroma.return_value = MagicMock()
        emb_module.construir_vectorstore()
        mock_loader.assert_not_called()


def test_vectorstore_novo_emite_aviso_de_custo(tmp_path, monkeypatch):
    import embeddings as emb_module
    from langchain_core.documents import Document

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setattr(emb_module, "VECTOR_STORE_DIR", tmp_path / "vector_store")
    monkeypatch.setattr(emb_module, "DATA_DIR", data_dir)

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
    import embeddings as emb_module

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    vs_vazio = tmp_path / "vector_store"
    vs_vazio.mkdir()
    monkeypatch.setattr(emb_module, "VECTOR_STORE_DIR", vs_vazio)
    monkeypatch.setattr(emb_module, "DATA_DIR", data_dir)

    with patch("embeddings.carregar_pdfs", return_value=[]), \
         warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        with pytest.raises(ValueError):
            emb_module.construir_vectorstore()
        assert any("vazio" in str(x.message) for x in w)


def test_construir_vectorstore_sem_permissao_de_escrita(tmp_path, monkeypatch):
    import embeddings as emb_module
    from langchain_core.documents import Document

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setattr(emb_module, "VECTOR_STORE_DIR", tmp_path / "vector_store")
    monkeypatch.setattr(emb_module, "DATA_DIR", data_dir)

    doc = Document(page_content="Texto.", metadata={})
    with patch("embeddings.carregar_pdfs", return_value=[doc]), \
         patch("embeddings.OpenAIEmbeddings"), \
         patch("embeddings.os.access", return_value=False):
        with pytest.raises(PermissionError, match="Sem permissão de escrita"):
            emb_module.construir_vectorstore()


def test_vectorstore_reutilizado_quando_hashes_coincidem(tmp_path, monkeypatch):
    import embeddings as emb_module
    import hashlib
    import json

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pdf_bytes = b"%PDF-1.4 fake content"
    (data_dir / "doc.pdf").write_bytes(pdf_bytes)

    vs_dir = tmp_path / "vector_store"
    vs_dir.mkdir()
    (vs_dir / "chroma.sqlite3").write_bytes(b"fake")
    hash_correto = hashlib.md5(pdf_bytes).hexdigest()
    (vs_dir / ".manifest.json").write_text(json.dumps({"doc.pdf": hash_correto}))

    monkeypatch.setattr(emb_module, "VECTOR_STORE_DIR", vs_dir)
    monkeypatch.setattr(emb_module, "DATA_DIR", data_dir)

    with patch("embeddings.Chroma") as mock_chroma, \
         patch("embeddings.carregar_pdfs") as mock_loader:
        mock_chroma.return_value = MagicMock()
        emb_module.construir_vectorstore()
        mock_loader.assert_not_called()
        mock_chroma.from_documents.assert_not_called()


def test_vectorstore_reconstruido_quando_pdf_alterado(tmp_path, monkeypatch):
    import embeddings as emb_module
    import json
    from langchain_core.documents import Document

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "doc.pdf").write_bytes(b"%PDF-1.4 fake")

    vs_dir = tmp_path / "vector_store"
    vs_dir.mkdir()
    (vs_dir / "chroma.sqlite3").write_bytes(b"fake")
    (vs_dir / ".manifest.json").write_text(json.dumps({"doc.pdf": "hash_antigo_invalido"}))

    monkeypatch.setattr(emb_module, "VECTOR_STORE_DIR", vs_dir)
    monkeypatch.setattr(emb_module, "DATA_DIR", data_dir)

    doc = Document(page_content="Conteúdo novo.", metadata={})
    with patch("embeddings.carregar_pdfs", return_value=[doc]), \
         patch("embeddings.Chroma") as mock_chroma, \
         patch("embeddings.OpenAIEmbeddings"), \
         warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        mock_chroma.from_documents.return_value = MagicMock()
        emb_module.construir_vectorstore()
        assert any("PDFs alterados" in str(x.message) for x in w)

    mock_chroma.from_documents.assert_called_once()


def test_upload_path_traversal_sanitizacao():
    casos = [
        ("../../etc/passwd.pdf", "passwd.pdf"),
        ("/absolute/path/doc.pdf", "doc.pdf"),
        ("normal.pdf", "normal.pdf"),
    ]
    for entrada, esperado in casos:
        assert Path(entrada).name == esperado


# ── chatbot ───────────────────────────────────────────────────────────────────

def _make_bot(monkeypatch, resposta: str = "Resposta simulada."):
    """Helper: cria Chatbot com vectorstore mockado via injeção."""
    import chatbot as chatbot_module
    importlib.reload(chatbot_module)

    mock_vs = MagicMock()
    mock_vs.as_retriever.return_value = MagicMock()

    with patch("chatbot.ChatOpenAI"), \
         patch("chatbot.StrOutputParser"), \
         patch("chatbot.RunnablePassthrough"):
        bot = chatbot_module.Chatbot(vectorstore=mock_vs)

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = resposta
    bot.chain = mock_chain
    return bot


def test_chatbot_sem_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import chatbot as chatbot_module
    importlib.reload(chatbot_module)
    with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
        chatbot_module.Chatbot()


def test_perguntar_retorna_string(monkeypatch):
    bot = _make_bot(monkeypatch)
    resposta = bot.perguntar("Qual é o conteúdo?")
    assert isinstance(resposta, str) and resposta != ""


def test_perguntar_nao_retorna_vazio_em_contexto_pobre(monkeypatch):
    bot = _make_bot(
        monkeypatch,
        resposta="Não encontrei informações sobre isso nos documentos fornecidos."
    )
    resposta = bot.perguntar("Qual é a cor do céu em Marte?")
    assert "documentos fornecidos" in resposta


def test_perguntar_string_vazia(monkeypatch):
    bot = _make_bot(monkeypatch)
    for entrada in ["", "   ", "\t\n"]:
        resposta = bot.perguntar(entrada)
        assert "Por favor" in resposta
        bot.chain.invoke.assert_not_called()


def test_perguntar_string_muito_longa(monkeypatch):
    bot = _make_bot(monkeypatch)
    pergunta_longa = "x" * 5000
    resposta = bot.perguntar(pergunta_longa)
    assert "Limite de" in resposta
    bot.chain.invoke.assert_not_called()


def test_rate_limit_retorna_mensagem_amigavel(monkeypatch):
    bot = _make_bot(monkeypatch)
    bot.chain.invoke.side_effect = RateLimitError(
        message="rate limit", response=MagicMock(), body={}
    )
    resposta = bot.perguntar("Pergunta qualquer")
    assert "Limite de requisições" in resposta


def test_api_error_retorna_mensagem_amigavel(monkeypatch):
    bot = _make_bot(monkeypatch)
    bot.chain.invoke.side_effect = APIError(
        message="api error", request=MagicMock(), body={}
    )
    resposta = bot.perguntar("Pergunta qualquer")
    assert "Erro na API OpenAI" in resposta


def test_timeout_retorna_mensagem_amigavel(monkeypatch):
    bot = _make_bot(monkeypatch)
    bot.chain.invoke.side_effect = APITimeoutError(request=MagicMock())
    resposta = bot.perguntar("Pergunta qualquer")
    assert "Tempo limite" in resposta
