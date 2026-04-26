import warnings
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = Path(__file__).parent.parent / "data"


def carregar_pdfs() -> list[Document]:
    pdfs = list(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documentos: list[Document] = []

    for pdf in pdfs:
        try:
            loader = PyPDFLoader(str(pdf))
            chunks = splitter.split_documents(loader.load())
        except Exception as exc:
            warnings.warn(
                f"{pdf.name}: falha ao processar PDF ({exc}). Arquivo ignorado."
            )
            continue

        chunks_validos = [c for c in chunks if c.page_content.strip()]
        ignorados = len(chunks) - len(chunks_validos)

        if ignorados > 0:
            warnings.warn(
                f"{pdf.name}: {ignorados} chunk(s) vazio(s) ignorados "
                "(possível PDF de imagem sem OCR)."
            )

        documentos.extend(chunks_validos)

    return documentos
