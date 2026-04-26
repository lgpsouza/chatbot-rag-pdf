import warnings
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = Path(__file__).parent.parent / "data"


def _processar_pdf(pdf: Path, splitter: RecursiveCharacterTextSplitter) -> list[Document]:
    try:
        chunks = splitter.split_documents(PyPDFLoader(str(pdf)).load())
    except Exception as exc:
        warnings.warn(f"{pdf.name}: falha ao processar PDF ({exc}). Arquivo ignorado.")
        return []

    chunks_validos = [c for c in chunks if c.page_content.strip()]
    ignorados = len(chunks) - len(chunks_validos)

    if ignorados > 0:
        warnings.warn(
            f"{pdf.name}: {ignorados} chunk(s) vazio(s) ignorados "
            "(possível PDF de imagem sem OCR)."
        )

    return chunks_validos


def validar_pdf(pdf: Path) -> str | None:
    """Retorna None se válido, ou mensagem de erro se inválido."""
    try:
        paginas = PyPDFLoader(str(pdf)).load()
    except Exception as exc:
        return f"falha ao processar ({exc})"
    if not any(p.page_content.strip() for p in paginas):
        return "sem texto extraível (possível PDF de imagem sem OCR)"
    return None


def carregar_pdfs() -> list[Document]:
    pdfs = list(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documentos: list[Document] = []

    for pdf in pdfs:
        documentos.extend(_processar_pdf(pdf, splitter))

    return documentos
