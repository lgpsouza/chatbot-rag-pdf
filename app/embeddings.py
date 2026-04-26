import os
import warnings
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from pdf_loader import carregar_pdfs

VECTOR_STORE_DIR = Path(__file__).parent.parent / "vector_store"


def construir_vectorstore(documentos: list[Document] | None = None) -> Chroma:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vs_existe = VECTOR_STORE_DIR.exists()
    vs_populado = vs_existe and any(VECTOR_STORE_DIR.iterdir())

    if vs_populado:
        return Chroma(
            persist_directory=str(VECTOR_STORE_DIR),
            embedding_function=embeddings,
        )

    if vs_existe and not vs_populado:
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

    target_dir = VECTOR_STORE_DIR if vs_existe else VECTOR_STORE_DIR.parent
    if not os.access(target_dir, os.W_OK):
        raise PermissionError(
            f"Sem permissão de escrita em {target_dir}. "
            "Verifique as permissões do diretório."
        )

    warnings.warn(
        f"Gerando embeddings para {len(documentos)} chunk(s). "
        "Isso consome créditos da API OpenAI."
    )

    return Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )
