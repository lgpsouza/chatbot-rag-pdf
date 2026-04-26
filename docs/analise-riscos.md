# Análise de Riscos — Chatbot RAG

## 1. Riscos técnicos na integração com OpenAI

- [x] `OPENAI_API_KEY` não é carregada via `load_dotenv()` — a variável pode não estar disponível em runtime
  _Resolvido: `load_dotenv()` chamado em `interface.py` e `main.py` antes de qualquer import da aplicação; `Chatbot.__init__` lança `EnvironmentError` se a chave estiver ausente._
- [x] Sem tratamento de `RateLimitError` ou `APIError` — qualquer falha da API derruba o processo
  _Resolvido: `chatbot.py` captura ambas as exceções e retorna mensagem amigável ao usuário._
- [x] `OpenAIEmbeddings()` e `ChatOpenAI()` sem modelo de embedding explícito — sujeito a mudança de default silenciosa pela OpenAI
  _Resolvido: `text-embedding-3-small` e `gpt-4o-mini` declarados explicitamente._
- [x] Sem timeout configurado nas chamadas — requisições podem travar indefinidamente
  _Resolvido: `ChatOpenAI(timeout=30, max_retries=2)` configurado._

---

## 2. O que pode quebrar em produção com PDFs grandes

- [ ] `loader.load()` carrega o PDF inteiro em memória antes do split — PDFs de centenas de páginas causam pico de RAM
  _Em aberto: streaming de PDF não está no escopo do v0.1._
- [x] `construir_vectorstore()` regera **todos** os embeddings a cada inicialização — custo alto e lentidão ao reiniciar
  _Resolvido: `embeddings.py` verifica `vector_store/` existente e populado antes de chamar a API._
- [x] Sem verificação se `data/` está vazia — o chatbot sobe sem documentos e responde com alucinações
  _Resolvido: `construir_vectorstore()` lança `ValueError` quando a lista de documentos é vazia; instrução anti-alucinação adicionada ao prompt._
- [x] PDFs com texto em imagem (scan) retornam chunks vazios sem aviso — `PyPDFLoader` não faz OCR
  _Resolvido: `pdf_loader.py` filtra chunks vazios e emite `warnings.warn()` com contagem._
- [ ] `chunk_size=1000` fixo — PDFs com tabelas ou layouts complexos podem gerar chunks sem sentido
  _Em aberto: configuração adaptativa de chunk está fora do escopo do v0.1._

---

## 3. Testes mínimos a criar agora

- [x] `test_carregar_pdfs_vazio` — garante comportamento com `data/` sem PDFs (retorna lista vazia)
- [x] `test_carregar_pdfs_retorna_documentos` — verifica que um PDF real gera chunks com conteúdo não vazio
- [x] `test_chatbot_sem_api_key` — confirma erro descritivo quando `OPENAI_API_KEY` está ausente
- [x] `test_perguntar_retorna_string` — mock da chain, valida que `perguntar()` retorna `str` não vazia
- [x] `test_pdf_scan_sem_texto_emite_aviso` — PDF de imagem emite `warnings.warn`, não falha silenciosa
- [x] `test_pdf_malformado_emite_aviso_e_continua` — PDF corrompido é ignorado; demais PDFs continuam sendo processados
- [x] `test_vectorstore_existente_e_reutilizado` — vectorstore populado não aciona `carregar_pdfs()`
- [x] `test_vectorstore_novo_emite_aviso_de_custo` — nova geração de embeddings emite aviso de crédito
- [x] `test_vectorstore_vazio_emite_aviso` — diretório vazio lança `ValueError` com aviso
- [x] `test_construir_vectorstore_sem_permissao_de_escrita` — `PermissionError` quando sem acesso ao diretório
- [x] `test_perguntar_nao_retorna_vazio_em_contexto_pobre` — contexto insuficiente retorna frase informativa
- [x] `test_perguntar_string_vazia` — entrada vazia/espaços retorna "Por favor" sem chamar a chain
- [x] `test_perguntar_string_muito_longa` — pergunta > 4096 chars retorna "Limite de" sem chamar a chain
- [x] `test_rate_limit_retorna_mensagem_amigavel` — `RateLimitError` retorna mensagem sem propagar exceção
- [x] `test_api_error_retorna_mensagem_amigavel` — `APIError` retorna mensagem sem propagar exceção
