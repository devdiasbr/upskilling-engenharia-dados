# Conteúdo — Módulo 1: SQL Fundamentals

> Antes de começar, leia o `recursos/schema.md` para entender as tabelas `categorias`, `produtos`, `clientes` e `vendas`.

---

## Como conectar ao banco

O banco SQLite está em `recursos/dados.db`. Caso ainda não tenha criado o banco, rode primeiro:

```bash
python recursos/setup_db.py
```

### Opção 1 — SQLite CLI

```bash
sqlite3 recursos/dados.db
.headers on
.mode column
```

### Opção 2 — Python

```python
import sqlite3
conn = sqlite3.connect('recursos/dados.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM clientes LIMIT 5")
for row in cursor.fetchall():
    print(row)
conn.close()
```

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
    cidade,
    estado
FROM clientes
WHERE cidade = 'São Paulo'
   OR estado = 'SP'
ORDER BY nome ASC;
```

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

No nosso banco:
- `produtos.categoria_id` aponta para `categorias.categoria_id`
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
>
> **SQLite:** não suporta `RIGHT JOIN` nem `FULL JOIN` nativamente. Reescreva invertendo a ordem das tabelas (`RIGHT JOIN A, B` vira `LEFT JOIN B, A`) ou usando `UNION ALL` para o FULL JOIN.

### Exemplo: vendas com nome do cliente, produto e categoria (INNER JOIN)

```sql
SELECT
    v.venda_id,
    c.nome           AS cliente,
    p.nome           AS produto,
    cat.nome         AS categoria,
    v.quantidade,
    v.data_venda,
    v.valor_total
FROM vendas AS v
INNER JOIN clientes  AS c   ON v.cliente_id  = c.cliente_id
INNER JOIN produtos  AS p   ON v.produto_id  = p.produto_id
INNER JOIN categorias AS cat ON p.categoria_id = cat.categoria_id
ORDER BY v.data_venda;
```

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
SELECT cat.nome AS categoria, COUNT(*) AS qtd_produtos
FROM produtos AS p
INNER JOIN categorias AS cat ON p.categoria_id = cat.categoria_id
GROUP BY cat.nome;

-- INCORRETO — p.nome não está no GROUP BY nem agregado
SELECT cat.nome, p.nome, COUNT(*)
FROM produtos AS p
INNER JOIN categorias AS cat ON p.categoria_id = cat.categoria_id
GROUP BY cat.nome;  -- erro em bancos estritos
```

### Filtrando grupos com HAVING

`WHERE` filtra linhas individuais (antes do agrupamento). `HAVING` filtra grupos (depois do agrupamento).

```sql
SELECT cat.nome AS categoria, AVG(p.preco) AS preco_medio
FROM produtos AS p
INNER JOIN categorias AS cat ON p.categoria_id = cat.categoria_id
GROUP BY cat.nome
HAVING AVG(p.preco) > 200;
```

### Exemplo: receita total por categoria

```sql
SELECT
    cat.nome                          AS categoria,
    SUM(v.valor_total)                AS receita_total,
    COUNT(DISTINCT v.venda_id)        AS qtd_vendas,
    ROUND(AVG(v.valor_total), 2)      AS ticket_medio
FROM vendas AS v
INNER JOIN produtos   AS p   ON v.produto_id   = p.produto_id
INNER JOIN categorias AS cat ON p.categoria_id = cat.categoria_id
GROUP BY cat.categoria_id, cat.nome
ORDER BY receita_total DESC;
```

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
LIMIT 10;
```

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
SELECT c.nome, c.cidade, c.estado
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

### Exemplo: rank de clientes por receita total

```sql
WITH receita_por_cliente AS (
    SELECT
        c.cliente_id,
        c.nome,
        c.estado,
        COALESCE(SUM(v.valor_total), 0) AS receita_total
    FROM clientes AS c
    LEFT JOIN vendas AS v ON c.cliente_id = v.cliente_id
    GROUP BY c.cliente_id, c.nome, c.estado
)
SELECT
    nome,
    estado,
    receita_total,
    RANK() OVER (ORDER BY receita_total DESC)        AS rank_geral,
    RANK() OVER (PARTITION BY estado ORDER BY receita_total DESC) AS rank_por_estado
FROM receita_por_cliente
ORDER BY rank_geral;
```

### Exemplo: receita acumulada por mês (SQLite)

Em SQLite, use `strftime` em vez de `DATE_TRUNC`:

```sql
WITH receita_mensal AS (
    SELECT
        strftime('%Y-%m', data_venda) AS mes,
        SUM(valor_total)              AS receita_mes
    FROM vendas
    GROUP BY strftime('%Y-%m', data_venda)
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
        strftime('%Y-%m', data_venda) AS mes,
        SUM(valor_total)              AS receita_mes
    FROM vendas
    GROUP BY strftime('%Y-%m', data_venda)
)
SELECT
    mes,
    receita_mes,
    LAG(receita_mes) OVER (ORDER BY mes)                            AS receita_mes_anterior,
    receita_mes - LAG(receita_mes) OVER (ORDER BY mes)              AS variacao
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

**Por quê:** `SELECT *` transfere dados desnecessários, impede o uso de índices cobrindo colunas e quebra aplicações quando o schema muda.

### 2. Filtre cedo

Aplique condições `WHERE` na menor granularidade possível antes de fazer JOINs ou agregações.

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
CREATE INDEX idx_vendas_data    ON vendas (data_venda);
CREATE INDEX idx_vendas_cliente ON vendas (cliente_id);
CREATE INDEX idx_produtos_cat   ON produtos (categoria_id);
```

**Atenção:** índices aceleram leituras mas podem desacelerar escritas (INSERT/UPDATE). Crie-os com critério.

### 4. EXPLAIN QUERY PLAN (SQLite)

No SQLite, use `EXPLAIN QUERY PLAN` para ver como o banco executará a query:

```sql
EXPLAIN QUERY PLAN
SELECT c.nome, SUM(v.valor_total)
FROM vendas AS v
INNER JOIN clientes AS c ON v.cliente_id = c.cliente_id
GROUP BY c.nome;
```

Procure no resultado por:
- **SCAN**: varredura completa (pode indicar falta de índice)
- **SEARCH ... USING INDEX**: uso de índice (eficiente)

> Em PostgreSQL use `EXPLAIN ANALYZE`. No MySQL use `EXPLAIN FORMAT=JSON`. No BigQuery use `INFORMATION_SCHEMA.JOBS_BY_PROJECT`.
