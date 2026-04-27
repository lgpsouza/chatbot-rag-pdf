# Escopo do MVP — Chatbot RAG com Processamento de PDFs

## Objetivo

Desenvolver um chatbot conversacional com interface web (Streamlit) capaz de responder perguntas em linguagem natural sobre o conteúdo de documentos PDF, utilizando Retrieval-Augmented Generation (RAG) com embeddings semânticos e modelos de linguagem da OpenAI.

---

## Requisitos Funcionais

| ID | Requisito |
| --- | --- |
| RF01 | O sistema deve carregar documentos PDF a partir de um diretório local (`data/`) |
| RF02 | O sistema deve segmentar os documentos em chunks de texto para indexação |
| RF03 | O sistema deve gerar embeddings semânticos dos chunks e persistir em vectorstore local |
| RF04 | O sistema deve reutilizar o vectorstore já existente sem reprocessar os PDFs |
| RF05 | O sistema deve receber perguntas via interface web Streamlit e exibir respostas no chat |
| RF06 | O sistema deve manter o histórico de mensagens durante a sessão |
| RF07 | O sistema deve recuperar os chunks mais relevantes para a pergunta recebida |
| RF08 | O sistema deve gerar respostas fundamentadas nos chunks recuperados |
| RF09 | O sistema deve alertar quando um PDF não contiver texto extraível (scan sem OCR) |

---

## Requisitos Não Funcionais

| ID | Requisito |
| --- | --- |
| RNF01 | A chave de API (`OPENAI_API_KEY`) deve ser carregada via arquivo `.env`, nunca exposta no código |
| RNF02 | Erros da API OpenAI (`RateLimitError`, `APIError`) devem ser tratados e exibidos ao usuário sem encerrar o processo |
| RNF03 | O modelo de linguagem utilizado deve ser `gpt-4o-mini` e o modelo de embeddings `text-embedding-3-small`, ambos declarados explicitamente |
| RNF04 | O vectorstore deve ser persistido localmente em `vector_store/` e ignorado pelo controle de versão |
| RNF05 | As chamadas à API devem ter timeout máximo de 30 segundos e até 2 tentativas automáticas |
| RNF06 | O ambiente de execução deve ser Python 3.11+ com dependências isoladas em `.venv` |
| RNF07 | Todos os módulos da aplicação devem possuir testes unitários com mocks, sem chamadas reais à API |

---

## Requisitos adicionados após v0.1

| ID | Requisito |
| --- | --- |
| RF10 | O sistema deve permitir o upload de PDFs diretamente pela interface Streamlit, salvando-os em `data/` |
| RF11 | O sistema deve disponibilizar um botão "Reindexar documentos" que reconstrói o vectorstore após novos uploads |

## Requisitos adicionados após v0.2

| ID | Requisito |
| --- | --- |
| RF12 | O sistema deve validar PDFs no upload e na listagem, exibindo aviso amigável e removendo automaticamente arquivos corrompidos ou sem texto selecionável |
| RF13 | O sistema deve limitar o tamanho dos PDFs enviados a 50 MB por arquivo, ignorando os que excederem |
| RF14 | O sistema deve sanitizar o nome do arquivo enviado para evitar path traversal (`Path(nome).name`) |
| RT12 | O projeto deve disponibilizar um `Makefile` com targets `install`, `run` e `test` |
| RT13 | O rebuild do vectorstore deve usar `delete_collection()` em vez de deletar o arquivo SQLite, evitando `SQLITE_READONLY_DBMOVED` |

---

## Fora de Escopo (v0.1)

- API REST ou backend separado
- Histórico de conversa persistido entre sessões
- Reranking ou re-scoring dos chunks recuperados
- Suporte a formatos além de PDF (DOCX, HTML, imagens)
- OCR para PDFs baseados em imagem
- Autenticação de usuários
- Deploy em nuvem ou containerização (Docker)
- Monitoramento, logging estruturado e observabilidade

---

## Critérios de Aceite do MVP

- [x] O chatbot responde perguntas sobre o conteúdo de ao menos um PDF válido
- [x] O vectorstore é reutilizado entre execuções sem reprocessar os PDFs
- [x] O histórico de mensagens é exibido corretamente durante a sessão Streamlit
- [x] Perguntas sem resposta nos documentos retornam mensagem informativa, não alucinação silenciosa
- [x] PDFs sem texto exibem aviso em vez de falha silenciosa
- [x] Ausência de `OPENAI_API_KEY` gera erro descritivo antes de qualquer chamada à API
- [x] Todos os testes unitários passam sem chamadas reais à API OpenAI (19/19 passando)
- [x] Usuário pode fazer upload de PDFs pela interface sem acesso manual ao sistema de arquivos
- [x] Botão "Reindexar" reconstrói o vectorstore e reinicia o chatbot com os novos documentos
- [x] PDFs inválidos (corrompidos ou scans sem OCR) são rejeitados com aviso e removidos automaticamente de `data/`
- [x] Upload de arquivo acima de 50 MB exibe aviso e não salva o arquivo
- [x] Nomes de arquivo com path traversal são sanitizados silenciosamente
- [x] `make install`, `make run` e `make test` funcionam sem ativar `.venv` manualmente
