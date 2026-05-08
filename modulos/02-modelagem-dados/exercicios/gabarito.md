# Gabarito — Módulo 2: Modelagem de Dados

> Consulte este arquivo somente depois de ter tentado resolver os exercícios. Respostas diferentes das apresentadas aqui podem ser igualmente válidas — o importante é a justificativa.

---

## Exercício 2.1 — Identificando e corrigindo violações de normalização

### (a) Violações identificadas

```
pedidos_legado
+----------+------------------+--------------------------------+----------+-----------+
| pedido_id| cliente          | produtos_comprados             | qtd_total| total_r$  |
+----------+------------------+--------------------------------+----------+-----------+
|   1001   | Ana Lima / SP    | Notebook Pro, Mouse USB        |    2     | 3600.00   |
|   1002   | Carlos Braga / RJ| Livro de Python                |    1     |   89.00   |
|   1003   | Ana Lima / SP    | Camiseta Básica, Tênis Run     |    2     |  309.90   |
|   1004   | Marcos Pinto / MG| Notebook Pro                  |    1     | 3500.00   |
+----------+------------------+--------------------------------+----------+-----------+
```

**Violação 1 — 1FN: coluna `produtos_comprados` não é atômica**
A coluna armazena múltiplos valores separados por vírgula ("Notebook Pro, Mouse USB"). Cada célula deve conter um único valor.

**Violação 2 — 1FN: coluna `cliente` mistura nome e estado**
"Ana Lima / SP" contém dois atributos distintos (nome e estado) numa mesma célula. Isso também viola a atomicidade.

**Violação 3 — 1FN / redundância: dados de clientes repetidos**
"Ana Lima / SP" aparece nos pedidos 1001 e 1003. O nome e estado do cliente estão duplicados — qualquer alteração exige atualizar múltiplas linhas.

**Violação 4 — 3FN: `qtd_total` e `total_r$` são derivados**
`qtd_total` é a soma das quantidades dos itens, e `total_r$` pode ser calculado a partir das quantidades e preços. Armazenar valores derivados viola o princípio da 3FN (dependência de outros atributos não-chave, além de criar risco de inconsistência).

**Violação 5 — ausência de identificadores únicos para clientes e produtos**
Não há `cliente_id` nem `produto_id` — sem PKs nas entidades, não é possível garantir unicidade nem criar FKs corretas.

---

### (b) Estrutura normalizada (3FN)

```
clientes
+-----------+------------------+-------+--------+
| cliente_id| nome             | estado| email  |
+-----------+------------------+-------+--------+
|     1     | Ana Lima         | SP    | ...    |
|     2     | Carlos Braga     | RJ    | ...    |
|     3     | Marcos Pinto     | MG    | ...    |
+-----------+------------------+-------+--------+
PK: cliente_id

produtos
+------------+------------------+--------+
| produto_id | nome             | preco  |
+------------+------------------+--------+
|     1      | Notebook Pro     |3500.00 |
|     2      | Mouse USB        | 100.00 |
|     3      | Livro de Python  |  89.00 |
|     4      | Camiseta Básica  |  89.90 |
|     5      | Tênis Run        | 220.00 |
+------------+------------------+--------+
PK: produto_id

pedidos
+-----------+------------+
| pedido_id | cliente_id |
+-----------+------------+
|   1001    |     1      |
|   1002    |     2      |
|   1003    |     1      |
|   1004    |     3      |
+-----------+------------+
PK: pedido_id
FK: cliente_id → clientes(cliente_id)

itens_pedido
+---------+-----------+------------+----------+
| item_id | pedido_id | produto_id | quantidade|
+---------+-----------+------------+----------+
|    1    |   1001    |     1      |    1     |
|    2    |   1001    |     2      |    1     |
|    3    |   1002    |     3      |    1     |
|    4    |   1003    |     4      |    1     |
|    5    |   1003    |     5      |    1     |
|    6    |   1004    |     1      |    1     |
+---------+-----------+------------+----------+
PK: item_id
FK: pedido_id → pedidos(pedido_id)
FK: produto_id → produtos(produto_id)
```

Observe que removemos `qtd_total` e `total_r$` — esses valores são calculados via query:
- `qtd_total` = `SUM(itens_pedido.quantidade)`
- `total_r$` = `SUM(itens_pedido.quantidade * produtos.preco)`

---

### (c) Query que reproduz a visão original

```sql
SELECT
    p.pedido_id,
    c.nome || ' / ' || c.estado AS cliente,
    GROUP_CONCAT(pr.nome, ', ') AS produtos_comprados,
    SUM(ip.quantidade) AS qtd_total,
    SUM(ip.quantidade * pr.preco) AS total_rs
FROM pedidos p
JOIN clientes c ON p.cliente_id = c.cliente_id
JOIN itens_pedido ip ON p.pedido_id = ip.pedido_id
JOIN produtos pr ON ip.produto_id = pr.produto_id
GROUP BY p.pedido_id, c.nome, c.estado
ORDER BY p.pedido_id;
```

> `GROUP_CONCAT` é a função do SQLite equivalente a juntar strings. Em PostgreSQL seria `STRING_AGG(pr.nome, ', ')`.

---

## Exercício 2.2 — Modelagem relacional: sistema de biblioteca

### (a) Entidades e atributos

| Entidade | Atributos |
|---|---|
| `livros` | `livro_id` (PK), `titulo`, `ano_publicacao`, `isbn` |
| `autores` | `autor_id` (PK), `nome` |
| `membros` | `membro_id` (PK), `nome`, `email`, `data_filiacao` |
| `emprestimos` | `emprestimo_id` (PK), `membro_id` (FK), `livro_id` (FK), `data_retirada`, `data_prevista_devolucao`, `data_devolucao_real` |
| `livros_autores` | `livro_id` (FK), `autor_id` (FK) — tabela associativa |

### (b) Relacionamentos e cardinalidades

| Relacionamento | Cardinalidade | Justificativa |
|---|---|---|
| livros ↔ autores | N:M | Um livro pode ter vários autores; um autor escreve vários livros |
| membros → emprestimos | 1:N | Um membro pode ter vários empréstimos ao longo do tempo |
| livros → emprestimos | 1:N | Um livro pode ser emprestado várias vezes (devolução antes do próximo) |

### (c) Diagrama ASCII

```
+------------------+     +---------------------+     +-----------------+
|     livros       |     |   livros_autores    |     |     autores     |
+------------------+     +---------------------+     +-----------------+
| livro_id   (PK)  |<----| livro_id      (FK)  |     | autor_id  (PK)  |
| titulo           |     | autor_id      (FK)  |---->| nome            |
| ano_publicacao   |     +---------------------+     +-----------------+
| isbn             |     PK composta: (livro_id,
+--------+---------+                  autor_id)
         |
        1:N
         |
         v
+------------------+     +-----------------+
|   emprestimos    |     |    membros      |
+------------------+     +-----------------+
| emprestimo_id(PK)|     | membro_id (PK)  |
| membro_id   (FK) |---->| nome            |
| livro_id    (FK) |     | email           |
| data_retirada    |     | data_filiacao   |
| data_prev_devol  |     +-----------------+
| data_devol_real  |     (NULL = não devolvido)
+------------------+
```

**Ponto importante:** `data_devolucao_real` pode ser `NULL` quando o livro ainda está emprestado. Isso é modelagem correta — não crie um valor padrão como "9999-12-31", use `NULL` para representar ausência de informação.

---

## Exercício 2.3 — Transformando o schema relacional em modelo dimensional

### (a) Grão da tabela fato

**Uma linha em `fato_vendas` representa: uma transação de venda de um produto específico por um cliente em uma data específica.**

Esse grão é herdado diretamente do schema atual de `vendas`, onde cada linha já é um único produto vendido.

### (b) Modelo dimensional

```
fato_vendas
+-----------+------------+-----------+----------+-------------+----------+
| venda_sk  | cliente_sk | produto_sk| tempo_sk | valor_total | quantidade|
+-----------+------------+-----------+----------+-------------+----------+
PK: venda_sk (surrogate key gerada pelo DW)
FK: cliente_sk → dim_cliente(cliente_sk)
FK: produto_sk → dim_produto(produto_sk)
FK: tempo_sk  → dim_tempo(tempo_sk)
Métricas: valor_total, quantidade

dim_cliente
+-------------+-----------+-------+-------+---------+---------------+
| cliente_sk  | cliente_id| nome  | email | cidade  | estado        |
+-------------+-----------+-------+-------+---------+---------------+
PK: cliente_sk
Atributos de contexto: cliente_id (chave do sistema de origem), nome, email,
                       cidade, estado

dim_produto
+-------------+-----------+--------------------+-------------------+--------+
| produto_sk  | produto_id| nome               | nome_categoria    | preco  |
+-------------+-----------+--------------------+-------------------+--------+
PK: produto_sk
Atributos de contexto: produto_id (chave de origem), nome, nome_categoria
                       (desnormalizado do join com categorias), preco

dim_tempo
+----------+------------+-----+------+-----------+--------+----------------+
| tempo_sk | data       | dia | mes  | trimestre | ano    | dia_da_semana  |
+----------+------------+-----+------+-----------+--------+----------------+
| 20230101 | 2023-01-01 |  1  |  1   |     1     | 2023   | domingo        |
+----------+------------+-----+------+-----------+--------+----------------+
PK: tempo_sk (formato YYYYMMDD ou inteiro sequencial)
Atributos analíticos: data, dia, mes, trimestre, ano, dia_da_semana,
                      eh_fimdesemana (BOOLEAN)
```

### (c) Diagrama Star Schema

```
               +-------------------+
               |    dim_cliente    |
               +-------------------+
               | cliente_sk (PK)   |
               | cliente_id        |
               | nome              |
               | email             |
               | cidade            |
               | estado            |
               +---------+---------+
                         |
                        FK: cliente_sk
                         |
+----------------+        v                  +-------------------+
|   dim_tempo    |   +------------+          |    dim_produto    |
+----------------+   | fato_vendas|          +-------------------+
| tempo_sk (PK)  |-->| venda_sk   |<---------| produto_sk (PK)   |
| data           |   | cliente_sk |          | produto_id        |
| dia            |   | produto_sk |          | nome              |
| mes            |   | tempo_sk   |          | nome_categoria    |
| trimestre      |   | valor_total|          | preco             |
| ano            |   | quantidade |          +-------------------+
| dia_da_semana  |   +------------+
| eh_fimdesemana |
+----------------+
```

### (d) Query de faturamento por mês e ano

```sql
SELECT
    strftime('%Y', data_venda) AS ano,
    strftime('%m', data_venda) AS mes,
    SUM(valor_total)           AS faturamento_total,
    COUNT(*)                   AS qtd_vendas
FROM vendas
GROUP BY
    strftime('%Y', data_venda),
    strftime('%m', data_venda)
ORDER BY
    ano DESC,
    mes DESC;
```

**Resultado esperado (amostra):**

```
ano  | mes | faturamento_total | qtd_vendas
-----|-----|-------------------|------------
2024 | 12  |    ...            |   ...
2024 | 11  |    ...            |   ...
...
2023 | 01  |    ...            |   ...
```

> Com a `dim_tempo` no DW, essa query seria ainda mais simples e permitiria filtros como `WHERE dia_da_semana = 'sábado'` sem precisar de `strftime`.

---

## Exercício 2.4 — Star Schema vs Snowflake Schema

### (a) Star Schema — `dim_loja` desnormalizada

```
dim_loja
+----------+-------------+----------+-----------+--------+--------+---------+
| loja_sk  | loja_id     | nome_loja| endereco  | cidade | estado | regiao  |
+----------+-------------+----------+-----------+--------+--------+---------+
|    1     |   L001      | Loja SP  | Av. ...   | São Paulo | SP | Sudeste |
|    2     |   L002      | Loja RJ  | Rua ...   | Rio de Janeiro | RJ | Sudeste|
|    3     |   L003      | Loja AM  | ...       | Manaus | AM | Norte   |
+----------+-------------+----------+-----------+--------+--------+---------+
PK: loja_sk
Todos os atributos de hierarquia (cidade, estado, região) estão na mesma tabela.
```

### (b) Snowflake Schema — dimensão normalizada

```
dim_regiao
+-----------+-----------+
| regiao_sk | nome      |
+-----------+-----------+
|     1     | Sudeste   |
|     2     | Norte     |
|     3     | Sul       |
+-----------+-----------+
PK: regiao_sk

dim_estado
+-----------+--------+-----------+
| estado_sk | sigla  | regiao_sk |
+-----------+--------+-----------+
|     1     | SP     |     1     |
|     2     | RJ     |     1     |
|     3     | AM     |     2     |
+-----------+--------+-----------+
PK: estado_sk
FK: regiao_sk → dim_regiao(regiao_sk)

dim_cidade
+-----------+----------------+-----------+
| cidade_sk | nome           | estado_sk |
+-----------+----------------+-----------+
|     1     | São Paulo      |     1     |
|     2     | Rio de Janeiro |     2     |
|     3     | Manaus         |     3     |
+-----------+----------------+-----------+
PK: cidade_sk
FK: estado_sk → dim_estado(estado_sk)

dim_loja (snowflake)
+----------+----------+-----------+-----------+
| loja_sk  | nome_loja| endereco  | cidade_sk |
+----------+----------+-----------+-----------+
|    1     | Loja SP  | Av. ...   |     1     |
|    2     | Loja RJ  | Rua ...   |     2     |
+----------+----------+-----------+-----------+
PK: loja_sk
FK: cidade_sk → dim_cidade(cidade_sk)
```

**Diagrama do snowflake:**
```
dim_regiao <─── dim_estado <─── dim_cidade <─── dim_loja <─── fato_vendas
```

### (c) Recomendação e justificativa

**Recomendação: Star Schema (`dim_loja` desnormalizada).**

Com apenas 1.200 lojas, a redundância de armazenar `cidade`, `estado` e `região` diretamente em `dim_loja` representa um overhead mínimo de armazenamento (na prática, alguns kilobytes extras). Em contrapartida, a equipe de BI ganha consultas diretas do tipo `GROUP BY cidade, estado, regiao` sem nenhum JOIN adicional, o que simplifica as queries no Power BI e melhora a performance.

O snowflake seria justificado se as dimensões tivessem volume muito alto (por exemplo, milhões de lojas) ou se as hierarquias mudassem com frequência e a redundância criasse risco de inconsistência. Como cidades e estados raramente mudam e o volume é pequeno, o custo de manutenção do snowflake (mais tabelas, queries mais complexas, possibilidade de JOINs incompletos) supera qualquer benefício de normalização.

**Regra prática:** em modelagem dimensional, prefira star schema até que haja uma razão técnica clara para snowflake.
