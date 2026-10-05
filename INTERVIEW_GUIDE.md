# Guia de entrevista — ai-document-analyzer

## Problema, arquitetura e decisões

O problema é integrar análise de documentos sem vincular o fluxo a um provedor único. A rota /analyze valida entrada, resolve Provider e retorna AnalysisResponse. Pydantic verifica estrutura; HTTPX faz integração opcional; o mock demonstra o fluxo local. Não existe banco ou histórico. ProviderError centraliza falhas externas e logs evitam registrar conteúdo. Os testes simulam HTTP para validar sucesso e falhas sem custo. Estude `app/providers.py`, `schemas.py` e `tests/test_analyzer.py`. O mock não executa IA; somente o LLMProvider chama um modelo. Produção exige avaliação, controle de uso, privacidade e autenticação.

## Roteiro de estudo

1. Execute os comandos do [README](README.md) e observe as saídas.
2. Execute os testes e leia os casos antes de alterar as regras.
3. Acompanhe uma entrada desde o contrato até a persistência ou saída.
4. Reproduza uma falha de validação e explique sua resposta.
5. Distinga o que foi implementado, o que foi validado e o que é melhoria futura.

## 15 perguntas com respostas

### 1. O mock usa IA?

Não. É uma rotina determinística por palavras-chave e frases. A saída informa provider=mock e inclui aviso explícito. Ele serve para demonstrar contratos e fluxo sem custo.

### 2. Como o provider é abstraído?

Um Protocol exige nome e método analyze que retorna Analysis. MockProvider e LLMProvider implementam esse contrato; get_provider seleciona o provider pela variável AI_PROVIDER.

### 3. Como o LLM é chamado?

HTTPX envia POST a /chat/completions com modelo, mensagens e modo JSON. O adapter lê choices[0].message.content e valida o JSON com Pydantic.

### 4. Como chaves são protegidas?

A chave é lida de variável de ambiente e usada só no header Authorization. .env é ignorado pelo Git. Logs não contêm conteúdo ou chave. Os testes usam um placeholder sem credencial real.

### 5. Qual o papel de Pydantic na saída?

Impõe categoria enumerada, tamanhos e listas limitadas e rejeita campos extras. Um JSON sintaticamente válido pode falhar no schema e ser convertido em ProviderError.

### 6. Como falhas externas aparecem?

Erros HTTP, envelope inválido e schema inválido viram ProviderError. O handler retorna 502 com mensagem segura. Não existe fallback silencioso para mock.

### 7. Como o timeout funciona?

Cada chamada HTTP limita o tempo de espera em 30 segundos. Não há retry; um timeout falha a análise. Produção pode adicionar backoff com limite de tentativas.

### 8. Como impedir prompt injection?

O prompt instrui o modelo a tratar texto como dados não confiáveis. Isso reduz risco mas não garante proteção. O schema limita formato, sem assegurar veracidade ou resistência semântica.

### 9. Os testes usam uma API paga?

Não. MockTransport intercepta HTTP e fornece respostas artificiais. Os testes verificam contrato, erros e parsing, sem comprovar qualidade de um modelo real.

### 10. Como a classificação mock decide?

Palavras financeiras têm precedência; palavras técnicas vêm em seguida; ausência gera general. O vocabulário é inglês e usa presença de substring, com limitações documentadas.

### 11. As datas extraídas são verificadas?

No mock são padrões YYYY-MM-DD, únicos e limitados a 20. Não há validação de calendário ou contexto. Uma melhoria seria normalização semântica e validação de datas.

### 12. Por que a API recebe texto?

Evita acoplar interpretação com parsing de arquivos. A demonstração lê samples e envia texto; PDF, upload e OCR são extensões futuras não implementadas.

### 13. Há persistência ou retenção?

Não há banco, histórico ou arquivos de resultado na API. A resposta retorna ao cliente. No modo LLM, retenção pelo serviço externo depende do provedor configurado.

### 14. O que os logs registram?

Sucesso registra provider, categoria e número de caracteres; falha registra mensagem sanitizada. Não se registra o texto analisado. Configuração de coleta e retenção operacional é futura.

### 15. Como avaliar a qualidade real?

Criaria dataset fictício com saídas esperadas, mediria classificação, factualidade de resumo e extração, e compararia modelos. Os testes atuais garantem o contrato, não acurácia de IA.

