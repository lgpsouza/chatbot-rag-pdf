import warnings
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from pdf_loader import carregar_pdfs

VECTOR_STORE_DIR = Path(__file__).parent.parent / "vector_store"


def construir_vectorstore() -> Chroma:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    if VECTOR_STORE_DIR.exists() and any(VECTOR_STORE_DIR.iterdir()):
        return Chroma(
            persist_directory=str(VECTOR_STORE_DIR),
            embedding_function=embeddings,
        )

    if VECTOR_STORE_DIR.exists() and not any(VECTOR_STORE_DIR.iterdir()):
        warnings.warn(
            "vector_store/ existe mas está vazio. "
            "PDFs serão reprocessados e novos embeddings serão gerados."
        )

    documentos = carregar_pdfs()
    if not documentos:
        raise ValueError(
            "Nenhum documento encontrado. Adicione arquivos PDF na pasta data/."
        )

    return Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )
