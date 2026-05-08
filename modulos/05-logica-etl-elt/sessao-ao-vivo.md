# Módulo 5 — Sessão ao Vivo (2 horas)

**Tema:** Lógica de ETL/ELT — da teoria ao pipeline robusto

---

## Visão geral

| Bloco | Duração | Formato |
|---|---|---|
| Abertura e contextualização | 10 min | Apresentação |
| Do Módulo 4 ao vocabulário formal | 15 min | Discussão guiada |
| Exercício ao vivo — Ex 5.4 | 70 min | Mãos na massa em grupo |
| Fechamento — prove a idempotência | 25 min | Demonstração + debate |

---

## Bloco 1 — Abertura (10 min)

### O que cobrir

Abrir com a pergunta-chave do módulo:

> "Quando um pipeline de dados quebra às 3h da manhã e alguém precisa reprocessar tudo — o que precisa estar no código para que isso seja seguro?"

**Agenda do dia:**
1. Vocabulário: ETL vs ELT (rápido — vocês já fizeram isso)
2. Extração incremental vs full load
3. Idempotência — o que é e por que salva vidas
4. Logging que ajuda vs logging que atrapalha
5. Exercício ao vivo: construir um pipeline que sobrevive a falhas

**Tom da abertura:** este módulo não traz conceitos abstratos — ele nomeia e formaliza o que vocês já fizeram no Módulo 4, e adiciona as camadas que faltam para um pipeline de produção.

---

## Bloco 2 — Vocês já fizeram ETL: agora têm o vocabulário (15 min)

### Objetivo

Conectar o script que os alunos já escreveram no Módulo 4 com os conceitos formais do Módulo 5. Ninguém começa do zero.

### Roteiro de discussão

**Pergunte ao grupo:**

> "No Módulo 4, quem escreveu um script que lê do `dados.db`, faz alguma transformação e salva o resultado?"

(Levante de mãos ou confirmação no chat.)

> "Isso é ETL. Vocês já sabem fazer ETL. O que o Módulo 5 faz é colocar nome nas decisões que vocês tomaram — e nas que vocês não sabiam que precisavam tomar."

**Três perguntas para provocar reflexão:**

1. **Sobre extração:** "Se vocês rodarem o script de vocês amanhã, ele vai pegar dados novos ou reprocessar tudo do zero? Como ele sabe o que já processou?"
   - Objetivo: mostrar que extração incremental é uma decisão consciente, não automática

2. **Sobre carga:** "Se vocês rodarem o script duas vezes seguidas, o arquivo de saída vai ter o dobro de linhas ou as mesmas linhas?"
   - Objetivo: introduzir idempotência pela prática antes da teoria

3. **Sobre erros:** "Se o banco estiver fora do ar e o script falhar, vocês sabem o que aconteceu? Como?"
   - Objetivo: mostrar que logging não é opcional em produção

**Conectar com as seções do conteúdo:**
- Pergunta 1 → Seção 2 (Extração Incremental)
- Pergunta 2 → Seção 4 e 5 (Estratégias de Carga e Idempotência)
- Pergunta 3 → Seção 6 (Tratamento de Erros e Logging)

**Encerrar o bloco:**
> "ETL vs ELT é uma decisão de arquitetura que depende de onde você transforma os dados. No restante da sessão, vamos trabalhar com ETL puro — Python + SQLite — mas os princípios se aplicam direto ao ELT com BigQuery ou Snowflake."

---

## Bloco 3 — Exercício ao vivo: Ex 5.4 (70 min)

### Objetivo

Construir ao vivo o `etl_idempotente.py` do Exercício 5.4, progressivamente, simulando uma falha no meio do caminho para demonstrar como o logging e o tratamento de erros fazem a diferença.

### Configuração

- Grupos de 3 a 4 pessoas
- Cada grupo abre o arquivo `exercicios/exercicios.md` (Ex 5.3 e 5.4)
- Ambiente: Python + pandas + sqlite3 instalados, `recursos/dados.db` disponível

### Parte 3A — Construindo o pipeline básico (20 min)

Instrução para os grupos:

> "Comecem com o Ex 5.3. Escreva o pipeline no arquivo `exercicios/etl_idempotente.py`. Não se preocupem com logging ainda — foco na estrutura ETL funcionando."

Enquanto os grupos trabalham, circule e observe:
- Qual estratégia de carga cada grupo escolheu? (`append` vs sobrescrever)
- Calcularam `valor_unitario` corretamente?
- Trataram o caso de `quantidade == 0` (divisão por zero)?

**Ponto de parada — 20 min:**
Peça que um grupo compartilhe a tela e mostre o pipeline. Discuta com a turma:
- A estratégia de carga escolhida é idempotente?
- O que acontece se `quantidade` for zero?

### Parte 3B — Adicionando logging (20 min)

Instrução para os grupos:

> "Agora adicionem logging. Cada etapa (extrair, transformar, carregar) deve logar início, fim e volume. Configurem para sair tanto no terminal quanto em `saida/pipeline.log`."

**Perguntas para guiar enquanto trabalham:**
- O que vocês precisariam saber se acordassem às 3h com um alerta de falha?
- Quais informações no log responderiam isso?

**Ponto de parada — 20 min:**
Execute o pipeline de um grupo ao vivo. Mostre o arquivo `saida/pipeline.log` para a turma. Discuta:
- O log conta uma história clara do que aconteceu?
- Vocês conseguem ver quantas linhas foram descartadas?

### Parte 3C — Simulando uma falha (30 min)

Esta é a parte mais importante da sessão. Instrução:

> "Vamos simular um ambiente com problema. Alterem o `CAMINHO_DB` para um caminho inválido e executem."

```python
CAMINHO_DB = "recursos/dados_inexistente.db"
```

**Observe com a turma:**
- O script quebra silenciosamente ou com mensagem clara?
- O arquivo de saída foi sobrescrito com dados inválidos/vazios?
- O log registrou o erro com contexto suficiente?

**Compare dois scripts:**
1. Um grupo que não tem `try/except` — qual é o comportamento?
2. Um grupo que tem `try/except` com `raise` + logging — qual é o comportamento?

**Discuta o anti-padrão silencioso:**

```python
# Anti-padrão — NUNCA faça isso
try:
    df = extrair(caminho_db)
except:
    pass  # silencia o erro — ninguém sabe que falhou
```

> "Um pipeline que falha silenciosamente é mais perigoso do que um que quebra com erro claro. No primeiro caso, você descobre o problema quando o cliente liga reclamando. No segundo, você descobre imediatamente."

**Exercício final do bloco:**
Peça que cada grupo adicione o alerta de qualidade do Ex 5.4:
- Se mais de 5% das linhas forem descartadas → `logger.warning()`

Mostre como simular isso: altere temporariamente a query de extração para retornar apenas metade dos dados, fazendo a limpeza descartar muitas linhas.

---

## Bloco 4 — Fechamento: prove que seu pipeline é idempotente (25 min)

### O desafio final

> "O critério de aceite de um pipeline de produção inclui: provar que ele é idempotente. Como você faz isso?"

### Demonstração ao vivo

Execute o pipeline 3 vezes consecutivas com os mesmos dados:

```bash
python exercicios/etl_idempotente.py
python exercicios/etl_idempotente.py
python exercicios/etl_idempotente.py
```

Mostre que:
1. As três execuções produzem o mesmo número de linhas no resumo
2. O arquivo `saida/vendas_processadas.parquet` tem o mesmo tamanho nas três vezes
3. Leia o arquivo após a terceira execução e mostre que a contagem é idêntica

```python
import pandas as pd
df = pd.read_parquet("saida/vendas_processadas.parquet")
print(f"Linhas no arquivo: {len(df)}")  # deve ser sempre o mesmo número
```

### Debate final com a turma (10 min)

**Pergunta 1:**
> "O pipeline de vocês usa `to_parquet()` para carregar. Se o destino fosse um banco de dados SQLite, como garantiriam idempotência?"

Resposta esperada: upsert com `INSERT OR REPLACE`

**Pergunta 2:**
> "Se vocês precisassem converter este pipeline para ELT — ou seja, carregar raw no destino e transformar lá dentro — o que mudaria?"

Pontos esperados:
- A etapa de extração ficaria mais simples (carrega tudo sem transformar)
- A transformação migraria para SQL/dbt dentro do destino
- O pipeline Python ficaria menor e menos frágil

**Pergunta 3:**
> "Quais informações esse pipeline ainda não loga, mas que seriam úteis em produção?"

Sugestões que podem surgir:
- Quem executou (usuário ou serviço)
- Qual versão do código foi usada
- Hash do arquivo de saída (para detectar mudanças inesperadas)
- Tempo de cada subetapa da transformação

### Encerramento

> "Hoje vocês construíram um pipeline que: sabe de onde veio, sabe o que processou, sabe quantas linhas descartou, avisa quando algo está fora do esperado, não duplica dados ao ser reexecutado, e deixa rastro claro quando falha. Isso é um pipeline de produção."

**Conexão com o próximo módulo:**
> "No Módulo 6, vamos pegar exatamente esse script e colocá-lo dentro de um orquestrador — que vai agendá-lo, monitorar as execuções, retentar automaticamente em caso de falha e alertar quando o SLA não é cumprido. O pipeline que vocês escreveram hoje é a peça central do próximo módulo."

---

## Materiais necessários

- `recursos/dados.db` disponível no repositório
- Python 3.9+ com `pandas` e `pyarrow` instalados
- Editor de código (VS Code recomendado)
- Diretório `saida/` criável no ambiente de cada participante

## Dependências Python

```bash
pip install pandas pyarrow
```
