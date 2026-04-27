# Roteiro de Demo — Chatbot RAG (5 min)

---

## Bloco 0 — Pré-demo `[antes de entrar na sala]`

```bash
# Terminal já aberto no diretório do projeto
source .venv/bin/activate
# PDFs já em data/ (não mostrar indexação do zero — demora)
# Browser fechado
```

---

## Bloco 1 — Inicialização `[0:00 – 0:45]`

**Fala:** "A interface sobe com um comando."

```bash
streamlit run app/interface.py
```

Mostrar no terminal: URL local (`http://localhost:8501`). Abrir no browser.

> Ponto técnico: `@st.cache_resource` — vectorstore carregado uma vez, reutilizado em todas as interações da sessão.

---

## Bloco 2 — Estrutura de dados `[0:45 – 1:30]`

Mostrar no terminal (segunda aba):

```bash
ls data/           # PDFs de entrada
ls vector_store/   # índice ChromaDB persistido
cat vector_store/.manifest.json   # hashes MD5 dos PDFs indexados
```

> Ponto técnico: rebuild só ocorre quando hash muda — sem custo duplicado de embeddings.

---

## Bloco 3 — Upload e reindexação `[1:30 – 2:30]`

Na sidebar da interface:
1. Fazer upload de um PDF novo
2. Mostrar o botão "Reindexar documentos" em destaque (`type="primary"`)
3. Clicar — mostrar spinner + reconstrução do índice no terminal

> Ponto técnico: `delete_collection()` em vez de `shutil.rmtree` — evita `SQLITE_READONLY_DBMOVED` com o singleton ChromaDB ativo.

---

## Bloco 4 — Pergunta e resposta `[2:30 – 3:45]`

No campo de chat, digitar uma pergunta cujo conteúdo está no PDF indexado:

```
"Qual é o objetivo principal do documento X?"
```

Mostrar:
- Spinner de loading
- Resposta exibida com `st.chat_message`
- Histórico preservado na tela

> Ponto técnico: chain LCEL — `retriever | prompt | llm | StrOutputParser` — sem `RetrievalQA` (removido no LangChain 1.x).

---

## Bloco 5 — Testes e cobertura `[3:45 – 4:30]`

```bash
make test
# ou: .venv/bin/pytest tests/ -v --cov=app --cov-report=term-missing
```

Mostrar output: 19 testes passando, cobertura `pdf_loader` 100%, `embeddings` 100%, `chatbot` 94%. Nenhuma chamada real à API OpenAI.

---

## Bloco 6 — Perguntas `[4:30 – 5:00]`

Deixar o chat aberto. Convidar para fazer uma pergunta ao vivo.

---

## Variáveis de risco

- Latência da API OpenAI na demo ao vivo → ter uma resposta capturada em screenshot como fallback
- PDF sem texto extraível → mostrar o aviso amigável como feature, não como erro
