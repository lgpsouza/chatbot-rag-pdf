# Revisão de Planejamento — Chatbot RAG

## 1. O que está grande demais para a release inicial (v0.1)?

- **Reranking de chunks** — adiciona latência e complexidade sem validação ainda do pipeline básico
- **Histórico de conversa** — exige gerenciamento de memória; muda a arquitetura da chain atual
- **Interface web (v0.3)** — FastAPI + Streamlit são escopos separados; não pertencem ao MVP CLI
- **Autenticação e Docker (v1.0)** — completamente fora do escopo inicial; risco de over-engineering prematuro

---

## 2. O que está faltando para testabilidade?

- **PDF real de fixture** em `tests/` — todos os testes mocam o loader; nenhum valida integração ponta a ponta
- **Teste de integração com ChromaDB** — `construir_vectorstore()` nunca é exercitada com dados reais
- **Variável de ambiente de teste isolada** — sem `conftest.py` definindo `OPENAI_API_KEY=fake` globalmente, testes dependem do ambiente local
- **Cobertura mínima configurada** — sem `pytest-cov` + threshold, regressões passam silenciosamente
- **Teste do fluxo completo `main.py`** — o loop CLI não tem nenhum teste

---

## 3. Três riscos técnicos a mitigar antes da implementação

- **Custo descontrolado de embeddings** — sem cache efetivo, reprocessar PDFs a cada deploy pode gerar cobranças inesperadas; mitigar com hash de arquivo para invalidação seletiva
- **Vectorstore corrompido em produção** — ChromaDB persiste em disco sem controle de versão; uma reinicialização parcial pode deixar o índice inconsistente; mitigar com flag de rebuild forçado e validação na inicialização
- **Qualidade das respostas não mensurável** — sem métrica de avaliação (ex: RAGAS, hit-rate do retriever), não há como saber se mudanças melhoram ou pioram o chatbot; mitigar adicionando ao menos logging das perguntas e chunks recuperados
