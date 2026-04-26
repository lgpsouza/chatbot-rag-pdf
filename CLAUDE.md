# CLAUDE.md — Chatbot RAG com Processamento de PDFs

## Visão geral

Chatbot conversacional com RAG (Retrieval-Augmented Generation) que responde perguntas em linguagem natural baseadas no conteúdo de documentos PDF. Interface web com Streamlit. Usa LangChain + OpenAI + ChromaDB.

## Comandos essenciais

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar interface web (principal)
streamlit run app/interface.py

# Rodar via CLI (fallback)
python app/main.py

# Executar testes
.venv/bin/pytest tests/ -v

# Executar testes com cobertura
.venv/bin/pytest tests/ -v --cov=app --cov-report=term-missing
```

## Estrutura do projeto

```text
app/
  interface.py   — Interface web Streamlit com histórico de sessão
  main.py        — Fallback CLI: loop de interação no terminal
  chatbot.py     — Chain RAG via LCEL (retriever | prompt | llm | parser)
  embeddings.py  — Cria ou reutiliza vectorstore ChromaDB persistido
  pdf_loader.py  — Carrega PDFs, faz chunking e filtra chunks vazios
data/            — PDFs de entrada (não versionados, ignorados pelo git)
vector_store/    — Índice ChromaDB persistido localmente (não versionado)
tests/           — Testes unitários com mocks
docs/            — Documentação de decisões técnicas
```

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```env
OPENAI_API_KEY=sk-...
```

O `load_dotenv()` é chamado em `app/interface.py` e `app/main.py` antes de qualquer import da aplicação.

## Decisões de arquitetura

- **Streamlit em vez de CLI** — interface web com `st.chat_input` e `st.chat_message`; histórico mantido em `st.session_state`; `main.py` permanece como fallback CLI
- **`@st.cache_resource` no Chatbot** — evita recarregar o vectorstore a cada interação do usuário
- **LCEL em vez de RetrievalQA** — `RetrievalQA` foi removido no LangChain 1.x; a chain usa `RunnablePassthrough` e `StrOutputParser`
- **Reuso do vectorstore** — `embeddings.py` verifica se `vector_store/` já existe antes de reprocessar PDFs, evitando custo desnecessário com a API de embeddings
- **Modelo explícito** — sempre usar `text-embedding-3-small` e `gpt-4o-mini` explicitamente; nunca depender do default da OpenAI
- **Chunks vazios** — `pdf_loader.py` filtra chunks com apenas espaços e emite `warnings.warn()` (PDFs de imagem sem OCR não são suportados)

## Padrões de código

- Imports do LangChain: usar `langchain_core`, `langchain_openai`, `langchain_community` e `langchain_text_splitters` — nunca `langchain.chains` ou `langchain.text_splitter` (removidos no 1.x)
- Erros da API OpenAI: capturar `RateLimitError` e `APIError` de `openai`; nunca deixar propagar até o usuário
- Erros de configuração: exibir via `st.error()` e `st.stop()` na interface; nunca deixar a app travar silenciosamente
- Commits: seguir Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`)

## Testes

Os testes ficam em `tests/test_chatbot.py` (15 testes, todos passando). `tests/conftest.py` define `OPENAI_API_KEY=sk-fake-test-key` via fixture `autouse`.

| Teste | O que valida |
| --- | --- |
| `test_carregar_pdfs_vazio` | `data/` vazia retorna lista vazia |
| `test_carregar_pdfs_retorna_documentos` | PDF válido gera chunks com conteúdo |
| `test_pdf_scan_sem_texto_emite_aviso` | Chunks vazios emitem `warnings.warn` |
| `test_pdf_malformado_emite_aviso_e_continua` | PDF corrompido é ignorado; outros continuam |
| `test_vectorstore_existente_e_reutilizado` | Vectorstore populado não aciona `carregar_pdfs()` |
| `test_vectorstore_novo_emite_aviso_de_custo` | Nova geração emite aviso de crédito |
| `test_vectorstore_vazio_emite_aviso` | Diretório vazio lança `ValueError` com aviso |
| `test_construir_vectorstore_sem_permissao_de_escrita` | `PermissionError` quando sem acesso ao diretório |
| `test_chatbot_sem_api_key` | `EnvironmentError` quando `OPENAI_API_KEY` ausente |
| `test_perguntar_retorna_string` | `perguntar()` retorna `str` não vazia |
| `test_perguntar_nao_retorna_vazio_em_contexto_pobre` | Contexto insuficiente retorna frase informativa |
| `test_perguntar_string_vazia` | Entrada vazia/espaços retorna "Por favor" sem chamar a chain |
| `test_perguntar_string_muito_longa` | Pergunta > 4096 chars retorna "Limite de" sem chamar a chain |
| `test_rate_limit_retorna_mensagem_amigavel` | `RateLimitError` retorna mensagem amigável |
| `test_api_error_retorna_mensagem_amigavel` | `APIError` retorna mensagem amigável |

Cobertura atual: `pdf_loader` 100%, `embeddings` 100%, `chatbot` 94%. Todos os testes usam mocks — nenhum faz chamada real à API OpenAI.

## Roadmap

- **v0.1 (atual)** — Pipeline RAG com interface Streamlit
- **v0.2** — Histórico persistido entre sessões + reranking
- **v0.3** — Upload de PDFs via interface + Docker + CI

## Documentação de referência

- [docs/analise-riscos.md](docs/analise-riscos.md) — Riscos técnicos identificados e testes mínimos
- [docs/revisao-planejamento.md](docs/revisao-planejamento.md) — O que está fora do escopo do MVP e riscos a mitigar
- [docs/estrutura-projeto.md](docs/estrutura-projeto.md) — Descrição dos módulos
- [docs/escopo-mvp.md](docs/escopo-mvp.md) — Requisitos funcionais, não funcionais e critérios de aceite
- [docs/backlog.md](docs/backlog.md) — Backlog por release com critérios de aceite
- [docs/arquitetura.md](docs/arquitetura.md) — Diagrama Mermaid de componentes e fluxo de dados
