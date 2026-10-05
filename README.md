# AI Document Analyzer

API de análise estruturada com contrato validado e providers intercambiáveis. Funciona sem credenciais no modo `mock`; uma integração HTTP opcional permite usar um endpoint compatível com Chat Completions.

## Tecnologias

Python, FastAPI, Pydantic, HTTPX, JSON, python-dotenv e Pytest.

## Funcionalidades

Recebe texto entre 20 e 20.000 caracteres; classifica como `financial`, `technical` ou `general`; retorna resumo, palavras-chave, datas identificadas e avisos; valida o retorno do modelo; converte falhas externas em HTTP 502; registra provider, categoria e tamanho sem registrar conteúdo ou chaves.

## Instalação

Requisitos: Python 3.11 ou superior e acesso à internet para instalar as dependências. Execute na raiz deste repositório. Os comandos abaixo usam PowerShell e não exigem ativar o ambiente virtual.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Em Linux/macOS, use `python3` na criação do ambiente e `.venv/bin/python` no lugar de `.\.venv\Scripts\python.exe`.

## Demonstração sem API paga

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe demo.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 18001 --log-level info
```

`demo.py` lê os dois arquivos fictícios de `samples/` e imprime JSON. Ele utiliza sempre `MockProvider`. A API usa `AI_PROVIDER` e publica [Swagger](http://127.0.0.1:18001/docs).

## Exemplo HTTP

```powershell
$text = Get-Content samples/financial.txt -Raw
$body = @{text=$text} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:18001/analyze -ContentType 'application/json' -Body $body
Invoke-RestMethod -Uri http://127.0.0.1:18001/health
```

Resposta para a amostra financeira:

```json
{"provider":"mock","analysis":{"category":"financial","summary":"FICTITIOUS document: all information is invented. Invoice DEMO-001.","keywords":["invoice","payment","amount"],"dates":["2025-01-20"],"warnings":["Deterministic demonstration: no language model inference was performed."]}}
```

Entrada curta, vazia ou excessiva retorna 422. Provider mal configurado, indisponível ou com JSON inválido retorna 502 com `detail`. `/health` indica que a aplicação responde; não testa disponibilidade externa.

## Provider real opcional

No `.env`, configure `AI_PROVIDER=llm`, `LLM_API_KEY` e `LLM_MODEL`. `LLM_BASE_URL` deve ser HTTPS e apontar para um servidor compatível com `/chat/completions`, `response_format` JSON e a estrutura `choices[0].message.content`. Reinicie a API após alterar configuração.

O provider realiza uma requisição HTTP com timeout de 30 segundos e valida o JSON retornado contra `Analysis`. Não existe dependência de SDK, modelo específico ou credencial no código. O provedor selecionado pode cobrar uso; a chamada envia o texto ao serviço configurado. A integração foi testada com transporte HTTP simulado, sem chamada paga ou avaliação de qualidade de um modelo real.

## Arquitetura

`schemas.py` define entrada e saída; `providers.py` contém o protocolo `Provider`, o mock e o adapter HTTP; `main.py` expõe rotas e centraliza erros; `demo.py` executa as amostras locais; `tests/` verifica comportamento e contratos. Não existe banco de dados: resultados retornam no HTTP ou no terminal.

O mock usa palavras em inglês, prioridade financeira sobre técnica e as duas primeiras frases como resumo. Ele não faz inferência de IA, não interpreta semântica complexa e detecta padrões de datas sem verificar calendário. A resposta o identifica explicitamente. No modo LLM, o documento é tratado como dado não confiável no prompt, mas isso não garante resistência total a prompt injection.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Os testes são locais e não exigem credenciais nem serviços externos.

São cobertos os três tipos de classificação, limites de entrada, configuração inválida, sucesso HTTP simulado, rate limit, envelope inválido e schema inválido.

## Limitações e melhorias futuras

Adicionar autenticação, controle de uso, retry com backoff, métricas, redaction, avaliação de qualidade e políticas de retenção antes de produção. Não há upload de PDF, OCR, RAG, treinamento, streaming ou persistência. A integração exige compatibilidade do servidor com o contrato documentado.

## Documentação adicional

- [Guia de entrevista](INTERVIEW_GUIDE.md)
- [Comandos de publicação](GIT_SETUP.md)
- [Licença MIT](LICENSE)

Todos os dados de demonstração são fictícios. As aplicações foram projetadas para demonstração local; não possuem autenticação de usuários.
