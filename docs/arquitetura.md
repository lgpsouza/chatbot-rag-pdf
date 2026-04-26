# Arquitetura — Chatbot RAG com Processamento de PDFs

## Diagrama de Componentes e Fluxo de Dados

```mermaid
flowchart LR
    classDef user   fill:#1a6fa4,stroke:#0d4f74,color:#fff,rx:20
    classDef app    fill:#276749,stroke:#1b4332,color:#fff
    classDef infra  fill:#92400e,stroke:#78350f,color:#fff
    classDef api    fill:#5b21b6,stroke:#3b0764,color:#fff

    User([" Usuário "]):::user

    subgraph APP["  Aplicação  "]
        direction TB
        UI["interface.py\nStreamlit UI"]:::app
        Chatbot["chatbot.py\nRAG Chain"]:::app
        Embeddings["embeddings.py\nVectorStore Builder"]:::app
        Loader["pdf_loader.py\nDocument Processor"]:::app
    end

    subgraph INFRA["  Infraestrutura Local  "]
        direction TB
        VS[("ChromaDB\nvector_store/")]:::infra
        PDF[("PDFs\ndata/")]:::infra
    end

    subgraph OAI["  OpenAI API  "]
        direction TB
        EMB["text-embedding-3-small"]:::api
        LLM["gpt-4o-mini"]:::api
    end

    User       -->|" upload PDF "| UI
    User       -->|" pergunta "| UI
    UI         -->|" salva arquivo "| PDF

    UI         --> Chatbot
    Chatbot    --> Embeddings

    Embeddings -->|" existe? "| VS
    VS         -. " reutiliza " .-> Embeddings

    Embeddings --> Loader
    Loader     -->|" lê chunks "| PDF
    Loader     -->|" gera embeddings "| EMB
    EMB        -->|" vetores "| VS

    Chatbot    -->|" similarity search "| VS
    VS         -->|" chunks relevantes "| Chatbot
    Chatbot    -->|" prompt + contexto "| LLM
    LLM        -->|" resposta "| Chatbot
    Chatbot    -->|" resposta "| UI
    UI         -->|" exibe no chat "| User
```

## Legenda de Cores

| Cor | Camada |
| --- | --- |
| Azul | Usuário |
| Verde | Aplicação (módulos Python) |
| Laranja | Infraestrutura local (disco) |
| Roxo | OpenAI API (nuvem) |
