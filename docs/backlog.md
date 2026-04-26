# Backlog — Chatbot RAG com Processamento de PDFs

---

## Release 1 — Core (Carregamento e Busca)

### Funcionalidades

- [ ] **RF01** — Carregar PDFs do diretório `data/`
  - Aceite: todos os `.pdf` presentes são lidos sem erro; diretório vazio retorna lista vazia
- [ ] **RF02** — Segmentar documentos em chunks de texto
  - Aceite: chunks com `chunk_size=1000` e `chunk_overlap=200`; chunks vazios são filtrados
- [ ] **RF03** — Gerar e persistir embeddings no vectorstore local
  - Aceite: vectorstore criado em `vector_store/` com modelo `text-embedding-3-small`
- [ ] **RF04** — Reutilizar vectorstore entre execuções
  - Aceite: segunda inicialização não faz chamadas à API de embeddings
- [ ] **RF05** — Receber perguntas via terminal e retornar respostas
  - Aceite: pergunta em linguagem natural retorna resposta baseada nos documentos indexados
- [ ] **RF06** — Encerrar sessão com comando "sair"
  - Aceite: processo termina normalmente ao digitar "sair"

### Técnico

- [ ] **RT01** — Configurar variáveis de ambiente via `.env`
  - Aceite: ausência de `OPENAI_API_KEY` lança `EnvironmentError` antes de qualquer chamada
- [ ] **RT02** — Tratar erros da API OpenAI (`RateLimitError`, `APIError`)
  - Aceite: erros exibem mensagem ao usuário sem encerrar o processo
- [ ] **RT03** — Declarar modelos explicitamente no código
  - Aceite: `gpt-4o-mini` e `text-embedding-3-small` definidos sem depender de defaults

---

## Release 2 — Qualidade (Testes e Otimizações)

### Funcionalidades

- [ ] **RF07** — Alertar quando PDF não contiver texto extraível
  - Aceite: `warnings.warn()` emitido para PDFs de imagem sem OCR
- [ ] **RF08** — Validar `data/` vazia na inicialização
  - Aceite: `ValueError` descritivo quando não há documentos para indexar

### Técnico

- [ ] **RT04** — Cobertura mínima de testes unitários com mocks
  - Aceite: 5 testes passando sem chamadas reais à API; cobertura ≥ 80%
- [ ] **RT05** — Configurar `conftest.py` com variáveis de ambiente de teste
  - Aceite: `OPENAI_API_KEY=fake` isolada para todos os testes
- [ ] **RT06** — Adicionar `pytest-cov` com threshold mínimo
  - Aceite: `pytest --cov=app --cov-fail-under=80` passa no CI
- [ ] **RT07** — Implementar hash de arquivo para invalidação seletiva do vectorstore
  - Aceite: apenas PDFs novos ou alterados são reprocessados

---

## Release 3 — Entrega Final (Documentação e Deployment)

### Funcionalidades

- [ ] **RF09** — Histórico de conversa (memória de contexto)
  - Aceite: perguntas subsequentes consideram o contexto das anteriores

### Técnico

- [ ] **RT08** — Documentação completa no README
  - Aceite: README cobre instalação, uso, variáveis de ambiente e exemplos
- [ ] **RT09** — Documentação de arquitetura e decisões técnicas
  - Aceite: `docs/` contém escopo, riscos, backlog e estrutura atualizados
- [ ] **RT10** — Containerização com Docker
  - Aceite: `docker build` e `docker run` executam o chatbot sem dependências locais
- [ ] **RT11** — Pipeline CI com GitHub Actions
  - Aceite: testes executados automaticamente a cada push na branch `main`
