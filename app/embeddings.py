import hashlib
import json
import os
import warnings
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from pdf_loader import DATA_DIR, carregar_pdfs

VECTOR_STORE_DIR = Path(__file__).parent.parent / "vector_store"
_MANIFEST = ".manifest.json"


# ── helpers privados ───────────────────────────────────────────────────────────

def _calcular_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _ler_manifest() -> dict[str, str]:
    manifest_path = VECTOR_STORE_DIR / _MANIFEST
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text())
    except Exception:
        return {}


def _salvar_manifest(pdfs: list[Path]) -> None:
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {pdf.name: _calcular_hash(pdf) for pdf in pdfs}
    (VECTOR_STORE_DIR / _MANIFEST).write_text(json.dumps(manifest, indent=2))


def _hashes_coincidem(pdfs: list[Path]) -> bool:
    manifest = _ler_manifest()
    nomes_atuais = {pdf.name for pdf in pdfs}
    if set(manifest.keys()) != nomes_atuais:
        return False
    return all(manifest.get(pdf.name) == _calcular_hash(pdf) for pdf in pdfs)


def _vs_populado() -> bool:
    if not VECTOR_STORE_DIR.exists():
        return False
    return any(f for f in VECTOR_STORE_DIR.iterdir() if f.name != _MANIFEST)


def _verificar_permissao(path: Path) -> None:
    if not os.access(path, os.W_OK):
        raise PermissionError(
            f"Sem permissão de escrita em {path}. "
            "Verifique as permissões do diretório."
        )


# ── API pública ────────────────────────────────────────────────────────────────

def construir_vectorstore(documentos: list[Document] | None = None) -> Chroma:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    pdfs_atuais = sorted(DATA_DIR.glob("*.pdf"))

    if _vs_populado():
        if _hashes_coincidem(pdfs_atuais):
            return Chroma(
                persist_directory=str(VECTOR_STORE_DIR),
                embedding_function=embeddings,
            )
        warnings.warn(
            "PDFs alterados detectados. Reconstruindo vectorstore."
        )

    vs_existe = VECTOR_STORE_DIR.exists()
    if vs_existe and not _vs_populado():
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

    vs = Chroma.from_documents(
        documents=documentos,
        embedding=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )
    _salvar_manifest(pdfs_atuais)
    return vs
