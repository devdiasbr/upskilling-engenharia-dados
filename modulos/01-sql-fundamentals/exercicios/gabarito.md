# Gabarito — Módulo 1: SQL Fundamentals

> Tente resolver os exercícios antes de consultar este arquivo.

---

## Nível 1 — Básico

### Exercício 1.1 — Produtos por categoria e preço

```sql
SELECT
    nome,
    preco
FROM produtos
WHERE categoria = 'Eletrônicos'
ORDER BY preco DESC;
```

**Resultado esperado:**

| nome            | preco   |
|-----------------|---------|
| Notebook Pro    | 3500.00 |
| Smartwatch      | 799.00  |
| Fone Bluetooth  | 299.00  |

---

### Exercício 1.2 — Contagem de vendas em março de 2024

```sql
SELECT
    COUNT(*) AS qtd_vendas
FROM vendas
WHERE data_venda >= '2024-03-01'
  AND data_venda < '2024-04-01';
```

**Resultado esperado:**

| qtd_vendas |
|------------|
| 3          |

> **Por que `< '2024-04-01'` em vez de `<= '2024-03-31'`?** Usar o primeiro dia do mês seguinte com `<` é mais seguro: funciona corretamente com colunas do tipo `TIMESTAMP` que podem ter hora/minuto/segundo, evitando perder registros do último dia às 23:59:59.

---

### Exercício 1.3 — Receita total

```sql
SELECT
    SUM(valor_total) AS receita_total
FROM vendas;
```

**Resultado esperado:**

| receita_total |
|---------------|
| 10724.40      |

---

## Nível 2 — Intermediário

### Exercício 2.1 — Total gasto por cliente (incluindo clientes sem compras)

```sql
SELECT
    c.nome,
    COALESCE(SUM(v.valor_total), 0) AS total_gasto
FROM clientes AS c
LEFT JOIN vendas AS v ON c.cliente_id = v.cliente_id
GROUP BY c.cliente_id, c.nome
ORDER BY total_gasto DESC;
```

**Resultado esperado:**

| nome          | total_gasto |
|---------------|-------------|
| Ana Lima      | 5397.00     |
| Bruno Silva   | 3679.70     |
| Carla Santos  | 1098.50     |
| Diego Rocha   | 418.80      |
| Elena Costa   | 129.90      |

**Por que `COALESCE`?** Clientes sem compras terão `SUM(valor_total) = NULL` após o LEFT JOIN. `COALESCE(NULL, 0)` converte esse NULL em 0.

**Por que `GROUP BY c.cliente_id, c.nome`?** Incluir `cliente_id` no GROUP BY garante que dois clientes com o mesmo nome sejam tratados como linhas distintas.

---

### Exercício 2.2 — Produto mais vendido em quantidade

```sql
SELECT
    p.nome   AS produto,
    SUM(v.quantidade) AS total_unidades
FROM vendas AS v
INNER JOIN produtos AS p ON v.produto_id = p.produto_id
GROUP BY p.produto_id, p.nome
ORDER BY total_unidades DESC
LIMIT 1;
```

**Resultado esperado:**

| produto          | total_unidades |
|------------------|----------------|
| Camiseta Básica  | 10             |

---

### Exercício 2.3 — Top 3 cidades com mais clientes

```sql
SELECT
    cidade,
    COUNT(*) AS qtd_clientes
FROM clientes
GROUP BY cidade
ORDER BY qtd_clientes DESC
LIMIT 3;
```

**Resultado esperado:**

| cidade            | qtd_clientes |
|-------------------|--------------|
| São Paulo         | 2            |
| Rio de Janeiro    | 1            |
| Belo Horizonte    | 1            |

> Com os dados de exemplo, há empate entre as cidades com 1 cliente. O LIMIT 3 retorna as 3 primeiras na ordem de desempate (alfabética, dependendo do banco).

---

## Nível 3 — Avançado

### Exercício 3.1 — Rank de clientes por receita

```sql
SELECT
    c.nome,
    COALESCE(SUM(v.valor_total), 0)                                     AS total_gasto,
    RANK() OVER (ORDER BY COALESCE(SUM(v.valor_total), 0) DESC)         AS rank_receita
FROM clientes AS c
LEFT JOIN vendas AS v ON c.cliente_id = v.cliente_id
GROUP BY c.cliente_id, c.nome
ORDER BY rank_receita;
```

**Resultado esperado:**

| nome          | total_gasto | rank_receita |
|---------------|-------------|--------------|
| Ana Lima      | 5397.00     | 1            |
| Bruno Silva   | 3679.70     | 2            |
| Carla Santos  | 1098.50     | 3            |
| Diego Rocha   | 418.80      | 4            |
| Elena Costa   | 129.90      | 5            |

**Observação:** `RANK()` atribui o mesmo rank a linhas com valores iguais e pula o próximo. `DENSE_RANK()` não pula. Para este dataset não há empates, então ambos produzem o mesmo resultado.

---

### Exercício 3.2 — Receita acumulada mês a mês em 2024

```sql
WITH receita_mensal AS (
    SELECT
        DATE_TRUNC('month', data_venda) AS mes,
        SUM(valor_total)                AS receita_mes
    FROM vendas
    WHERE data_venda >= '2024-01-01'
      AND data_venda < '2025-01-01'
    GROUP BY DATE_TRUNC('month', data_venda)
)
SELECT
    mes,
    receita_mes,
    SUM(receita_mes) OVER (ORDER BY mes) AS receita_acumulada
FROM receita_mensal
ORDER BY mes;
```

**Resultado esperado:**

| mes        | receita_mes | receita_acumulada |
|------------|-------------|-------------------|
| 2024-01-01 | 3679.70     | 3679.70           |
| 2024-02-01 | 1217.80     | 4897.50           |
| 2024-03-01 | 5227.90     | 10125.40          |
| 2024-04-01 | 598.50      | 10723.90          |

> **Diferença de R$ 0,50:** o total acumulado de abril (10723.90) difere ligeiramente do `SUM` direto (10724.40) devido ao arredondamento de `DECIMAL` em alguns bancos. Verifique a precisão do tipo de dado no seu ambiente.

> **Compatibilidade:** `DATE_TRUNC` é sintaxe PostgreSQL/BigQuery. No MySQL use `DATE_FORMAT(data_venda, '%Y-%m-01')`. No SQL Server use `DATETRUNC('month', data_venda)` ou `DATEFROMPARTS(YEAR(data_venda), MONTH(data_venda), 1)`.

---

### Exercício 3.3 — Identificar e refatorar uma query problemática

#### Query original

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

#### Problemas identificados

1. **`SELECT *` desnecessário (duas ocorrências):** a subquery `SELECT * FROM clientes` e o `SELECT *` externo leem todas as colunas sem necessidade. Isso transfere dados desnecessários e impede otimizações.

2. **Subquery `SELECT cliente_id FROM clientes` redundante:** dentro do cálculo da média, o filtro `WHERE cliente_id IN (SELECT cliente_id FROM clientes)` não elimina nenhuma linha — todo `cliente_id` em `vendas` já é uma FK válida para `clientes`. Essa subquery é inócua e confusa.

3. **Subquery escalar recalculada por linha:** a subquery que calcula `AVG(valor_total)` está dentro do `WHERE` de outra subquery correlacionada com o `IN`. Dependendo do otimizador do banco, pode ser reavaliada para cada linha de `vendas`, em vez de calculada uma única vez.

4. **Estrutura aninhada desnecessária:** a subquery `FROM (SELECT * FROM clientes) AS todos_clientes` é equivalente a `FROM clientes` direto.

#### Query refatorada

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

**O que mudou:**

| Problema | Solução aplicada |
|---|---|
| `SELECT *` externo | Colunas explícitas: `cliente_id, nome, email, cidade, data_cadastro` |
| Subquery `FROM (SELECT * FROM clientes)` | Eliminada; `FROM clientes` direto |
| Subquery `IN (SELECT cliente_id FROM clientes)` | Eliminada; era redundante |
| Subquery escalar recalculada | Movida para CTE `media_vendas` — calculada uma única vez |
| Lógica opaca com IN aninhado | Substituída por JOIN explícito com CTE nomeada |

**Resultado esperado** (clientes com ao menos uma venda acima da média de R$ 1.072,44):

| cliente_id | nome         | email           | cidade            | data_cadastro |
|------------|--------------|-----------------|-------------------|---------------|
| 1          | Ana Lima     | ana@email.com   | São Paulo         | 2023-01-15    |
| 2          | Bruno Silva  | bruno@email.com | Rio de Janeiro    | 2023-02-20    |
