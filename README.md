# Chatbot RAG com Processamento de PDFs

Chatbot conversacional com Retrieval-Augmented Generation (RAG) para responder perguntas baseadas em documentos PDF, utilizando embeddings semânticos e LLMs da OpenAI. Interface web com Streamlit.

---

## Objetivo

Permitir que usuários façam perguntas em linguagem natural sobre o conteúdo de documentos PDF, obtendo respostas precisas e fundamentadas nos próprios documentos.

---

## Stack Tecnológico

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.11+ |
| Interface web | Streamlit |
| Orquestração LLM | LangChain |
| Modelo de linguagem | OpenAI GPT-4o-mini |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector store | ChromaDB |
| Carregamento de PDFs | PyPDF |
| Variáveis de ambiente | python-dotenv |

---

## Estrutura do Projeto

```text
├── app/
│   ├── interface.py     # Interface web Streamlit (ponto de entrada principal)
│   ├── main.py          # Fallback CLI (linha de comando)
│   ├── chatbot.py       # Chain RAG
│   ├── embeddings.py    # Geração e persistência de embeddings
│   └── pdf_loader.py    # Carregamento e chunking de PDFs
├── data/                # PDFs locais (não versionados)
├── vector_store/        # Índice vetorial persistido (não versionado)
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## Como Rodar Localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/lgpsouza/chatbot-rag-pdf.git
cd chatbot-rag-pdf
```

### 2. Criar e ativar ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env e adicione sua OPENAI_API_KEY
```

### 5. Adicionar PDFs

Coloque os arquivos `.pdf` na pasta `data/`.

### 6. Iniciar a interface web

```bash
streamlit run app/interface.py
```

> Para usar via terminal: `python app/main.py`

---

## Exemplos de Uso

Após iniciar a interface, acesse `http://localhost:8501` no navegador:

```text
Você: Qual é o prazo de entrega descrito no contrato?
Bot:  Conforme a cláusula 4.2 do contrato, o prazo de entrega é de 30 dias corridos...

Você: Quais são os requisitos técnicos do sistema?
Bot:  Os requisitos técnicos listados no documento incluem...
```

---

## Roadmap de Releases

### v0.1 — MVP (atual)

- [x] Carregamento e chunking de PDFs
- [x] Geração de embeddings com ChromaDB
- [x] Chain RAG com LangChain + GPT-4o-mini
- [x] Interface web com Streamlit
- [x] Histórico de mensagens por sessão

### v0.2 — Melhorias de Qualidade

- [ ] Invalidação seletiva do vectorstore por hash de arquivo
- [ ] Histórico de conversa persistido entre sessões
- [ ] Reranking dos chunks recuperados

### v0.3 — Produção

- [ ] Upload de PDFs via interface web
- [ ] Containerização com Docker
- [ ] Pipeline CI com GitHub Actions

---

## Pré-requisitos

- Python 3.11+
- Chave de API da OpenAI ([platform.openai.com](https://platform.openai.com))
