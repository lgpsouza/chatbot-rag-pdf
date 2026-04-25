# Estrutura do Projeto

```
mini_projeto_modulo_01_ufg/
│
├── .env.example              # Variáveis de ambiente (modelo)
├── .gitignore
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── main.py               # Ponto de entrada do chatbot
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
│   ├── estrutura-projeto.md
│   └── analise-riscos.md
│
├── PROMPTS/                  # Prompts utilizados no desenvolvimento
└── docs/
```

---

## Descrição dos Módulos

| Arquivo | Responsabilidade |
|---|---|
| `app/main.py` | Loop de interação CLI com o usuário |
| `app/chatbot.py` | Chain RAG: recuperação + geração de resposta |
| `app/embeddings.py` | Criação e persistência do vectorstore ChromaDB |
| `app/pdf_loader.py` | Carregamento, parsing e chunking dos PDFs |
| `data/` | PDFs de entrada (não versionados) |
| `vector_store/` | Índice vetorial persistido localmente (não versionado) |
| `tests/` | Testes automatizados |
