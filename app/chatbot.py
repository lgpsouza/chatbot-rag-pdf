import os
from typing import Sequence

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from openai import APIError, APITimeoutError, RateLimitError

from embeddings import construir_vectorstore

MAX_PERGUNTA_CHARS = 4096

_PROMPT = ChatPromptTemplate.from_template(
    "Responda a pergunta usando apenas o contexto abaixo.\n"
    "Se o contexto não contiver informações suficientes, responda exatamente: "
    "'Não encontrei informações sobre isso nos documentos fornecidos.'\n"
    "Não invente respostas.\n\n"
    "Contexto:\n{context}\n\n"
    "Pergunta: {question}"
)


def _format_docs(docs: Sequence[Document]) -> str:
    return "\n\n".join(d.page_content for d in docs)


def _build_chain(vectorstore: Chroma, llm: ChatOpenAI):
    return (
        {"context": vectorstore.as_retriever() | _format_docs, "question": RunnablePassthrough()}
        | _PROMPT
        | llm
        | StrOutputParser()
    )


class Chatbot:
    def __init__(self, vectorstore: Chroma | None = None):
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY não definida. Configure o arquivo .env.")

        if vectorstore is None:
            vectorstore = construir_vectorstore()

        self.chain = _build_chain(
            vectorstore,
            ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=2),
        )

    def perguntar(self, pergunta: str) -> str:
        if not pergunta.strip():
            return "Por favor, digite uma pergunta."
        if len(pergunta) > MAX_PERGUNTA_CHARS:
            return f"Pergunta muito longa. Limite de {MAX_PERGUNTA_CHARS} caracteres."
        try:
            return self.chain.invoke(pergunta)
        except APITimeoutError:
            return "Tempo limite excedido. Tente novamente em instantes."
        except RateLimitError:
            return "Limite de requisições atingido. Aguarde alguns segundos e tente novamente."
        except APIError as e:
            return f"Erro na API OpenAI: {e}"
