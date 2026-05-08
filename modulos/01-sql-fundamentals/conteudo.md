# Conteúdo — Módulo 1: SQL Fundamentals

> Antes de começar, leia o `recursos/datasets/schema.md` para entender as tabelas `clientes`, `produtos` e `vendas`.

---

## Seção 1 — SELECT e Filtros Básicos

### Sintaxe fundamental

A estrutura base de qualquer consulta SQL é:

```sql
SELECT coluna1, coluna2
FROM tabela
WHERE condição
ORDER BY coluna [ASC | DESC];
```

- **SELECT**: define quais colunas retornar
- **FROM**: define a tabela de origem
- **WHERE**: filtra as linhas (aplicado antes da agregação)
- **ORDER BY**: ordena o resultado (ASC é o padrão; use DESC para invertido)

### Operadores comuns no WHERE

| Operador | Uso |
|---|---|
| `=` | igualdade exata |
| `<>` ou `!=` | diferente |
| `>`, `<`, `>=`, `<=` | comparações numéricas e de data |
| `BETWEEN a AND b` | intervalo inclusivo |
| `IN (v1, v2, ...)` | lista de valores |
| `LIKE 'padrão%'` | correspondência de texto (`%` = qualquer sequência) |
| `IS NULL` / `IS NOT NULL` | verifica ausência de valor |
| `AND`, `OR`, `NOT` | combinação de condições |

### Exemplo: clientes de São Paulo

```sql
SELECT
    cliente_id,
    nome,
    email,
    cidade
FROM clientes
WHERE cidade = 'São Paulo'
ORDER BY nome ASC;
```

**Resultado esperado** (com os dados de exemplo):

| cliente_id | nome        | email           | cidade     |
|------------|-------------|-----------------|------------|
| 1          | Ana Lima    | ana@email.com   | São Paulo  |
| 4          | Diego Rocha | diego@email.com | São Paulo  |

### Exemplo: vendas de fevereiro de 2024

```sql
SELECT
    venda_id,
    cliente_id,
    produto_id,
    data_venda,
    valor_total
FROM vendas
WHERE data_venda BETWEEN '2024-02-01' AND '2024-02-28'
ORDER BY data_venda;
```

### Boas práticas desde o início

- Liste explicitamente as colunas necessárias — evite `SELECT *` (veremos o motivo na Seção 6)
- Use aliases (`AS`) para clareza: `SELECT valor_total AS receita`
- Comente queries complexas com `--` ou `/* */`

---

## Seção 2 — JOINs

### Por que precisamos de JOIN?

Os dados estão distribuídos em tabelas separadas para evitar redundância. O JOIN combina linhas de tabelas diferentes com base em uma condição, geralmente uma chave estrangeira.

No nosso dataset:
- `vendas.cliente_id` aponta para `clientes.cliente_id`
- `vendas.produto_id` aponta para `produtos.produto_id`

### Tipos de JOIN

| Tipo | O que retorna |
|---|---|
| `INNER JOIN` | Somente linhas com correspondência nas duas tabelas |
| `LEFT JOIN` | Todas as linhas da tabela esquerda; NULL onde não há correspondência à direita |
| `RIGHT JOIN` | Todas as linhas da tabela direita; NULL onde não há correspondência à esquerda |
| `FULL JOIN` | Todas as linhas de ambas as tabelas; NULL onde não há correspondência em nenhum lado |

> **Dica:** `INNER JOIN` e `JOIN` são equivalentes. `LEFT JOIN` e `LEFT OUTER JOIN` também.

### Exemplo: vendas com nome do cliente e produto (INNER JOIN)

```sql
SELECT
    v.venda_id,
    c.nome       AS cliente,
    p.nome       AS produto,
    v.quantidade,
    v.data_venda,
    v.valor_total
FROM vendas AS v
INNER JOIN clientes AS c ON v.cliente_id = c.cliente_id
INNER JOIN produtos AS p ON v.produto_id = p.produto_id
ORDER BY v.data_venda;
```

**Resultado esperado** (primeiras linhas):

| venda_id | cliente     | produto          | quantidade | data_venda | valor_total |
|----------|-------------|------------------|------------|------------|-------------|
| 1        | Ana Lima    | Notebook Pro     | 1          | 2024-01-10 | 3500.00     |
| 2        | Bruno Silva | Camiseta Básica  | 3          | 2024-01-15 | 179.70      |
| 3        | Ana Lima    | Fone Bluetooth   | 1          | 2024-02-01 | 299.00      |

### Exemplo: clientes SEM compras (LEFT JOIN com IS NULL)

```sql
SELECT
    c.cliente_id,
    c.nome,
    c.email
FROM clientes AS c
LEFT JOIN vendas AS v ON c.cliente_id = v.cliente_id
WHERE v.venda_id IS NULL;
```

**Como funciona:** o LEFT JOIN preserva todos os clientes. Para aqueles sem venda, as colunas de `vendas` ficam NULL. O filtro `WHERE v.venda_id IS NULL` mantém somente esses casos.

> Com os dados de exemplo, todos os 5 clientes possuem ao menos uma compra, então o resultado seria vazio. Experimente inserir um cliente sem venda para testar.

---

## Seção 3 — Agregações e GROUP BY

### Funções de agregação

| Função | Descrição |
|---|---|
| `COUNT(*)` | conta todas as linhas |
| `COUNT(coluna)` | conta valores não-NULL |
| `SUM(coluna)` | soma os valores |
| `AVG(coluna)` | média dos valores |
| `MAX(coluna)` | maior valor |
| `MIN(coluna)` | menor valor |

### Regra do GROUP BY

> Toda coluna no SELECT que **não** estiver dentro de uma função de agregação **deve** aparecer no GROUP BY.

```sql
-- CORRETO
SELECT categoria, COUNT(*) AS qtd_produtos
FROM produtos
GROUP BY categoria;

-- INCORRETO — nome não está no GROUP BY nem agregado
SELECT categoria, nome, COUNT(*)
FROM produtos
GROUP BY categoria;  -- erro em bancos estritos
```

### Filtrando grupos com HAVING

`WHERE` filtra linhas individuais (antes do agrupamento). `HAVING` filtra grupos (depois do agrupamento).

```sql
SELECT categoria, AVG(preco) AS preco_medio
FROM produtos
GROUP BY categoria
HAVING AVG(preco) > 200;
```

### Exemplo: receita total por categoria

```sql
SELECT
    p.categoria,
    SUM(v.valor_total)            AS receita_total,
    COUNT(DISTINCT v.venda_id)    AS qtd_vendas,
    ROUND(AVG(v.valor_total), 2)  AS ticket_medio
FROM vendas AS v
INNER JOIN produtos AS p ON v.produto_id = p.produto_id
GROUP BY p.categoria
ORDER BY receita_total DESC;
```

**Resultado esperado:**

| categoria    | receita_total | qtd_vendas | ticket_medio |
|--------------|---------------|------------|--------------|
| Eletrônicos  | 9995.00       | 6          | 1665.83      |
| Roupas       | 728.90        | 4          | 182.23       |

---

## Seção 4 — CTEs (Common Table Expressions)

### O que são CTEs?

Uma CTE é uma consulta nomeada e temporária definida com a cláusula `WITH`, que pode ser referenciada na query principal como se fosse uma tabela.

```sql
WITH nome_da_cte AS (
    -- query aqui
)
SELECT *
FROM nome_da_cte;
```

### Por que usar CTEs?

- **Legibilidade:** quebra queries longas em etapas nomeadas
- **Reutilização:** a mesma CTE pode ser referenciada múltiplas vezes na query principal
- **Debugging:** cada CTE pode ser testada isoladamente
- **Alternativa a subqueries:** mais fácil de ler e manter

### Exemplo: top clientes por receita usando CTE

```sql
WITH receita_por_cliente AS (
    SELECT
        cliente_id,
        SUM(valor_total)  AS receita_total,
        COUNT(venda_id)   AS qtd_compras
    FROM vendas
    GROUP BY cliente_id
)
SELECT
    c.nome,
    r.receita_total,
    r.qtd_compras
FROM receita_por_cliente AS r
INNER JOIN clientes AS c ON r.cliente_id = c.cliente_id
ORDER BY r.receita_total DESC
LIMIT 3;
```

**Resultado esperado:**

| nome        | receita_total | qtd_compras |
|-------------|---------------|-------------|
| Ana Lima    | 5397.00       | 3           |
| Bruno Silva | 3679.70       | 2           |
| Carla Santos| 1098.50       | 2           |

### CTEs encadeadas

Você pode definir múltiplas CTEs separadas por vírgula:

```sql
WITH
receita_por_cliente AS (
    SELECT cliente_id, SUM(valor_total) AS receita_total
    FROM vendas
    GROUP BY cliente_id
),
clientes_premium AS (
    SELECT cliente_id
    FROM receita_por_cliente
    WHERE receita_total > 1000
)
SELECT c.nome, c.cidade
FROM clientes AS c
INNER JOIN clientes_premium AS cp ON c.cliente_id = cp.cliente_id;
```

---

## Seção 5 — Window Functions

### O que são window functions?

Window functions calculam um valor para cada linha **com base em um conjunto de linhas relacionadas** (a "janela"), sem colapsar as linhas como o GROUP BY faz.

| GROUP BY | Window Function |
|---|---|
| Retorna uma linha por grupo | Retorna todas as linhas originais |
| Agrega e elimina linhas | Mantém as linhas e adiciona uma coluna calculada |

Sintaxe geral:

```sql
FUNÇÃO() OVER (
    PARTITION BY coluna_de_agrupamento  -- opcional
    ORDER BY coluna_de_ordenação        -- opcional (obrigatório para ranking e frames)
)
```

### Principais funções

| Função | Descrição |
|---|---|
| `ROW_NUMBER()` | Número sequencial único por partição |
| `RANK()` | Rank com lacunas em caso de empate |
| `DENSE_RANK()` | Rank sem lacunas em caso de empate |
| `LAG(col, n)` | Valor da linha n posições antes |
| `LEAD(col, n)` | Valor da linha n posições adiante |
| `SUM() OVER (...)` | Soma acumulada ou por partição |
| `AVG() OVER (...)` | Média por partição |

### Exemplo: média de preço por categoria e rank por preço

```sql
SELECT
    nome,
    categoria,
    preco,
    ROUND(AVG(preco) OVER (PARTITION BY categoria), 2)  AS preco_medio_categoria,
    RANK() OVER (PARTITION BY categoria ORDER BY preco DESC) AS rank_preco_na_categoria
FROM produtos
ORDER BY categoria, rank_preco_na_categoria;
```

**Resultado esperado:**

| nome             | categoria   | preco   | preco_medio_categoria | rank_preco_na_categoria |
|------------------|-------------|---------|----------------------|-------------------------|
| Notebook Pro     | Eletrônicos | 3500.00 | 1532.67              | 1                       |
| Smartwatch       | Eletrônicos | 799.00  | 1532.67              | 2                       |
| Fone Bluetooth   | Eletrônicos | 299.00  | 1532.67              | 3                       |
| Calça Jeans      | Roupas      | 129.90  | 94.90                | 1                       |
| Camiseta Básica  | Roupas      | 59.90   | 94.90                | 2                       |

### Exemplo: receita acumulada por mês

```sql
WITH receita_mensal AS (
    SELECT
        DATE_TRUNC('month', data_venda) AS mes,
        SUM(valor_total) AS receita_mes
    FROM vendas
    GROUP BY DATE_TRUNC('month', data_venda)
)
SELECT
    mes,
    receita_mes,
    SUM(receita_mes) OVER (ORDER BY mes) AS receita_acumulada
FROM receita_mensal
ORDER BY mes;
```

### Exemplo: variação de vendas mês a mês com LAG

```sql
WITH receita_mensal AS (
    SELECT
        DATE_TRUNC('month', data_venda) AS mes,
        SUM(valor_total) AS receita_mes
    FROM vendas
    GROUP BY DATE_TRUNC('month', data_venda)
)
SELECT
    mes,
    receita_mes,
    LAG(receita_mes) OVER (ORDER BY mes) AS receita_mes_anterior,
    receita_mes - LAG(receita_mes) OVER (ORDER BY mes) AS variacao
FROM receita_mensal
ORDER BY mes;
```

---

## Seção 6 — Performance Básica

### Por que performance importa?

Em produção, tabelas têm milhões ou bilhões de linhas. Uma query mal escrita pode:
- Bloquear outros processos
- Consumir memória excessiva
- Demorar horas quando poderia demorar segundos

### 1. Evite SELECT *

```sql
-- Ruim: lê todas as colunas, inclusive as desnecessárias
SELECT * FROM vendas;

-- Bom: lê somente o necessário
SELECT venda_id, cliente_id, valor_total FROM vendas;
```

**Por quê:** `SELECT *` transfere dados desnecessários pela rede, impede o uso de índices cobrindo colunas e quebra aplicações quando o schema muda.

### 2. Filtre cedo

Aplique condições `WHERE` na menor granularidade possível antes de fazer JOINs ou agregações. Em queries com subqueries ou CTEs, mova os filtros para dentro da CTE.

```sql
-- Menos eficiente: agrupa tudo e depois filtra
WITH tudo AS (
    SELECT cliente_id, SUM(valor_total) AS total
    FROM vendas
    GROUP BY cliente_id
)
SELECT * FROM tudo WHERE total > 1000;

-- Mais eficiente: filtra antes de entrar na CTE quando possível
WITH vendas_2024 AS (
    SELECT cliente_id, valor_total
    FROM vendas
    WHERE data_venda >= '2024-01-01'
)
SELECT cliente_id, SUM(valor_total)
FROM vendas_2024
GROUP BY cliente_id;
```

### 3. Índices

Índices aceleram buscas por coluna evitando varredura completa da tabela (full table scan). São criados automaticamente em chaves primárias; para outras colunas usadas em `WHERE`, `JOIN ON` ou `ORDER BY`, pode ser necessário criá-los manualmente:

```sql
CREATE INDEX idx_vendas_data ON vendas (data_venda);
CREATE INDEX idx_vendas_cliente ON vendas (cliente_id);
```

**Atenção:** índices aceleram leituras mas podem desacelerar escritas (INSERT/UPDATE). Crie-os com critério.

### 4. EXPLAIN e EXPLAIN ANALYZE

Use `EXPLAIN` para ver o plano de execução de uma query sem executá-la. Use `EXPLAIN ANALYZE` para executar e ver os tempos reais.

```sql
EXPLAIN ANALYZE
SELECT c.nome, SUM(v.valor_total)
FROM vendas AS v
INNER JOIN clientes AS c ON v.cliente_id = c.cliente_id
GROUP BY c.nome;
```

Procure no resultado por:
- **Seq Scan**: varredura completa (pode indicar falta de índice)
- **Index Scan**: uso de índice (eficiente)
- **Hash Join / Nested Loop**: estratégia de JOIN escolhida pelo otimizador
- **rows**: estimativa de linhas processadas em cada etapa

> `EXPLAIN ANALYZE` está disponível no PostgreSQL. MySQL usa `EXPLAIN FORMAT=JSON`. BigQuery usa `INFORMATION_SCHEMA.JOBS_BY_PROJECT`.
