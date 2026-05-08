# Exercícios — Módulo 1: SQL Fundamentals

Use o dataset de e-commerce em `recursos/datasets/` (tabelas: `clientes`, `produtos`, `vendas`).

Consulte o `schema.md` se precisar relembrar a estrutura das tabelas.

As soluções estão em `gabarito.md` — tente resolver antes de consultá-las.

---

## Nível 1 — Básico

### Exercício 1.1 — Produtos por categoria e preço

Liste todos os produtos da categoria **Eletrônicos**, exibindo o nome e o preço, ordenados do mais caro para o mais barato.

**Colunas esperadas no resultado:** `nome`, `preco`

---

### Exercício 1.2 — Contagem de vendas em março de 2024

Quantas vendas foram realizadas no mês de **março de 2024**?

**Colunas esperadas no resultado:** `qtd_vendas`

---

### Exercício 1.3 — Receita total

Qual é o **valor total** de todas as vendas registradas na tabela `vendas`?

**Colunas esperadas no resultado:** `receita_total`

---

## Nível 2 — Intermediário

### Exercício 2.1 — Total gasto por cliente (incluindo clientes sem compras)

Retorne o nome de cada cliente e o total que ele gastou. Clientes que ainda não fizeram nenhuma compra devem aparecer com `0` no total gasto (não devem ser omitidos).

**Colunas esperadas no resultado:** `nome`, `total_gasto`

**Dica:** pense em qual tipo de JOIN preserva todos os clientes, mesmo sem correspondência em `vendas`.

---

### Exercício 2.2 — Produto mais vendido em quantidade

Qual produto teve o maior número total de **unidades vendidas**? Retorne apenas o produto vencedor.

**Colunas esperadas no resultado:** `produto`, `total_unidades`

---

### Exercício 2.3 — Top 3 cidades com mais clientes

Liste as 3 cidades com o maior número de clientes cadastrados, em ordem decrescente.

**Colunas esperadas no resultado:** `cidade`, `qtd_clientes`

---

## Nível 3 — Avançado

### Exercício 3.1 — Rank de clientes por receita

Retorne o nome de cada cliente, o total que ele gastou e o seu **rank** entre todos os clientes (1 = maior gasto). Inclua todos os clientes, mesmo os que não compraram (total = 0).

**Colunas esperadas no resultado:** `nome`, `total_gasto`, `rank_receita`

**Dica:** use uma window function com `RANK()` ou `DENSE_RANK()`.

---

### Exercício 3.2 — Receita acumulada mês a mês em 2024

Calcule a receita de cada mês de 2024 e a **receita acumulada** até aquele mês (soma progressiva desde janeiro).

**Colunas esperadas no resultado:** `mes`, `receita_mes`, `receita_acumulada`

**Dica:** use uma CTE para agregar por mês e depois aplique uma window function com `SUM() OVER`.

---

### Exercício 3.3 — Identificar e refatorar uma query problemática

A query abaixo foi escrita por um colega e funciona corretamente, mas tem problemas de legibilidade e performance. Sua tarefa é:

1. **Identificar** os problemas da query
2. **Reescrever** a query de forma mais eficiente e legível, mantendo o mesmo resultado

**Query original (problemática):**

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

**O que a query faz:** retorna os clientes que possuem ao menos uma venda com `valor_total` acima da média geral de todas as vendas.

**Perguntas para guiar sua análise:**
- Quais `SELECT *` são desnecessários?
- A subquery `SELECT cliente_id FROM clientes` dentro do `WHERE` é necessária?
- A subquery escalar que calcula a média é calculada uma vez ou repetida para cada linha?
- Como você reescreveria isso usando CTEs?
