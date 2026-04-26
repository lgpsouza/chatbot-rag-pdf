import os
import warnings
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from pdf_loader import carregar_pdfs

VECTOR_STORE_DIR = Path(__file__).parent.parent / "vector_store"


def _vs_populado() -> bool:
    return VECTOR_STORE_DIR.exists() and any(VECTOR_STORE_DIR.iterdir())


def _verificar_permissao(path: Path) -> None:
    if not os.access(path, os.W_OK):
        raise PermissionError(
            f"Sem permissão de escrita em {path}. "
            "Verifique as permissões do diretório."
        )


def construir_vectorstore(documentos: list[Document] | None = None) -> Chroma:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    if _vs_populado():
        return Chroma(
            persist_directory=str(VECTOR_STORE_DIR),
            embedding_function=embeddings,
        )

    vs_existe = VECTOR_STORE_DIR.exists()
    if vs_existe:
        warnings.warn(
            "vector_store/ existe mas está vazio. "
            "PDFs serão reprocessados e novos embeddings serão gerados."
        )

    if documentos is None:
        documentos = carregar_pdfs()

    if not documentos:
        raise ValueError(
            "Nenhum documento encontrado. Adicione arquivos PDF na pasta data/."
        )

    _verificar_permissao(VECTOR_STORE_DIR if vs_existe else VECTOR_STORE_DIR.parent)

    warnings.warn(
        f"Gerando embeddings para {len(documentos)} chunk(s). "
        "Isso consome créditos da API OpenAI."
    )

    return Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )
