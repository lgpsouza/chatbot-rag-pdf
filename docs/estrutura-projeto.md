# Estrutura do Projeto

```text
mini_projeto_modulo_01_ufg/
│
├── .env.example              # Variáveis de ambiente (modelo)
├── .gitignore
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── interface.py          # Interface web Streamlit (ponto de entrada principal)
│   ├── main.py               # Fallback CLI (linha de comando)
│   ├── chatbot.py            # Lógica RAG (LangChain chain)
│   ├── embeddings.py         # Geração e cache de embeddings
│   └── pdf_loader.py         # Processamento de PDFs
│
├── data/                     # PDFs locais (ignorado pelo git)
│
├── vector_store/             # Índice vetorial (ignorado pelo git)
│
├── tests/
│   └── test_chatbot.py
│
├── docs/                     # Documentação do projeto
│   ├── arquitetura.md
│   ├── backlog.md
│   ├── escopo-mvp.md
│   ├── estrutura-projeto.md
│   ├── analise-riscos.md
│   └── revisao-planejamento.md
│
└── PROMPTS/                  # Prompts utilizados no desenvolvimento
```

---

## Descrição dos Módulos

| Arquivo | Responsabilidade |
| --- | --- |
| `app/interface.py` | Interface web Streamlit — chat com histórico de sessão |
| `app/main.py` | Fallback CLI — loop de interação no terminal |
| `app/chatbot.py` | Chain RAG: recuperação + geração de resposta via LCEL |
| `app/embeddings.py` | Criação e reutilização do vectorstore ChromaDB |
| `app/pdf_loader.py` | Carregamento, chunking e filtragem de PDFs |
| `data/` | PDFs de entrada (não versionados) |
| `vector_store/` | Índice vetorial persistido localmente (não versionado) |
| `tests/` | Testes automatizados com mocks |
