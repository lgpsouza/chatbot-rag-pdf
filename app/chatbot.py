import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from openai import APIError, RateLimitError

from embeddings import construir_vectorstore

_PROMPT = ChatPromptTemplate.from_template(
    "Responda a pergunta usando apenas o contexto abaixo.\n\n"
    "Contexto:\n{context}\n\n"
    "Pergunta: {question}"
)


def _format_docs(docs) -> str:
    return "\n\n".join(d.page_content for d in docs)


class Chatbot:
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY não definida. Configure o arquivo .env.")

        vectorstore = construir_vectorstore()
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=2)
        retriever = vectorstore.as_retriever()

        self.chain = (
            {"context": retriever | _format_docs, "question": RunnablePassthrough()}
            | _PROMPT
            | llm
            | StrOutputParser()
        )

    def perguntar(self, pergunta: str) -> str:
        try:
            return self.chain.invoke(pergunta)
        except RateLimitError:
            return "Limite de requisições atingido. Aguarde alguns segundos e tente novamente."
        except APIError as e:
            return f"Erro na API OpenAI: {e}"
