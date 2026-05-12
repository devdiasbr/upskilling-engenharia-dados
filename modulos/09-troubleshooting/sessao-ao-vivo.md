# Roteiro da Sessão ao Vivo — Módulo 9: Troubleshooting

**Duração total:** 2 horas  
**Formato:** facilitador + participantes com acesso ao banco SQLite e Python  
**Pré-requisito:** ter lido o `conteudo.md` e tentado os exercícios antes da sessão

---

## Abertura — 10 min

**Objetivo:** conectar o conteúdo do módulo com experiências reais do grupo.

**Pergunta de abertura:**
> "Alguém já foi acordado às 3h por causa de um pipeline quebrado — ou descobriu na manhã seguinte que o dado do dashboard estava errado? O que você fez primeiro?"

Deixe 2–3 pessoas responder. Conecte cada história com um dos três pilares (pipeline / dados / SQL).

**Agenda da sessão:**
- 10 min — abertura
- 30 min — Ex 9.1: pipeline com falha silenciosa (ao vivo)
- 30 min — Ex 9.2: dataset com anomalias (em duplas)
- 30 min — Ex 9.3: query lenta + EXPLAIN (ao vivo)
- 20 min — fechamento da trilha

---

## Bloco 1 — Pipeline com Falha Silenciosa — 30 min

**Objetivo:** experimentar o diagnóstico de uma falha silenciosa usando a metodologia dos 4 passos.

### Dinâmica

1. **Mostrar o pipeline com bug (5 min)**

   Compartilhe a tela com o código do Ex 9.1. Peça que o grupo leia em silêncio por 1 minuto e responda: "Esse pipeline parece correto. O que poderia estar errado?"

   Não revele o bug ainda — deixe o grupo tentar identificar.

2. **Rodar e observar (5 min)**

   Execute o pipeline ao vivo. Mostre que termina sem erro e imprime "Pipeline concluído."

   Pergunte: "Quantas linhas o Parquet tem?"

   ```python
   import pandas as pd
   df = pd.read_parquet("saida/vendas_processadas.parquet")
   print(len(df))  # deve revelar o problema
   ```

3. **Aplicar bisection (10 min)**

   Adicione prints ao vivo, etapa por etapa, até isolar a linha que descarta as linhas:

   ```python
   def transformar(df):
       print(f"entrada: {len(df)}")
       df = df[df['valor_total'] > 10000]
       print(f"após filtro valor: {len(df)}")   # ← aqui está
       ...
   ```

   Quando o grupo identificar a linha, pergunte: "Qual era a intenção do autor?"

4. **Corrigir + prevenir (10 min)**

   - Corrija o filtro ao vivo
   - Adicione logging com volume em cada etapa
   - Mostre como o teste do Parte C teria capturado o bug antes do deploy

**Mensagem para o grupo:**
> "Um pipeline que termina sem exceção não é necessariamente correto. Volume é parte do contrato — e precisa estar no log."

---

## Bloco 2 — Dataset com Anomalias — 30 min

**Objetivo:** praticar classificação de problemas nas 5 dimensões e construir uma função de limpeza.

### Dinâmica

1. **Individual — 5 min**

   Mostre o dataset do Ex 9.2. Cada participante lista os problemas que encontra, sem consultar o gabarito.

2. **Coleta — 10 min**

   Pergunte: "Quantos problemas vocês encontraram?" Vá anotando em lousa/slide.

   Conduza a discussão linha por linha:
   - Linha 2 (`cliente_id` nulo): "Qual dimensão?"
   - Linhas 3–4 (duplicatas): "E aqui?"
   - Linha 5 (`produto_id=999`): "Qual dimensão? Acurácia ou consistência?"
   - Linha 5 (`data_venda=2099`): "E essa data no futuro?"
   - Linha 6 (quantidade e valor negativos): "Qual dimensão?"

3. **Implementar em duplas — 10 min**

   Duplas implementam a função `limpar()`. Compare as implementações — alguém usou uma abordagem diferente para checar `produto_id`?

4. **Validação de volume — 5 min**

   Mostre a função `validar_volume_descartado`. Pergunte:
   > "Se numa run normal você descarta 2% das linhas e de repente descarta 40%, o que isso significa para a fonte?"

**Ponto de discussão importante:**

> "Limpar ou rejeitar? Às vezes a decisão correta não é limpar o dado, mas rejeitar o arquivo inteiro e alertar o time da fonte. Limpeza silenciosa pode mascarar um problema maior."

---

## Bloco 3 — Query Lenta — 30 min

**Objetivo:** desenvolver o hábito de ler `EXPLAIN QUERY PLAN` antes de qualquer otimização.

### Dinâmica

1. **Medir antes (5 min)**

   Execute a query original com `time.time()`. Anote o tempo.

   ```python
   import time, sqlite3, pandas as pd
   conn = sqlite3.connect("recursos/dados.db")
   t0 = time.time()
   df = pd.read_sql(query_original, conn)
   print(f"{time.time()-t0:.3f}s — {len(df)} linhas")
   ```

2. **EXPLAIN ao vivo (10 min)**

   Execute `EXPLAIN QUERY PLAN` na query original. Mostre o output e pergunte: "Quantos SCANs vocês veem?"

   Explique as subqueries correlacionadas: "Esta subquery executa uma vez para cada linha do resultado externo. Com 3.000 linhas, isso significa no mínimo 3.000 execuções adicionais."

3. **Reescrever com CTEs — ao vivo (10 min)**

   Construa a versão com CTEs com o grupo sugerindo cada passo:
   - Primeiro CTE: média geral (calculada uma vez)
   - Segundo CTE: média por cliente (calculada uma vez por cliente)
   - Query final: apenas JOINs

4. **Medir depois + índices (5 min)**

   Crie os índices, meça novamente. Mostre a diferença.

   > "Com 3.000 linhas a diferença parece pequena. A mesma query em produção com 10 milhões de linhas pode ser a diferença entre 2 segundos e 20 minutos."

**Mensagem para o grupo:**
> "Nunca otimize sem medir antes. E nunca declare vitória sem medir depois."

---

## Fechamento da Trilha — 20 min

### Linha do Tempo dos 9 Módulos (10 min)

| Módulo | O que o aluno domina agora |
|--------|---------------------------|
| 1 — SQL | Consultar, filtrar, agregar, CTEs, window functions |
| 2 — Modelagem | Entidades, normalização, chaves, relacionamentos |
| 3 — Formatos | CSV vs JSON vs Parquet — quando usar cada um |
| 4 — Python | pandas + sqlite3, primeiro pipeline ETL |
| 5 — ETL/ELT | Idempotência, logging, falha explícita |
| 6 — Pipelines | Airflow, DAGs, Git para código de pipeline |
| 7 — Armazenamento | Data Lake, Lakehouse, Spark, particionamento |
| 8 — Qualidade | 5 dimensões, TDD, ciclo vermelho-verde |
| **9 — Troubleshooting** | **Reproduzir → Isolar → Corrigir → Prevenir** |

### O que fica (5 min)

Pergunte ao grupo:
- "Qual módulo foi o mais difícil?"
- "Qual conceito vocês já usaram no trabalho desde que começaram a trilha?"
- "O que vocês fariam diferente no pipeline que vocês têm hoje?"

### Próximos Passos (5 min)

A trilha cobre os fundamentos. O próximo nível natural:

| Área | Ferramenta | O que adiciona |
|------|-----------|----------------|
| Qualidade declarativa | Great Expectations, dbt tests | Validações estruturadas em escala |
| Observabilidade | Monte Carlo, Soda | Detecção automática de anomalias |
| Orquestração | Airflow em produção | Multi-tenancy, RBAC, alertas integrados |
| Processamento | PySpark real | Cluster, particionamento, otimização distribuída |
| Troubleshooting avançado | OpenLineage, DataHub | Linhagem de dados — rastrear a origem de qualquer campo |

> "A diferença entre usar essas ferramentas e entendê-las de verdade é ter construído o fundamento na mão. Vocês fizeram isso."
