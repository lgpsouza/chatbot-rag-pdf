# Análise de Riscos — Chatbot RAG

## 1. Riscos técnicos na integração com OpenAI

- [ ] `OPENAI_API_KEY` não é carregada via `load_dotenv()` — a variável pode não estar disponível em runtime
- [ ] Sem tratamento de `RateLimitError` ou `APIError` — qualquer falha da API derruba o processo
- [ ] `OpenAIEmbeddings()` e `ChatOpenAI()` sem modelo de embedding explícito — sujeito a mudança de default silenciosa pela OpenAI
- [ ] Sem timeout configurado nas chamadas — requisições podem travar indefinidamente

---

## 2. O que pode quebrar em produção com PDFs grandes

- [ ] `loader.load()` carrega o PDF inteiro em memória antes do split — PDFs de centenas de páginas causam pico de RAM
- [ ] `construir_vectorstore()` regera **todos** os embeddings a cada inicialização — custo alto e lentidão ao reiniciar
- [ ] Sem verificação se `data/` está vazia — o chatbot sobe sem documentos e responde com alucinações
- [ ] PDFs com texto em imagem (scan) retornam chunks vazios sem aviso — `PyPDFLoader` não faz OCR
- [ ] `chunk_size=1000` fixo — PDFs com tabelas ou layouts complexos podem gerar chunks sem sentido

---

## 3. Testes mínimos a criar agora

- [ ] `test_carregar_pdfs_vazio` — garante comportamento com `data/` sem PDFs (deve retornar lista vazia ou erro claro)
- [ ] `test_carregar_pdfs_retorna_documentos` — verifica que um PDF real gera chunks com conteúdo não vazio
- [ ] `test_chatbot_sem_api_key` — confirma erro descritivo quando `OPENAI_API_KEY` está ausente
- [ ] `test_perguntar_retorna_string` — mock da chain, valida que `perguntar()` retorna `str` não vazia
- [ ] `test_pdf_scan_sem_texto` — PDF de imagem deve retornar aviso, não resposta silenciosa errada
