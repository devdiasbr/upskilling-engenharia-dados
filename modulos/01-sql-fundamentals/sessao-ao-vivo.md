# Roteiro da Sessão ao Vivo — Módulo 1: SQL Fundamentals

**Duração total:** 2 horas
**Formato:** facilitador + participantes com acesso ao banco de dados
**Pré-requisito para os participantes:** ter lido o `conteudo.md` e tentado os exercícios antes da sessão

---

## Abertura — 10 min

**Objetivo:** garantir que todo o grupo está no mesmo patamar técnico antes de avançar.

**Roteiro:**

1. Boas-vindas e apresentação do objetivo da sessão (2 min)
2. Verificação rápida de ambiente: pedir que todos rodem a query abaixo e confirmem que recebem resultado (3 min):

```sql
SELECT COUNT(*) AS total_vendas FROM vendas;
-- Resultado esperado: 10
```

3. Sondagem rápida (levantar a mão ou chat): "Quem tentou todos os exercícios antes de hoje?" (1 min)
4. Apresentar a agenda da sessão (2 min):
   - 30 min de dúvidas abertas sobre o conteúdo
   - 60 min de exercício em grupo ao vivo
   - 20 min de fechamento e preview do próximo módulo

---

## Bloco de Dúvidas — 30 min

**Objetivo:** resolver dúvidas do conteúdo e consolidar conceitos que costumam gerar confusão.

Abrir para perguntas livres, mas ter os tópicos abaixo preparados para preencher o tempo caso as perguntas sejam escassas.

### Tópico 1 — WHERE vs HAVING

Confusão comum: usar `WHERE` para filtrar resultados de agregação.

```sql
-- ERRADO: WHERE não enxerga colunas agregadas
SELECT categoria, SUM(preco) AS total
FROM produtos
WHERE SUM(preco) > 1000  -- erro de sintaxe
GROUP BY categoria;

-- CORRETO: HAVING filtra após o agrupamento
SELECT categoria, SUM(preco) AS total
FROM produtos
GROUP BY categoria
HAVING SUM(preco) > 1000;
```

**Regra prática:** se a condição envolve uma função de agregação (`SUM`, `COUNT`, `AVG`...), use `HAVING`. Se não, use `WHERE`.

### Tópico 2 — CTE vs Subquery

Ambas produzem o mesmo resultado na maioria dos casos. A diferença é na **legibilidade** e **manutenção**.

```sql
-- Com subquery aninhada (difícil de ler)
SELECT nome
FROM clientes
WHERE cliente_id IN (
    SELECT cliente_id
    FROM vendas
    GROUP BY cliente_id
    HAVING SUM(valor_total) > 1000
);

-- Com CTE (fácil de ler e testar em partes)
WITH clientes_valiosos AS (
    SELECT cliente_id
    FROM vendas
    GROUP BY cliente_id
    HAVING SUM(valor_total) > 1000
)
SELECT c.nome
FROM clientes AS c
INNER JOIN clientes_valiosos AS cv ON c.cliente_id = cv.cliente_id;
```

**Orientação para o time:** prefira CTEs em qualquer query com mais de uma camada de lógica.

### Tópico 3 — LEFT JOIN com NULL para "não existe"

Padrão muito usado em análise: encontrar registros que **não têm correspondência** em outra tabela.

```sql
-- Clientes que nunca compraram
SELECT c.nome
FROM clientes AS c
LEFT JOIN vendas AS v ON c.cliente_id = v.cliente_id
WHERE v.venda_id IS NULL;
```

**Armadilha:** usar `WHERE v.cliente_id IS NULL` pode parecer equivalente, mas se `cliente_id` for NOT NULL na tabela `vendas`, o banco pode otimizá-lo de forma diferente. Prefira checar a chave primária da tabela direita (`v.venda_id`).

---

## Exercício em Grupo — 60 min

**Objetivo:** resolver o Exercício 3.3 ao vivo, coletivamente, passando por todas as etapas de análise e refatoração.

### Etapa 1 — Apresentar a query original (10 min)

Exibir a query do Exercício 3.3 e pedir que o grupo a leia em silêncio por 2 minutos:

```sql
SELECT *
FROM (
    SELECT *
    FROM clientes
) AS todos_clientes
WHERE cliente_id IN (
    SELECT cliente_id
    FROM vendas
    WHERE valor_total > (
        SELECT AVG(valor_total)
        FROM vendas
        WHERE cliente_id IN (
            SELECT cliente_id
            FROM clientes
        )
    )
);
```

Perguntar ao grupo:
- "O que essa query faz? Consiga explicar em uma frase."
- "Onde vocês veem desperdício ou redundância?"

Anotar as respostas observadas em lousa/slide colaborativo.

### Etapa 2 — Identificar os problemas coletivamente (15 min)

Guiar o grupo através das perguntas do enunciado do exercício:

1. **`SELECT *` desnecessário:** "Precisamos de todas as colunas aqui? Quais colunas o resultado final precisa?"
2. **`FROM (SELECT * FROM clientes)`:** "O que essa subquery adiciona? Poderíamos usar `FROM clientes` diretamente?"
3. **`WHERE cliente_id IN (SELECT cliente_id FROM clientes)`:** "Todo `cliente_id` em `vendas` já existe em `clientes` (FK). Essa subquery filtra alguma coisa?"
4. **Subquery escalar no `WHERE`:** "Quantas vezes o banco precisa calcular `AVG(valor_total)`? Uma vez? Ou uma vez para cada linha de `vendas`?"

### Etapa 3 — Refatorar juntos (20 min)

Construir a query refatorada ao vivo, passo a passo, com o grupo sugerindo cada parte:

**Passo 1:** Extrair a média para uma CTE:
```sql
WITH media_vendas AS (
    SELECT AVG(valor_total) AS media_geral
    FROM vendas
)
-- continua...
```

**Passo 2:** Identificar os clientes acima da média:
```sql
WITH media_vendas AS (
    SELECT AVG(valor_total) AS media_geral
    FROM vendas
),
clientes_acima_da_media AS (
    SELECT DISTINCT cliente_id
    FROM vendas, media_vendas
    WHERE valor_total > media_vendas.media_geral
)
-- continua...
```

**Passo 3:** Unir com a tabela de clientes e selecionar colunas explícitas:
```sql
WITH media_vendas AS (
    SELECT AVG(valor_total) AS media_geral
    FROM vendas
),
clientes_acima_da_media AS (
    SELECT DISTINCT cliente_id
    FROM vendas, media_vendas
    WHERE valor_total > media_vendas.media_geral
)
SELECT
    c.cliente_id,
    c.nome,
    c.email,
    c.cidade,
    c.data_cadastro
FROM clientes AS c
INNER JOIN clientes_acima_da_media AS cam ON c.cliente_id = cam.cliente_id
ORDER BY c.nome;
```

Executar e confirmar que o resultado é idêntico à query original.

### Etapa 4 — Comparar os planos de execução com EXPLAIN (15 min)

Rodar `EXPLAIN ANALYZE` nas duas versões e comparar lado a lado:

```sql
-- Query original
EXPLAIN ANALYZE
SELECT *
FROM (SELECT * FROM clientes) AS todos_clientes
WHERE cliente_id IN (
    SELECT cliente_id FROM vendas
    WHERE valor_total > (
        SELECT AVG(valor_total) FROM vendas
        WHERE cliente_id IN (SELECT cliente_id FROM clientes)
    )
);
```

```sql
-- Query refatorada
EXPLAIN ANALYZE
WITH media_vendas AS (
    SELECT AVG(valor_total) AS media_geral FROM vendas
),
clientes_acima_da_media AS (
    SELECT DISTINCT cliente_id FROM vendas, media_vendas
    WHERE valor_total > media_vendas.media_geral
)
SELECT c.cliente_id, c.nome, c.email, c.cidade, c.data_cadastro
FROM clientes AS c
INNER JOIN clientes_acima_da_media AS cam ON c.cliente_id = cam.cliente_id
ORDER BY c.nome;
```

**Pontos para chamar atenção no plano:**
- Quantas vezes `AVG(valor_total)` aparece no plano original?
- O otimizador do banco já eliminou alguma das redundâncias automaticamente?
- O número de linhas estimadas é compatível com o resultado?

> **Nota:** com apenas 10 linhas de dados de exemplo, a diferença de tempo real será imperceptível. O exercício serve para criar o hábito de ler planos de execução — o ganho aparece em tabelas grandes.

---

## Fechamento — 20 min

### Resumo do módulo (10 min)

Retomar os objetivos de aprendizagem do `README.md` e checar cada um:

| Objetivo | Coberto por |
|---|---|
| SELECT, WHERE, ORDER BY | Seção 1 + Ex 1.1, 1.2, 1.3 |
| JOINs | Seção 2 + Ex 2.1, 2.2 |
| GROUP BY e agregações | Seção 3 + Ex 2.3 |
| CTEs | Seção 4 + Ex 3.2, 3.3 |
| Window functions | Seção 5 + Ex 3.1, 3.2 |
| Performance básica | Seção 6 + Ex 3.3 |

Perguntar ao grupo:
- "Qual conceito foi o mais novo para vocês?"
- "Qual conceito ainda gera dúvida?"
- "Quem terminou todos os 9 exercícios? Alguém ficou travado em algum?"

### Preview do Módulo 2 (5 min)

O próximo módulo cobre **SQL Avançado** com foco em:
- Window functions mais avançadas (frames, ROWS BETWEEN, NTILE)
- Recursive CTEs
- Tratamento de NULLs e dados sujos
- Queries analíticas para séries temporais

**Recomendação antes do Módulo 2:** revisar o Exercício 3.2 deste módulo e tentar variar o frame da window function (`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` é o padrão — o que muda se você trocar por `RANGE BETWEEN`?).

### Encerramento (5 min)

- Compartilhar link do material (conteudo.md, exercicios.md, gabarito.md)
- Data da próxima sessão
- Canal de dúvidas assíncronas (Slack/Teams)
