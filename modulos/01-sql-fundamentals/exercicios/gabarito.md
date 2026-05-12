# Gabarito — Módulo 1: SQL Fundamentals

> Tente resolver os exercícios antes de consultar este arquivo.
>
> Todas as queries foram escritas para **SQLite** (`recursos/dados.db`).
> Notas de compatibilidade com outros bancos são indicadas quando relevante.

---

## Nível 1 — Básico

### Exercício 1.1 — Produtos por categoria

```sql
SELECT
    p.nome,
    p.preco
FROM produtos AS p
INNER JOIN categorias AS cat ON p.categoria_id = cat.categoria_id
WHERE cat.nome = 'Eletronicos'
ORDER BY p.preco DESC;
```

**Nota:** o campo `nome` em `categorias` não tem acento ("Eletronicos", não "Eletrônicos") — verifique com `SELECT DISTINCT nome FROM categorias` caso tenha dúvida.

---

### Exercício 1.2 — Contagem de vendas em um período

```sql
SELECT
    COUNT(*) AS qtd_vendas
FROM vendas
WHERE data_venda >= '2024-03-01'
  AND data_venda <  '2024-04-01';
```

> **Por que `< '2024-04-01'` em vez de `<= '2024-03-31'`?** Usar o primeiro dia do mês seguinte com `<` é mais seguro: funciona corretamente com colunas do tipo `TIMESTAMP` que podem ter hora/minuto/segundo, evitando perder registros do último dia às 23:59:59.

---

### Exercício 1.3 — Receita total

```sql
SELECT
    SUM(valor_total) AS receita_total
FROM vendas;
```

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

**Por que `COALESCE`?** Clientes sem compras terão `SUM(valor_total) = NULL` após o LEFT JOIN. `COALESCE(NULL, 0)` converte esse NULL em 0.

**Por que `GROUP BY c.cliente_id, c.nome`?** Incluir `cliente_id` no GROUP BY garante que dois clientes com o mesmo nome sejam tratados como linhas distintas.

---

### Exercício 2.2 — Produto mais vendido em quantidade

```sql
SELECT
    p.nome            AS produto,
    SUM(v.quantidade) AS total_unidades
FROM vendas AS v
INNER JOIN produtos AS p ON v.produto_id = p.produto_id
GROUP BY p.produto_id, p.nome
ORDER BY total_unidades DESC
LIMIT 1;
```

---

### Exercício 2.3 — Top 5 estados com maior receita

```sql
SELECT
    c.estado,
    SUM(v.valor_total) AS receita_total
FROM vendas AS v
INNER JOIN clientes AS c ON v.cliente_id = c.cliente_id
GROUP BY c.estado
ORDER BY receita_total DESC
LIMIT 5;
```

---

## Nível 3 — Avançado

### Exercício 3.1 — Rank de clientes por receita

```sql
WITH totais AS (
    SELECT
        c.cliente_id,
        c.nome,
        COALESCE(SUM(v.valor_total), 0) AS total_gasto
    FROM clientes AS c
    LEFT JOIN vendas AS v ON c.cliente_id = v.cliente_id
    GROUP BY c.cliente_id, c.nome
)
SELECT
    nome,
    total_gasto,
    RANK() OVER (ORDER BY total_gasto DESC) AS rank_receita
FROM totais
ORDER BY rank_receita;
```

**Observação:** `RANK()` atribui o mesmo rank a linhas com valores iguais e pula o próximo. `DENSE_RANK()` não pula. Para clientes com o mesmo total, `DENSE_RANK()` produz uma sequência contínua.

---

### Exercício 3.2 — Receita acumulada mês a mês em 2024

```sql
WITH receita_mensal AS (
    SELECT
        strftime('%Y-%m', data_venda) AS mes,
        SUM(valor_total)              AS receita_mes
    FROM vendas
    WHERE data_venda >= '2024-01-01'
      AND data_venda <  '2025-01-01'
    GROUP BY strftime('%Y-%m', data_venda)
)
SELECT
    mes,
    receita_mes,
    SUM(receita_mes) OVER (ORDER BY mes) AS receita_acumulada
FROM receita_mensal
ORDER BY mes;
```

> **Compatibilidade SQLite:** use `strftime('%Y-%m', data_venda)` para extrair ano e mês.
> Em PostgreSQL/BigQuery use `DATE_TRUNC('month', data_venda)`.
> No MySQL use `DATE_FORMAT(data_venda, '%Y-%m-01')`.
> No SQL Server use `DATEFROMPARTS(YEAR(data_venda), MONTH(data_venda), 1)`.

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

1. **`SELECT *` desnecessário (duas ocorrências):** a subquery `SELECT * FROM clientes` e o `SELECT *` externo leem todas as colunas sem necessidade.

2. **Subquery `SELECT cliente_id FROM clientes` redundante:** dentro do cálculo da média, o filtro `WHERE cliente_id IN (SELECT cliente_id FROM clientes)` não elimina nenhuma linha — todo `cliente_id` em `vendas` já é uma FK válida. Essa subquery é inócua e confusa.

3. **Subquery escalar potencialmente recalculada:** a subquery que calcula `AVG(valor_total)` está aninhada dentro do WHERE. Dependendo do otimizador, pode ser reavaliada para cada linha de `vendas`.

4. **Estrutura aninhada desnecessária:** `FROM (SELECT * FROM clientes) AS todos_clientes` é equivalente a `FROM clientes` diretamente.

#### Query refatorada

```sql
WITH media_vendas AS (
    SELECT AVG(valor_total) AS media_geral
    FROM vendas
),
clientes_acima_da_media AS (
    SELECT DISTINCT v.cliente_id
    FROM vendas AS v, media_vendas AS m
    WHERE v.valor_total > m.media_geral
)
SELECT
    c.cliente_id,
    c.nome,
    c.email,
    c.cidade,
    c.estado,
    c.data_cadastro
FROM clientes AS c
INNER JOIN clientes_acima_da_media AS cam ON c.cliente_id = cam.cliente_id
ORDER BY c.nome;
```

**O que mudou:**

| Problema | Solução aplicada |
|---|---|
| `SELECT *` externo | Colunas explícitas: `cliente_id, nome, email, cidade, estado, data_cadastro` |
| `FROM (SELECT * FROM clientes)` | Eliminado; `FROM clientes` diretamente |
| `IN (SELECT cliente_id FROM clientes)` | Eliminado; era redundante |
| Subquery escalar recalculada | Movida para CTE `media_vendas` — calculada uma única vez |
| Lógica opaca com IN aninhado | Substituída por JOIN explícito com CTEs nomeadas |

> **SQLite:** a sintaxe `FROM vendas AS v, media_vendas AS m` é um cross join implícito que funciona corretamente quando `media_vendas` retorna exatamente uma linha (o que é sempre o caso de `AVG` sem GROUP BY).
