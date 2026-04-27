# Estrutura do Projeto

```text
mini_projeto_modulo_01_ufg/
│
├── .env.example              # Variáveis de ambiente (modelo)
├── .gitignore
├── Makefile                  # Atalhos: install, run, test
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── interface.py          # Interface web Streamlit (ponto de entrada principal)
│   ├── main.py               # Fallback CLI (linha de comando)
│   ├── chatbot.py            # Lógica RAG (LangChain chain)
│   ├── embeddings.py         # Geração, cache e invalidação de embeddings
│   └── pdf_loader.py         # Carregamento, chunking, validação e filtragem de PDFs
│
├── data/                     # PDFs locais (ignorado pelo git, criado automaticamente)
│
├── vector_store/             # Índice vetorial ChromaDB (ignorado pelo git)
│   └── .manifest.json        # Manifest de hashes MD5 para invalidação seletiva
│
├── tests/
│   ├── conftest.py           # Fixture autouse: OPENAI_API_KEY=fake para todos os testes
│   └── test_chatbot.py       # 19 testes unitários com mocks
│
└── docs/                     # Documentação do projeto
    ├── arquitetura.md
    ├── backlog.md
    ├── escopo-mvp.md
    ├── estrutura-projeto.md
    ├── analise-riscos.md
    └── revisao-planejamento.md
```

---

## Descrição dos Módulos

| Arquivo | Responsabilidade |
| --- | --- |
| `app/interface.py` | Interface web Streamlit — upload de PDFs, validação, chat com histórico de sessão |
| `app/main.py` | Fallback CLI — loop de interação no terminal |
| `app/chatbot.py` | Chain RAG: recuperação + geração de resposta via LCEL |
| `app/embeddings.py` | Criação, reutilização e invalidação do vectorstore ChromaDB com manifest MD5 |
| `app/pdf_loader.py` | Carregamento, chunking, validação (`validar_pdf`) e filtragem de PDFs |
| `data/` | PDFs de entrada (não versionados, criados automaticamente) |
| `vector_store/` | Índice vetorial persistido localmente (não versionado) |
| `tests/` | 19 testes automatizados com mocks — sem chamadas reais à API OpenAI |
| `Makefile` | Atalhos: `make install`, `make run`, `make test` |
