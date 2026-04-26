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
  - Aceite: 15 testes passando sem chamadas reais à API; cobertura: `pdf_loader` 100%, `embeddings` 100%, `chatbot` 94%
- [x] **RT05** — Configurar `conftest.py` com variáveis de ambiente de teste
  - Aceite: `OPENAI_API_KEY=sk-fake-test-key` isolada para todos os testes via `autouse`
- [x] **RT06** — Adicionar `pytest-cov` ao projeto
  - Aceite: `pytest --cov=app --cov-report=term-missing` funciona localmente; threshold de 80% para módulos de negócio (interface e CLI excluídos)
- [ ] **RT07** — Implementar hash de arquivo para invalidação seletiva do vectorstore
  - Aceite: apenas PDFs novos ou alterados são reprocessados

---

## Release 3 — Entrega Final (Documentação e Deployment)

### Funcionalidades

- [ ] **RF09** — Histórico de conversa persistido entre sessões
  - Aceite: perguntas e respostas anteriores são carregadas ao reiniciar a interface

### Técnico

- [ ] **RT08** — Documentação completa no README
  - Aceite: README cobre instalação, uso, variáveis de ambiente e exemplos
- [ ] **RT09** — Documentação de arquitetura e decisões técnicas
  - Aceite: `docs/` contém escopo, riscos, backlog e estrutura atualizados
- [ ] **RT10** — Containerização com Docker
  - Aceite: `docker build` e `docker run` sobem a interface Streamlit sem dependências locais
- [ ] **RT11** — Pipeline CI com GitHub Actions
  - Aceite: testes executados automaticamente a cada push na branch `main`
