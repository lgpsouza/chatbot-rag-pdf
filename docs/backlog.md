# Backlog — Chatbot RAG com Processamento de PDFs

---

## Release 1 — Core (Carregamento, Busca e Interface)

### Funcionalidades

- [x] **RF01** — Carregar PDFs do diretório `data/`
  - Aceite: todos os `.pdf` presentes são lidos sem erro; diretório vazio retorna lista vazia
- [x] **RF02** — Segmentar documentos em chunks de texto
  - Aceite: chunks com `chunk_size=1000` e `chunk_overlap=200`; chunks vazios são filtrados
- [x] **RF03** — Gerar e persistir embeddings no vectorstore local
  - Aceite: vectorstore criado em `vector_store/` com modelo `text-embedding-3-small`
- [x] **RF04** — Reutilizar vectorstore entre execuções
  - Aceite: segunda inicialização não faz chamadas à API de embeddings
- [x] **RF05** — Interface web Streamlit com campo de pergunta e exibição de resposta
  - Aceite: usuário digita pergunta, resposta é exibida no chat com spinner de loading
- [x] **RF06** — Histórico de mensagens durante a sessão
  - Aceite: mensagens anteriores permanecem visíveis durante a sessão ativa

### Técnico

- [x] **RT01** — Configurar variáveis de ambiente via `.env`
  - Aceite: ausência de `OPENAI_API_KEY` lança `EnvironmentError` antes de qualquer chamada
- [x] **RT02** — Tratar erros da API OpenAI (`RateLimitError`, `APIError`)
  - Aceite: erros exibem mensagem ao usuário sem encerrar o processo
- [x] **RT03** — Declarar modelos explicitamente no código
  - Aceite: `gpt-4o-mini` e `text-embedding-3-small` definidos sem depender de defaults

---

## Release 2 — Qualidade (Testes e Otimizações)

### Funcionalidades

- [x] **RF07** — Alertar quando PDF não contiver texto extraível
  - Aceite: `warnings.warn()` emitido para PDFs de imagem sem OCR
- [x] **RF08** — Validar `data/` vazia na inicialização
  - Aceite: `ValueError` lançado e exibido via `st.warning()` na interface Streamlit

### Técnico

- [x] **RT04** — Cobertura mínima de testes unitários com mocks
  - Aceite: 19 testes passando sem chamadas reais à API; cobertura: `pdf_loader` 100%, `embeddings` 100%, `chatbot` 94%
- [x] **RT05** — Configurar `conftest.py` com variáveis de ambiente de teste
  - Aceite: `OPENAI_API_KEY=sk-fake-test-key` isolada para todos os testes via `autouse`
- [x] **RT06** — Adicionar `pytest-cov` ao projeto
  - Aceite: `pytest --cov=app --cov-report=term-missing` funciona localmente; threshold de 80% para módulos de negócio (interface e CLI excluídos)
- [x] **RT07** — Implementar hash de arquivo para invalidação seletiva do vectorstore
  - Aceite: apenas PDFs novos ou alterados são reprocessados; manifest JSON com MD5 em `vector_store/.manifest.json`

---

## Release 2.1 — Upload de PDFs (adicionado após v0.1)

### Funcionalidades

- [x] **RF10** — Upload de PDFs pela interface Streamlit
  - Aceite: `st.file_uploader` aceita múltiplos PDFs e salva em `data/`; sessão rastreia arquivos já salvos para evitar duplicatas
- [x] **RF11** — Botão "Reindexar documentos"
  - Aceite: apaga o manifest via `invalidar_vectorstore()`, invoca `delete_collection()` para rebuild seguro (sem deletar SQLite), invalida `@st.cache_resource` e força reconstrução; botão fica em destaque quando há arquivos pendentes de indexação

---

## Release 2.2 — Robustez e Segurança (adicionado após v0.2)

### Funcionalidades

- [x] **RF12** — Validar PDFs no upload e na listagem, com remoção automática de inválidos
  - Aceite: `validar_pdf()` detecta arquivos corrompidos e scans sem OCR; aviso amigável exibido; arquivo removido de `data/` automaticamente
- [x] **RF13** — Limite de tamanho no upload de PDFs (50 MB)
  - Aceite: arquivos acima de 50 MB exibem aviso e são ignorados sem salvar em disco
- [x] **RF14** — Proteção contra path traversal no nome do arquivo enviado
  - Aceite: `Path(nome).name` extrai apenas o basename; diretórios relativos (`../`) são silenciosamente descartados

### Técnico

- [x] **RT12** — Makefile com targets `install`, `run` e `test`
  - Aceite: `make install` cria `.venv` e instala dependências; `make run` inicia Streamlit; `make test` executa pytest sem ativar o ambiente manualmente
- [x] **RT13** — Correção de `SQLITE_READONLY_DBMOVED` no Reindexar
  - Aceite: rebuild usa `delete_collection()` em vez de `shutil.rmtree`, evitando mudança de inode no SQLite enquanto o singleton ChromaDB mantém a conexão aberta

---

## Release 3 — Entrega Final (Documentação e Deployment)

### Funcionalidades

- [ ] **RF12** — Histórico de conversa persistido entre sessões
  - Aceite: perguntas e respostas anteriores são carregadas ao reiniciar a interface

### Técnico

- [x] **RT08** — Documentação completa no README
  - Aceite: README cobre stack, instalação via Makefile, uso, troubleshooting, arquitetura Mermaid e roadmap
- [x] **RT09** — Documentação de arquitetura e decisões técnicas
  - Aceite: `docs/` contém escopo, riscos, backlog e estrutura atualizados para v0.2
- [ ] **RT10** — Containerização com Docker
  - Aceite: `docker build` e `docker run` sobem a interface Streamlit sem dependências locais
- [ ] **RT11** — Pipeline CI com GitHub Actions
  - Aceite: testes executados automaticamente a cada push na branch `main`
