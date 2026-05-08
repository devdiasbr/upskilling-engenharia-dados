# Upskilling — Fundamentos de Engenharia de Dados: Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o material completo da trilha de upskilling em fundamentos de engenharia de dados — 8 módulos sequenciais com conteúdo teórico, exercícios práticos e roteiro de sessão ao vivo.

**Architecture:** Cada módulo é uma pasta independente com README (objetivos), conteúdo teórico, exercícios com gabarito e roteiro para sessão ao vivo. Um dataset reutilizável serve de base para os exercícios práticos de todos os módulos.

**Tech Stack:** Markdown, SQL, Python (pandas), arquivos de dados CSV/JSON/Parquet como exemplos práticos.

---

## Estrutura de Arquivos

```
modulos/
  01-sql-fundamentals/
    README.md
    conteudo.md
    exercicios/
      exercicios.md
      gabarito.md
    sessao-ao-vivo.md
  02-modelagem-dados/
    ...
  03-formatos-dados/
    ...
  04-python-dados/
    ...
  05-logica-etl-elt/
    ...
  06-engenharia-pipelines/
    ...
  07-armazenamento-processamento/
    ...
  08-qualidade-observabilidade/
    ...
recursos/
  datasets/
    vendas.csv          # dataset principal reutilizado em todos os módulos
    schema.md           # descrição das tabelas e campos
  cheatsheets/
    sql-cheatsheet.md
    python-cheatsheet.md
```

---

## Tarefa 0: Setup do Projeto

**Arquivos:**
- Criar: `recursos/datasets/schema.md`
- Criar: `recursos/datasets/vendas.csv`
- Criar: `recursos/datasets/clientes.csv`
- Criar: `recursos/datasets/produtos.csv`

- [ ] **Passo 1: Criar o schema do dataset**

Criar `recursos/datasets/schema.md` com o seguinte conteúdo:

```markdown
# Dataset — Loja de E-commerce

Dataset fictício reutilizado em todos os módulos da trilha.

## Tabelas

### clientes
| coluna         | tipo    | descrição                        |
|----------------|---------|----------------------------------|
| cliente_id     | INTEGER | identificador único              |
| nome           | VARCHAR | nome completo                    |
| email          | VARCHAR | email de contato                 |
| cidade         | VARCHAR | cidade de residência             |
| data_cadastro  | DATE    | data de cadastro na plataforma   |

### produtos
| coluna         | tipo    | descrição                        |
|----------------|---------|----------------------------------|
| produto_id     | INTEGER | identificador único              |
| nome           | VARCHAR | nome do produto                  |
| categoria      | VARCHAR | categoria (Eletrônicos, Roupas…) |
| preco          | DECIMAL | preço unitário                   |

### vendas
| coluna         | tipo    | descrição                        |
|----------------|---------|----------------------------------|
| venda_id       | INTEGER | identificador único              |
| cliente_id     | INTEGER | FK → clientes                    |
| produto_id     | INTEGER | FK → produtos                    |
| quantidade     | INTEGER | unidades vendidas                |
| data_venda     | DATE    | data da transação                |
| valor_total    | DECIMAL | quantidade × preço               |
```

- [ ] **Passo 2: Criar os arquivos CSV de exemplo**

Criar `recursos/datasets/clientes.csv`:
```csv
cliente_id,nome,email,cidade,data_cadastro
1,Ana Lima,ana@email.com,São Paulo,2023-01-15
2,Bruno Silva,bruno@email.com,Rio de Janeiro,2023-02-20
3,Carla Santos,carla@email.com,Belo Horizonte,2023-03-10
4,Diego Rocha,diego@email.com,São Paulo,2023-04-05
5,Elena Costa,elena@email.com,Curitiba,2023-05-18
```

Criar `recursos/datasets/produtos.csv`:
```csv
produto_id,nome,categoria,preco
1,Notebook Pro,Eletrônicos,3500.00
2,Camiseta Básica,Roupas,59.90
3,Fone Bluetooth,Eletrônicos,299.00
4,Calça Jeans,Roupas,129.90
5,Smartwatch,Eletrônicos,799.00
```

Criar `recursos/datasets/vendas.csv`:
```csv
venda_id,cliente_id,produto_id,quantidade,data_venda,valor_total
1,1,1,1,2024-01-10,3500.00
2,2,2,3,2024-01-15,179.70
3,1,3,1,2024-02-01,299.00
4,3,5,1,2024-02-14,799.00
5,4,2,2,2024-02-20,119.80
6,2,1,1,2024-03-05,3500.00
7,5,4,1,2024-03-12,129.90
8,1,5,2,2024-03-20,1598.00
9,3,2,5,2024-04-01,299.50
10,4,3,1,2024-04-10,299.00
```

---

## Tarefa 1: Módulo 1 — SQL Fundamentals

**Arquivos:**
- Criar: `modulos/01-sql-fundamentals/README.md`
- Criar: `modulos/01-sql-fundamentals/conteudo.md`
- Criar: `modulos/01-sql-fundamentals/exercicios/exercicios.md`
- Criar: `modulos/01-sql-fundamentals/exercicios/gabarito.md`
- Criar: `modulos/01-sql-fundamentals/sessao-ao-vivo.md`

- [ ] **Passo 1: Criar README do módulo**

Criar `modulos/01-sql-fundamentals/README.md`:

```markdown
# Módulo 1 — SQL Fundamentals

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Escrever queries para consultar e filtrar dados com SELECT, WHERE, ORDER BY
- Combinar dados de múltiplas tabelas com diferentes tipos de JOIN
- Agregar e sumarizar dados com GROUP BY e funções de agregação
- Usar CTEs para organizar queries complexas
- Usar window functions para cálculos sobre partições de dados
- Identificar e evitar problemas básicos de performance em queries

## Pré-requisitos

Nenhum. Este é o módulo inicial da trilha.

## Duração Estimada

8–12 horas de estudo + exercícios

## Dataset

Usaremos o dataset de e-commerce em `recursos/datasets/`. Leia o `schema.md` antes de começar.
```

- [ ] **Passo 2: Criar conteúdo teórico**

Criar `modulos/01-sql-fundamentals/conteudo.md` com as seguintes seções e exemplos usando o dataset:

```markdown
# SQL Fundamentals — Conteúdo

## 1. SELECT e Filtros Básicos

SQL (Structured Query Language) é a linguagem padrão para consultar bancos de dados relacionais.

### Sintaxe básica

```sql
SELECT coluna1, coluna2
FROM tabela
WHERE condição
ORDER BY coluna ASC|DESC;
```

### Exemplo: buscar clientes de São Paulo

```sql
SELECT nome, email
FROM clientes
WHERE cidade = 'São Paulo'
ORDER BY nome;
```

## 2. JOINs

JOINs combinam dados de duas ou mais tabelas com base em uma relação.

| Tipo       | Retorna                                           |
|------------|---------------------------------------------------|
| INNER JOIN | apenas linhas com correspondência em ambas        |
| LEFT JOIN  | todas da esquerda + correspondências da direita   |
| RIGHT JOIN | todas da direita + correspondências da esquerda   |
| FULL JOIN  | todas as linhas de ambas, com NULL onde não casa  |

### Exemplo: vendas com nome do cliente e produto

```sql
SELECT
    v.venda_id,
    c.nome AS cliente,
    p.nome AS produto,
    v.valor_total
FROM vendas v
INNER JOIN clientes c ON v.cliente_id = c.cliente_id
INNER JOIN produtos p ON v.produto_id = p.produto_id;
```

### Exemplo: clientes SEM compras (LEFT JOIN)

```sql
SELECT c.nome, v.venda_id
FROM clientes c
LEFT JOIN vendas v ON c.cliente_id = v.cliente_id
WHERE v.venda_id IS NULL;
```

## 3. Agregações e GROUP BY

Funções de agregação calculam um valor sobre um conjunto de linhas.

| Função  | Descrição              |
|---------|------------------------|
| COUNT() | conta linhas           |
| SUM()   | soma valores           |
| AVG()   | média                  |
| MAX()   | maior valor            |
| MIN()   | menor valor            |

### Exemplo: receita total por categoria

```sql
SELECT
    p.categoria,
    SUM(v.valor_total) AS receita_total,
    COUNT(v.venda_id) AS total_vendas
FROM vendas v
INNER JOIN produtos p ON v.produto_id = p.produto_id
GROUP BY p.categoria
ORDER BY receita_total DESC;
```

**Regra:** toda coluna no SELECT que não é função de agregação DEVE estar no GROUP BY.

## 4. CTEs (Common Table Expressions)

CTEs organizam queries complexas em blocos nomeados, melhorando legibilidade.

```sql
WITH receita_por_cliente AS (
    SELECT
        cliente_id,
        SUM(valor_total) AS total_gasto
    FROM vendas
    GROUP BY cliente_id
)
SELECT
    c.nome,
    r.total_gasto
FROM receita_por_cliente r
INNER JOIN clientes c ON r.cliente_id = c.cliente_id
ORDER BY r.total_gasto DESC;
```

## 5. Window Functions

Window functions calculam valores sobre uma "janela" de linhas relacionadas, sem colapsar o resultado como o GROUP BY faz.

```sql
SELECT
    nome,
    categoria,
    preco,
    AVG(preco) OVER (PARTITION BY categoria) AS media_categoria,
    RANK() OVER (PARTITION BY categoria ORDER BY preco DESC) AS rank_preco
FROM produtos;
```

Funções comuns: `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LAG()`, `LEAD()`, `SUM() OVER`, `AVG() OVER`.

## 6. Performance Básica

- **Evite SELECT ***: especifique apenas as colunas que precisa
- **Filtre cedo**: coloque condições no WHERE, não depois do JOIN
- **Índices**: colunas usadas em JOIN e WHERE se beneficiam de índices
- **EXPLAIN/EXPLAIN ANALYZE**: mostra o plano de execução da query — use para investigar queries lentas
```

- [ ] **Passo 3: Criar exercícios práticos**

Criar `modulos/01-sql-fundamentals/exercicios/exercicios.md`:

```markdown
# Exercícios — SQL Fundamentals

Use o dataset em `recursos/datasets/`. Você pode usar SQLite, DuckDB, ou qualquer banco que preferir.

## Nível 1 — Básico

**Ex 1.1** Liste todos os produtos da categoria "Eletrônicos", ordenados por preço decrescente.

**Ex 1.2** Quantas vendas foram realizadas em março de 2024?

**Ex 1.3** Qual o valor total de todas as vendas?

## Nível 2 — Intermediário

**Ex 2.1** Liste o nome de cada cliente e o total que ele gastou em compras. Inclua clientes que nunca compraram (exiba 0 para eles).

**Ex 2.2** Qual produto vendeu mais unidades no total? Mostre nome do produto e total de unidades.

**Ex 2.3** Liste as 3 cidades com mais clientes cadastrados.

## Nível 3 — Avançado

**Ex 3.1** Para cada cliente, mostre: nome, total gasto, e o rank dele entre todos os clientes por valor gasto (1 = maior gasto).

**Ex 3.2** Calcule a receita acumulada mês a mês em 2024 (receita do mês + todos os meses anteriores).

**Ex 3.3** Identifique o problema desta query e reescreva-a de forma mais eficiente:

```sql
SELECT *
FROM (
    SELECT cliente_id, SUM(valor_total) as total
    FROM vendas
    GROUP BY cliente_id
) sub
INNER JOIN (
    SELECT *
    FROM clientes
) c ON sub.cliente_id = c.cliente_id
WHERE sub.total > (SELECT AVG(valor_total) FROM vendas);
```
```

- [ ] **Passo 4: Criar gabarito**

Criar `modulos/01-sql-fundamentals/exercicios/gabarito.md`:

```markdown
# Gabarito — SQL Fundamentals

## Nível 1

**Ex 1.1**
```sql
SELECT nome, preco
FROM produtos
WHERE categoria = 'Eletrônicos'
ORDER BY preco DESC;
```

**Ex 1.2**
```sql
SELECT COUNT(*) AS total_vendas
FROM vendas
WHERE data_venda >= '2024-03-01'
  AND data_venda < '2024-04-01';
```

**Ex 1.3**
```sql
SELECT SUM(valor_total) AS receita_total
FROM vendas;
```

## Nível 2

**Ex 2.1**
```sql
SELECT
    c.nome,
    COALESCE(SUM(v.valor_total), 0) AS total_gasto
FROM clientes c
LEFT JOIN vendas v ON c.cliente_id = v.cliente_id
GROUP BY c.cliente_id, c.nome
ORDER BY total_gasto DESC;
```

**Ex 2.2**
```sql
SELECT
    p.nome,
    SUM(v.quantidade) AS total_unidades
FROM vendas v
INNER JOIN produtos p ON v.produto_id = p.produto_id
GROUP BY p.produto_id, p.nome
ORDER BY total_unidades DESC
LIMIT 1;
```

**Ex 2.3**
```sql
SELECT cidade, COUNT(*) AS total_clientes
FROM clientes
GROUP BY cidade
ORDER BY total_clientes DESC
LIMIT 3;
```

## Nível 3

**Ex 3.1**
```sql
SELECT
    c.nome,
    SUM(v.valor_total) AS total_gasto,
    RANK() OVER (ORDER BY SUM(v.valor_total) DESC) AS ranking
FROM clientes c
LEFT JOIN vendas v ON c.cliente_id = v.cliente_id
GROUP BY c.cliente_id, c.nome;
```

**Ex 3.2**
```sql
WITH receita_mensal AS (
    SELECT
        DATE_TRUNC('month', data_venda) AS mes,
        SUM(valor_total) AS receita_mes
    FROM vendas
    WHERE data_venda >= '2024-01-01'
    GROUP BY 1
)
SELECT
    mes,
    receita_mes,
    SUM(receita_mes) OVER (ORDER BY mes) AS receita_acumulada
FROM receita_mensal;
```

**Ex 3.3** — Problemas na query original:
1. `SELECT *` nas duas subqueries traz colunas desnecessárias
2. Subquery de clientes desnecessária — é só um `SELECT *` sem transformação
3. Subquery escalar no WHERE recalcula a média para cada linha

Versão corrigida:
```sql
WITH media_gasto AS (
    SELECT AVG(valor_total) AS media FROM vendas
),
gasto_por_cliente AS (
    SELECT cliente_id, SUM(valor_total) AS total
    FROM vendas
    GROUP BY cliente_id
)
SELECT
    c.nome,
    g.total
FROM gasto_por_cliente g
INNER JOIN clientes c ON g.cliente_id = c.cliente_id
CROSS JOIN media_gasto m
WHERE g.total > m.media;
```
```

- [ ] **Passo 5: Criar roteiro da sessão ao vivo**

Criar `modulos/01-sql-fundamentals/sessao-ao-vivo.md`:

```markdown
# Sessão ao Vivo — Módulo 1: SQL Fundamentals

**Duração:** 2 horas
**Formato:** Abertura → Dúvidas → Exercício em grupo → Fechamento

---

## Abertura (10 min)
- Verificar: todos conseguiram rodar as queries do conteúdo?
- Dificuldades mais comuns identificadas antes da sessão?

## Bloco de Dúvidas (30 min)
Perguntas abertas. Temas que costumam gerar dúvida:
- Diferença entre WHERE e HAVING
- Quando usar CTE vs subquery
- Por que LEFT JOIN com NULL não equivale a NOT IN em todos os casos

## Exercício em Grupo (60 min)
Resolver ao vivo o **Ex 3.3** (refatoração de query):
1. Pedir para alguém ler a query original em voz alta
2. Identificar os problemas em grupo (não dar a resposta de imediato)
3. Refatorar juntos, explicando cada decisão
4. Mostrar o EXPLAIN de ambas as versões se o ambiente permitir

## Fechamento (20 min)
- Resumo dos pontos principais
- Preview do Módulo 2: Modelagem de Dados
- Tirar dúvidas pendentes
```

---

## Tarefa 2: Módulo 2 — Modelagem de Dados

**Arquivos:**
- Criar: `modulos/02-modelagem-dados/README.md`
- Criar: `modulos/02-modelagem-dados/conteudo.md`
- Criar: `modulos/02-modelagem-dados/exercicios/exercicios.md`
- Criar: `modulos/02-modelagem-dados/exercicios/gabarito.md`
- Criar: `modulos/02-modelagem-dados/sessao-ao-vivo.md`

- [ ] **Passo 1: Criar README**

```markdown
# Módulo 2 — Modelagem de Dados

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Identificar entidades, atributos e relacionamentos em um domínio de negócio
- Aplicar normalização (1FN, 2FN, 3FN) e entender quando desnormalizar faz sentido
- Desenhar um modelo dimensional com tabelas fato e dimensão
- Reconhecer star schema e snowflake schema e seus trade-offs
- Decidir qual tipo de modelagem usar dado um contexto

## Pré-requisito

Módulo 1 — SQL Fundamentals

## Duração Estimada

8–10 horas
```

- [ ] **Passo 2: Criar conteúdo teórico**

Criar `modulos/02-modelagem-dados/conteudo.md` com seções:

```markdown
# Modelagem de Dados — Conteúdo

## 1. Modelagem Relacional

O modelo relacional organiza dados em tabelas com relacionamentos explícitos via chaves.

**Conceitos fundamentais:**
- **Entidade:** objeto do mundo real (Cliente, Produto, Venda)
- **Atributo:** propriedade da entidade (nome, preço, data)
- **Chave primária (PK):** identificador único de cada linha
- **Chave estrangeira (FK):** referência à PK de outra tabela

### Cardinalidade
- **1:1** — um cliente tem um cadastro de endereço principal
- **1:N** — um cliente pode ter várias vendas
- **N:M** — um pedido pode ter vários produtos, e um produto pode estar em vários pedidos (resolvido com tabela associativa)

## 2. Normalização

Normalização é o processo de organizar dados para reduzir redundância e garantir integridade.

### 1ª Forma Normal (1FN)
- Cada célula deve ter um único valor atômico
- Sem grupos repetidos

❌ Errado:
```
cliente_id | produtos_comprados
1          | Notebook, Fone
```
✅ Correto: usar tabela separada para produtos.

### 2ª Forma Normal (2FN)
- Atende 1FN
- Todos os atributos não-chave dependem da chave primária COMPLETA (relevante em PKs compostas)

### 3ª Forma Normal (3FN)
- Atende 2FN
- Nenhum atributo não-chave depende de outro atributo não-chave

**Quando desnormalizar?** Em cenários de leitura intensiva (relatórios, dashboards), a desnormalização reduz JOINs e melhora performance. É uma decisão consciente, não um erro.

## 3. Modelagem Dimensional

Otimizada para análise e relatórios. Pensada para responder perguntas de negócio.

**Componentes:**
- **Tabela Fato:** armazena eventos ou transações mensuráveis (vendas, cliques, pedidos). Contém métricas numéricas e FKs para dimensões.
- **Tabela Dimensão:** descreve o contexto do evento (quem, o quê, quando, onde). Contém atributos descritivos.

### Star Schema
Tabela fato no centro, dimensões ao redor. Simples e performático.

```
         dim_tempo
             |
dim_cliente — fato_vendas — dim_produto
             |
         dim_local
```

### Snowflake Schema
Dimensões normalizadas (subdimensões). Economiza espaço, mas adiciona JOINs.

**Quando usar cada um:**
- Star Schema: padrão para a maioria dos casos, melhor performance, mais simples de entender
- Snowflake: quando dimensões têm muita redundância e armazenamento é crítico

## 4. Aplicando ao Dataset

O dataset de e-commerce já segue um modelo relacional simples. Transformá-lo em dimensional:

```
fato_vendas
├── venda_id (PK)
├── cliente_id (FK → dim_cliente)
├── produto_id (FK → dim_produto)
├── tempo_id (FK → dim_tempo)
├── quantidade
└── valor_total

dim_cliente: cliente_id, nome, cidade
dim_produto: produto_id, nome, categoria, preco
dim_tempo: tempo_id, data, ano, mes, trimestre, dia_semana
```
```

- [ ] **Passo 3: Criar exercícios**

Criar `modulos/02-modelagem-dados/exercicios/exercicios.md`:

```markdown
# Exercícios — Modelagem de Dados

## Ex 2.1 — Identificar violações de normalização

A tabela abaixo viola a 1FN. Identifique o problema e proponha a estrutura correta:

```
pedido_id | cliente | produtos                        | total
1         | Ana     | Notebook (1x), Fone (2x)        | 3898.00
2         | Bruno   | Camiseta (3x)                   | 179.70
```

## Ex 2.2 — Desenhar modelo relacional

Um sistema de biblioteca precisa registrar: livros, autores, empréstimos e membros. Um livro pode ter múltiplos autores. Um membro pode ter múltiplos empréstimos.

Desenhe (em texto ou ASCII) o modelo entidade-relacionamento com tabelas, PKs, FKs e cardinalidades.

## Ex 2.3 — Transformar relacional em dimensional

Dado o modelo relacional do dataset de e-commerce (clientes, produtos, vendas), projete um modelo dimensional com:
- 1 tabela fato
- Pelo menos 3 dimensões (incluindo uma dimensão de tempo)

Liste os campos de cada tabela e justifique suas escolhas.

## Ex 2.4 — Star vs Snowflake

Você está construindo um DW para uma rede de lojas com 500 cidades, 50 estados e 5 regiões. A dimensão de localização tem muita redundância.

Modele a dimensão de localização como:
a) Star schema (desnormalizado)
b) Snowflake schema (normalizado)

Qual você escolheria e por quê?
```

- [ ] **Passo 4: Criar gabarito**

Criar `modulos/02-modelagem-dados/exercicios/gabarito.md`:

```markdown
# Gabarito — Modelagem de Dados

## Ex 2.1

Problema: coluna `produtos` contém múltiplos valores (viola 1FN).

Solução:
```
pedidos: pedido_id, cliente_id, total
itens_pedido: item_id, pedido_id, produto_id, quantidade
clientes: cliente_id, nome
produtos: produto_id, nome, preco
```

## Ex 2.2

```
livros: livro_id (PK), titulo, isbn, ano_publicacao
autores: autor_id (PK), nome, nacionalidade
livro_autor: livro_id (FK), autor_id (FK)  ← tabela associativa N:M
membros: membro_id (PK), nome, email, data_cadastro
emprestimos: emprestimo_id (PK), membro_id (FK), livro_id (FK), data_emprestimo, data_devolucao
```

## Ex 2.3

```
fato_vendas: venda_id, cliente_id, produto_id, tempo_id, quantidade, valor_total

dim_cliente: cliente_id, nome, email, cidade
dim_produto: produto_id, nome, categoria, preco_atual
dim_tempo: tempo_id, data, ano, mes, nome_mes, trimestre, dia_semana
```

Justificativa: dim_tempo é criada sinteticamente a partir das datas de venda — permite análises por período sem cálculos na query.

## Ex 2.4

**Star Schema (desnormalizado):**
```
dim_localizacao: local_id, cidade, estado, regiao
```
500 cidades × dados de estado e região repetidos = redundância, mas queries simples.

**Snowflake Schema (normalizado):**
```
dim_cidade: cidade_id, nome, estado_id (FK)
dim_estado: estado_id, nome, regiao_id (FK)
dim_regiao: regiao_id, nome
```

**Escolha:** Star Schema na maioria dos casos. A redundância de estados e regiões é pequena comparada à complexidade adicionada pelos JOINs extras no Snowflake. Snowflake faz sentido se o volume for massivo e o armazenamento for crítico.
```

- [ ] **Passo 5: Criar roteiro da sessão ao vivo**

Criar `modulos/02-modelagem-dados/sessao-ao-vivo.md`:

```markdown
# Sessão ao Vivo — Módulo 2: Modelagem de Dados

**Duração:** 2 horas

## Abertura (10 min)
- Dúvidas rápidas sobre o conteúdo

## Bloco de Dúvidas (20 min)
Temas comuns:
- "Quando normalizar vs desnormalizar?"
- Diferença prática entre star e snowflake schema
- O que é uma slowly changing dimension (preview do próximo nível)

## Exercício em Grupo (70 min)
**Ex 2.3 ao vivo:** transformar o dataset de e-commerce em modelo dimensional.
1. Cada pessoa propõe sua versão (5 min individual)
2. Discutir diferenças entre as propostas
3. Chegar em consenso sobre o modelo final
4. Discutir: "e se quiséssemos rastrear mudanças de preço de produto ao longo do tempo?"

## Fechamento (20 min)
- Revisão do modelo final acordado
- Preview: Módulo 3 — Formatos de Dados
```

---

## Tarefa 3: Módulo 3 — Formatos de Dados

**Arquivos:**
- Criar: `modulos/03-formatos-dados/README.md`
- Criar: `modulos/03-formatos-dados/conteudo.md`
- Criar: `modulos/03-formatos-dados/exercicios/exercicios.md`
- Criar: `modulos/03-formatos-dados/exercicios/gabarito.md`
- Criar: `modulos/03-formatos-dados/sessao-ao-vivo.md`

- [ ] **Passo 1: Criar README**

```markdown
# Módulo 3 — Formatos de Dados

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Explicar as diferenças entre CSV, JSON, Parquet, Avro e Delta
- Escolher o formato adequado dado um cenário
- Ler e escrever cada formato com Python
- Entender por que Parquet e Delta são padrão em ambientes de dados modernos

## Pré-requisito

Módulos 1 e 2

## Duração Estimada

5–7 horas
```

- [ ] **Passo 2: Criar conteúdo teórico**

Criar `modulos/03-formatos-dados/conteudo.md`:

```markdown
# Formatos de Dados — Conteúdo

## Visão Geral

| Formato | Orientação | Legível por humanos | Compressão | Schema | Melhor para         |
|---------|-----------|---------------------|------------|--------|---------------------|
| CSV     | Linha     | Sim                 | Não nativo | Não    | Intercâmbio simples |
| JSON    | Linha     | Sim                 | Não nativo | Não    | APIs, dados aninhados|
| Parquet | Coluna    | Não                 | Alta       | Sim    | Analytics em escala |
| Avro    | Linha     | Não                 | Boa        | Sim    | Streaming, Kafka    |
| Delta   | Coluna    | Não                 | Alta       | Sim    | Lakehouse, ACID     |

## CSV

Texto plano separado por delimitador (geralmente vírgula).

```python
import pandas as pd

df = pd.read_csv('recursos/datasets/vendas.csv')
df.to_csv('saida/vendas_filtradas.csv', index=False)
```

**Prós:** simples, universal, fácil de abrir em qualquer ferramenta
**Contras:** sem tipos, sem schema, ineficiente para grandes volumes, frágil (encoding, delimitadores)

## JSON

Formato de texto para dados estruturados e semiestruturados.

```python
import json
import pandas as pd

# Ler
with open('dados.json') as f:
    dados = json.load(f)

# Dados aninhados → DataFrame
df = pd.json_normalize(dados, record_path='vendas')
```

**Prós:** flexível, suporta aninhamento, padrão de APIs
**Contras:** verboso, ineficiente para dados tabulares em escala

## Parquet

Formato colunar binário. Armazena dados por coluna, não por linha.

```python
import pandas as pd

df = pd.read_parquet('vendas.parquet')
df.to_parquet('saida/vendas.parquet', compression='snappy')
```

**Por que colunar importa?** Em analytics, você raramente precisa de todas as colunas. Se a query precisa só de `valor_total` e `data_venda`, Parquet lê apenas essas colunas — muito mais eficiente que CSV, que lê a linha inteira.

**Compressão:** Snappy (velocidade) ou Gzip (maior compressão). Snappy é o padrão.

## Avro

Formato binário orientado a linhas com schema embutido. Popular em streaming.

**Casos de uso:** pipelines Kafka/Kinesis, quando schema evolution é crítico (campos podem ser adicionados sem quebrar consumidores).

## Delta Lake

Formato Parquet + camada de transações ACID + log de operações.

**Recursos chave:**
- **ACID transactions:** operações seguras mesmo com múltiplos escritores
- **Time travel:** consultar versões anteriores dos dados
- **Schema enforcement:** rejeita dados que não batem com o schema
- **Upserts (MERGE):** inserir ou atualizar em uma operação

```python
# Com pandas + delta-rs
from deltalake import write_deltalake, DeltaTable

write_deltalake('caminho/delta', df)

dt = DeltaTable('caminho/delta')
df_atual = dt.to_pandas()
df_historico = dt.load_as_version(0).to_pandas()  # time travel
```

## Critério de Escolha

- **Intercâmbio com sistemas externos:** CSV ou JSON
- **Analytics e data lake:** Parquet
- **Streaming/Kafka:** Avro
- **Lakehouse com necessidade de ACID ou histórico:** Delta
```

- [ ] **Passo 3: Criar exercícios**

Criar `modulos/03-formatos-dados/exercicios/exercicios.md`:

```markdown
# Exercícios — Formatos de Dados

## Ex 3.1 — Conversão de formatos

Usando Python e pandas, leia o arquivo `recursos/datasets/vendas.csv` e:
a) Salve como JSON (orientação `records`)
b) Salve como Parquet com compressão Snappy
c) Compare o tamanho dos três arquivos em bytes

## Ex 3.2 — Leitura seletiva com Parquet

Leia o arquivo Parquet de vendas criado no Ex 3.1, mas carregue **apenas** as colunas `data_venda` e `valor_total`. Calcule a receita total por mês.

Compare o tempo de leitura com a leitura do CSV completo.

## Ex 3.3 — Escolha de formato

Para cada cenário abaixo, indique o formato mais adequado e justifique:

a) Uma API REST que retorna dados de pedidos para um app mobile
b) Um pipeline que processa 10 bilhões de eventos de cliques por dia para relatórios
c) Um tópico Kafka com eventos de transações bancárias, onde o schema pode evoluir
d) Um arquivo de configuração simples trocado entre equipes via email
e) Uma tabela no data lake que sofre updates diários e precisa de histórico
```

- [ ] **Passo 4: Criar gabarito**

Criar `modulos/03-formatos-dados/exercicios/gabarito.md`:

```markdown
# Gabarito — Formatos de Dados

## Ex 3.1

```python
import pandas as pd
import os

df = pd.read_csv('recursos/datasets/vendas.csv')

df.to_json('saida/vendas.json', orient='records', indent=2)
df.to_parquet('saida/vendas.parquet', compression='snappy')

for f in ['recursos/datasets/vendas.csv', 'saida/vendas.json', 'saida/vendas.parquet']:
    print(f"{f}: {os.path.getsize(f)} bytes")
```

Resultado esperado (aproximado com dataset de exemplo):
- CSV: ~400 bytes
- JSON: ~1.2 KB (mais verboso)
- Parquet: ~4 KB (overhead de schema para arquivos pequenos; vantagem aparece em milhões de linhas)

## Ex 3.2

```python
import pandas as pd
import time

# Leitura seletiva com Parquet
start = time.time()
df_parquet = pd.read_parquet('saida/vendas.parquet', columns=['data_venda', 'valor_total'])
print(f"Parquet: {time.time() - start:.4f}s")

# Comparação com CSV
start = time.time()
df_csv = pd.read_csv('recursos/datasets/vendas.csv', usecols=['data_venda', 'valor_total'])
print(f"CSV: {time.time() - start:.4f}s")

# Receita por mês
df_parquet['mes'] = pd.to_datetime(df_parquet['data_venda']).dt.to_period('M')
print(df_parquet.groupby('mes')['valor_total'].sum())
```

Nota: com o dataset de exemplo a diferença é mínima. Em produção com GBs de dados, Parquet é ordens de magnitude mais rápido.

## Ex 3.3

a) **JSON** — APIs REST usam JSON por padrão. Flexível para dados aninhados (linhas do pedido, endereço).

b) **Parquet** — formato colunar para analytics em escala. Compressão alta, leitura eficiente por coluna.

c) **Avro** — schema evolution nativo. Kafka + Schema Registry com Avro é o padrão do mercado.

d) **CSV ou JSON** — simplicidade e legibilidade humana são prioridade. CSV para dados tabulares simples, JSON para estruturado.

e) **Delta Lake** — ACID + time travel resolve exatamente esse cenário.
```

- [ ] **Passo 5: Criar roteiro da sessão ao vivo**

Criar `modulos/03-formatos-dados/sessao-ao-vivo.md`:

```markdown
# Sessão ao Vivo — Módulo 3: Formatos de Dados

**Duração:** 2 horas

## Abertura (10 min)
- Dúvidas do módulo

## Bloco Conceitual (20 min)
- Demo ao vivo: abrir o mesmo arquivo em CSV, JSON e Parquet e mostrar o tamanho
- Mostrar o schema embutido no Parquet com `pd.read_parquet(...).dtypes`

## Exercício em Grupo (70 min)
**Ex 3.3 em grupo:** cada pessoa justifica sua escolha para os 5 cenários. Discutir divergências — não há sempre uma resposta única.

Bônus se der tempo: criar um arquivo Delta pequeno e demonstrar time travel.

## Fechamento (20 min)
- "Por que Parquet virou o padrão?" — reforçar o raciocínio
- Preview: Módulo 4 — Python para Dados
```

---

## Tarefa 4: Módulo 4 — Python para Dados

**Arquivos:**
- Criar: `modulos/04-python-dados/README.md`
- Criar: `modulos/04-python-dados/conteudo.md`
- Criar: `modulos/04-python-dados/exercicios/exercicios.md`
- Criar: `modulos/04-python-dados/exercicios/gabarito.md`
- Criar: `modulos/04-python-dados/sessao-ao-vivo.md`

- [ ] **Passo 1: Criar README**

```markdown
# Módulo 4 — Python para Dados

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Manipular dados com pandas (leitura, filtros, transformações, agrupamentos)
- Escrever funções reutilizáveis para transformação de dados
- Ler e escrever diferentes formatos de arquivo com Python
- Estruturar um script Python organizado e legível
- Automatizar tarefas repetitivas de manipulação de dados

## Pré-requisito

Módulos 1, 2 e 3

## Duração Estimada

10–15 horas
```

- [ ] **Passo 2: Criar conteúdo teórico**

Criar `modulos/04-python-dados/conteudo.md`:

```markdown
# Python para Dados — Conteúdo

## 1. Estruturas de Dados Essenciais

```python
# Listas — coleções ordenadas e mutáveis
meses = ['Jan', 'Fev', 'Mar']
meses.append('Abr')

# Dicionários — pares chave-valor
cliente = {'id': 1, 'nome': 'Ana', 'cidade': 'SP'}
print(cliente['nome'])

# Sets — valores únicos, sem ordem
categorias = {'Eletrônicos', 'Roupas', 'Eletrônicos'}
print(categorias)  # {'Eletrônicos', 'Roupas'}

# List comprehension
precos_com_desconto = [p * 0.9 for p in [3500, 299, 799] if p > 500]
```

## 2. Pandas — DataFrames

O pandas é a biblioteca padrão para manipulação de dados tabulares em Python.

```python
import pandas as pd

df = pd.read_csv('recursos/datasets/vendas.csv')

# Inspeção básica
print(df.shape)       # (linhas, colunas)
print(df.dtypes)      # tipos de cada coluna
print(df.head())      # primeiras 5 linhas
print(df.describe())  # estatísticas descritivas

# Filtros
df_sp = df[df['cidade'] == 'São Paulo']
df_caro = df[(df['valor_total'] > 1000) & (df['quantidade'] > 1)]

# Seleção de colunas
df[['cliente_id', 'valor_total']]

# Nova coluna calculada
df['valor_unitario'] = df['valor_total'] / df['quantidade']
```

## 3. Operações Essenciais

```python
# Merge (equivalente ao JOIN do SQL)
vendas = pd.read_csv('recursos/datasets/vendas.csv')
clientes = pd.read_csv('recursos/datasets/clientes.csv')

df = vendas.merge(clientes, on='cliente_id', how='left')

# Group by + aggregação
resumo = df.groupby('cidade').agg(
    total_vendas=('venda_id', 'count'),
    receita=('valor_total', 'sum'),
    ticket_medio=('valor_total', 'mean')
).reset_index()

# Ordenação
resumo.sort_values('receita', ascending=False)

# Tratamento de valores nulos
df['coluna'].fillna(0)
df.dropna(subset=['coluna_obrigatoria'])
```

## 4. Funções Reutilizáveis

Organize transformações em funções com responsabilidade única.

```python
def calcular_receita_por_periodo(df_vendas: pd.DataFrame, coluna_data: str) -> pd.DataFrame:
    df = df_vendas.copy()
    df['mes'] = pd.to_datetime(df[coluna_data]).dt.to_period('M')
    return df.groupby('mes')['valor_total'].sum().reset_index()

def enriquecer_vendas(df_vendas, df_clientes, df_produtos):
    return (
        df_vendas
        .merge(df_clientes[['cliente_id', 'nome', 'cidade']], on='cliente_id', how='left')
        .merge(df_produtos[['produto_id', 'nome', 'categoria']], on='produto_id', how='left')
    )
```

## 5. Estrutura de um Script Python para Dados

```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path('recursos/datasets')
OUTPUT_DIR = Path('saida')


def extrair(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho)


def transformar(df_vendas, df_clientes, df_produtos) -> pd.DataFrame:
    df = df_vendas.merge(df_clientes, on='cliente_id', how='left')
    df = df.merge(df_produtos, on='produto_id', how='left')
    df['mes'] = pd.to_datetime(df['data_venda']).dt.to_period('M')
    return df


def carregar(df: pd.DataFrame, destino: Path) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_parquet(destino, index=False)
    print(f"Salvo em {destino} — {len(df)} linhas")


def main():
    vendas = extrair(DATA_DIR / 'vendas.csv')
    clientes = extrair(DATA_DIR / 'clientes.csv')
    produtos = extrair(DATA_DIR / 'produtos.csv')

    resultado = transformar(vendas, clientes, produtos)
    carregar(resultado, OUTPUT_DIR / 'vendas_enriquecidas.parquet')


if __name__ == '__main__':
    main()
```

Este script já segue a estrutura de um ETL — você vai reconhecê-lo no próximo módulo.
```

- [ ] **Passo 3: Criar exercícios**

Criar `modulos/04-python-dados/exercicios/exercicios.md`:

```markdown
# Exercícios — Python para Dados

## Ex 4.1 — Manipulação básica

Usando pandas e o dataset de e-commerce:
a) Carregue as três tabelas (vendas, clientes, produtos)
b) Faça um merge para criar um DataFrame único com nome do cliente, nome do produto, categoria, data e valor
c) Filtre apenas vendas do primeiro trimestre de 2024
d) Calcule a receita total por categoria nesse período

## Ex 4.2 — Funções de transformação

Crie as seguintes funções:
a) `top_clientes(df, n)` → retorna os N clientes com maior receita total
b) `vendas_por_mes(df)` → retorna receita e quantidade de vendas por mês
c) `ticket_medio_por_categoria(df)` → retorna o ticket médio por categoria de produto

## Ex 4.3 — Script ETL estruturado

Escreva um script Python completo (`pipeline.py`) que:
1. Lê os três arquivos CSV do dataset
2. Enriquece as vendas com informações de clientes e produtos
3. Calcula a receita total por cidade e por categoria
4. Salva o resultado em dois arquivos Parquet: `receita_por_cidade.parquet` e `receita_por_categoria.parquet`

O script deve seguir a estrutura extrair/transformar/carregar vista no conteúdo.
```

- [ ] **Passo 4: Criar gabarito**

Criar `modulos/04-python-dados/exercicios/gabarito.md`:

```markdown
# Gabarito — Python para Dados

## Ex 4.1

```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path('recursos/datasets')

vendas = pd.read_csv(DATA_DIR / 'vendas.csv')
clientes = pd.read_csv(DATA_DIR / 'clientes.csv')
produtos = pd.read_csv(DATA_DIR / 'produtos.csv')

df = (
    vendas
    .merge(clientes[['cliente_id', 'nome', 'cidade']], on='cliente_id')
    .merge(produtos[['produto_id', 'nome', 'categoria']], on='produto_id', suffixes=('_cliente', '_produto'))
)

df['data_venda'] = pd.to_datetime(df['data_venda'])
q1 = df[(df['data_venda'] >= '2024-01-01') & (df['data_venda'] < '2024-04-01')]

receita = q1.groupby('categoria')['valor_total'].sum().reset_index()
print(receita)
```

## Ex 4.2

```python
def top_clientes(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return (
        df.groupby('nome_cliente')['valor_total']
        .sum()
        .reset_index()
        .sort_values('valor_total', ascending=False)
        .head(n)
    )


def vendas_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['mes'] = pd.to_datetime(df['data_venda']).dt.to_period('M')
    return df.groupby('mes').agg(
        receita=('valor_total', 'sum'),
        qtd_vendas=('venda_id', 'count')
    ).reset_index()


def ticket_medio_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby('categoria')['valor_total']
        .mean()
        .reset_index()
        .rename(columns={'valor_total': 'ticket_medio'})
    )
```

## Ex 4.3

```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path('recursos/datasets')
OUTPUT_DIR = Path('saida')


def extrair():
    return (
        pd.read_csv(DATA_DIR / 'vendas.csv'),
        pd.read_csv(DATA_DIR / 'clientes.csv'),
        pd.read_csv(DATA_DIR / 'produtos.csv'),
    )


def transformar(vendas, clientes, produtos):
    df = (
        vendas
        .merge(clientes[['cliente_id', 'cidade']], on='cliente_id')
        .merge(produtos[['produto_id', 'categoria']], on='produto_id')
    )
    receita_cidade = df.groupby('cidade')['valor_total'].sum().reset_index()
    receita_categoria = df.groupby('categoria')['valor_total'].sum().reset_index()
    return receita_cidade, receita_categoria


def carregar(receita_cidade, receita_categoria):
    OUTPUT_DIR.mkdir(exist_ok=True)
    receita_cidade.to_parquet(OUTPUT_DIR / 'receita_por_cidade.parquet', index=False)
    receita_categoria.to_parquet(OUTPUT_DIR / 'receita_por_categoria.parquet', index=False)
    print(f"Receita por cidade: {len(receita_cidade)} linhas")
    print(f"Receita por categoria: {len(receita_categoria)} linhas")


def main():
    vendas, clientes, produtos = extrair()
    receita_cidade, receita_categoria = transformar(vendas, clientes, produtos)
    carregar(receita_cidade, receita_categoria)


if __name__ == '__main__':
    main()
```

- [ ] **Passo 5: Criar roteiro da sessão ao vivo**

Criar `modulos/04-python-dados/sessao-ao-vivo.md`:

```markdown
# Sessão ao Vivo — Módulo 4: Python para Dados

**Duração:** 2 horas

## Abertura (10 min)
- Dúvidas do módulo

## Bloco Conceitual (15 min)
- Mostrar ao vivo: a estrutura do Ex 4.3 é um ETL — conectar com o próximo módulo

## Exercício em Grupo (75 min)
**Ex 4.3 ao vivo:**
1. Cada um apresenta seu `pipeline.py`
2. Discutir diferenças na estrutura e nas transformações
3. Refatorar juntos uma versão consolidada com o melhor de cada abordagem

Pergunta provocativa: "O que acontece se o CSV tiver um valor nulo em `valor_total`? Onde você trataria isso?"

## Fechamento (20 min)
- "Vocês acabaram de escrever um ETL funcional"
- Preview: Módulo 5 — Lógica de ETL/ELT (formalizar o que fizemos aqui)
```

---

## Tarefa 5: Módulo 5 — Lógica de ETL/ELT

**Arquivos:**
- Criar: `modulos/05-logica-etl-elt/README.md`
- Criar: `modulos/05-logica-etl-elt/conteudo.md`
- Criar: `modulos/05-logica-etl-elt/exercicios/exercicios.md`
- Criar: `modulos/05-logica-etl-elt/exercicios/gabarito.md`
- Criar: `modulos/05-logica-etl-elt/sessao-ao-vivo.md`

- [ ] **Passo 1: Criar README**

```markdown
# Módulo 5 — Lógica de ETL/ELT

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Explicar a diferença entre ETL e ELT e quando usar cada um
- Identificar estratégias de extração (full load, incremental)
- Aplicar transformações de limpeza, enriquecimento e padronização
- Implementar estratégias de carga: insert, upsert, full replace
- Escrever pipelines idempotentes
- Tratar erros e estruturar reprocessamento

## Pré-requisito

Módulos 1–4

## Duração Estimada

10–12 horas
```

- [ ] **Passo 2: Criar conteúdo teórico**

Criar `modulos/05-logica-etl-elt/conteudo.md`:

```markdown
# Lógica de ETL/ELT — Conteúdo

## 1. ETL vs ELT

**ETL (Extract → Transform → Load):**
Os dados são transformados ANTES de serem carregados no destino.
- Usado quando o sistema de destino tem capacidade limitada
- Mais controle sobre o que chega no destino
- Transformações feitas em código (Python, Spark)

**ELT (Extract → Load → Transform):**
Os dados são carregados RAW no destino e transformados lá dentro.
- Moderno — aproveita o poder de processamento de DWs como BigQuery, Snowflake, Databricks
- Dados brutos preservados, mais fácil de reprocessar
- Transformações feitas em SQL (dbt, views, stored procedures)

**Tendência atual:** ELT domina em cloud data warehouses e lakehouses.

## 2. Estratégias de Extração

**Full Load:** extrai toda a tabela de origem a cada execução.
- Simples de implementar
- Ineficiente para tabelas grandes
- Seguro: sempre tem o estado atual completo

```python
def extrair_full(conn_string: str, tabela: str) -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM {tabela}", conn_string)
```

**Incremental:** extrai apenas os registros novos ou alterados desde a última execução.
- Eficiente para grandes volumes
- Requer uma coluna de controle (data de atualização, ID sequencial)
- Mais complexo de implementar corretamente

```python
def extrair_incremental(conn_string, tabela, ultima_execucao):
    query = f"""
        SELECT *
        FROM {tabela}
        WHERE updated_at > '{ultima_execucao}'
    """
    return pd.read_sql(query, conn_string)
```

## 3. Transformações Comuns

```python
def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Remover duplicatas
    df = df.drop_duplicates(subset=['venda_id'])
    # Tratar nulos
    df['valor_total'] = df['valor_total'].fillna(0)
    # Padronizar strings
    df['cidade'] = df['cidade'].str.strip().str.title()
    # Corrigir tipos
    df['data_venda'] = pd.to_datetime(df['data_venda'])
    return df


def enriquecer(df: pd.DataFrame, df_ref: pd.DataFrame) -> pd.DataFrame:
    return df.merge(df_ref, on='produto_id', how='left')
```

## 4. Estratégias de Carga

**Full Replace:** trunca a tabela destino e carrega tudo.
- Simples, seguro para tabelas pequenas
- Ineficiente para grandes volumes

**Append (Insert):** insere apenas os novos registros.
- Rápido
- Risco de duplicatas se o controle incremental falhar

**Upsert (Merge):** insere se não existe, atualiza se existe.
- Padrão mais seguro para a maioria dos casos
- Requer chave natural para identificar duplicatas

```python
def upsert_parquet(df_novo: pd.DataFrame, caminho_destino: str, chave: str):
    from deltalake import DeltaTable, write_deltalake

    if DeltaTable.is_deltatable(caminho_destino):
        dt = DeltaTable(caminho_destino)
        dt.merge(
            source=df_novo,
            predicate=f"target.{chave} = source.{chave}",
            source_alias="source",
            target_alias="target"
        ).when_matched_update_all().when_not_matched_insert_all().execute()
    else:
        write_deltalake(caminho_destino, df_novo)
```

## 5. Idempotência

Um pipeline é **idempotente** quando executá-lo múltiplas vezes com os mesmos dados produz o mesmo resultado.

Por que importa? Pipelines falham. Você precisa reprocessar com segurança.

**Anti-padrão (não idempotente):**
```python
df.to_sql('vendas', conn, if_exists='append')  # cada execução duplica os dados
```

**Padrão idempotente:**
```python
# Estratégia 1: Full Replace
df.to_sql('vendas', conn, if_exists='replace')

# Estratégia 2: Upsert com chave natural
# (inserir ou atualizar baseado em venda_id)
```

## 6. Tratamento de Erros

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def executar_pipeline():
    try:
        df = extrair()
        df = transformar(df)
        carregar(df)
        logger.info(f"Pipeline concluído: {len(df)} linhas processadas")
    except FileNotFoundError as e:
        logger.error(f"Arquivo não encontrado: {e}")
        raise
    except Exception as e:
        logger.error(f"Falha no pipeline: {e}")
        raise
```
```

- [ ] **Passo 3: Criar exercícios**

Criar `modulos/05-logica-etl-elt/exercicios/exercicios.md`:

```markdown
# Exercícios — Lógica de ETL/ELT

## Ex 5.1 — ETL vs ELT

Para cada cenário, indique se ETL ou ELT é mais adequado e justifique:

a) Uma empresa com Snowflake como DW quer transformar logs de acesso brutos em relatórios de comportamento de usuário.

b) Um sistema legado exporta arquivos CSV com dados sensíveis que precisam ser anonimizados antes de qualquer armazenamento.

c) Uma startup usa BigQuery e quer construir um pipeline simples de vendas.

## Ex 5.2 — Extração incremental

Adicione ao dataset de vendas uma coluna `updated_at` com timestamps simulados. Escreva uma função `extrair_incremental(df, ultima_execucao)` que retorna apenas linhas com `updated_at` posterior ao parâmetro.

Simule duas execuções: a primeira processa todas as vendas, a segunda processa apenas as novas.

## Ex 5.3 — Pipeline idempotente

Escreva um pipeline completo (`etl_idempotente.py`) que:
1. Lê `vendas.csv`
2. Limpa os dados (remove duplicatas, trata nulos, corrige tipos)
3. Calcula `valor_unitario = valor_total / quantidade`
4. Salva em `saida/vendas_processadas.parquet`

O pipeline deve ser idempotente: executar 3 vezes seguidas deve produzir exatamente o mesmo arquivo de saída.

## Ex 5.4 — Tratamento de erro

Modifique o pipeline do Ex 5.3 para:
- Logar o início e fim de cada etapa com timestamp
- Capturar e logar erros sem deixar o programa travar silenciosamente
- Ao final, exibir um resumo: total de linhas lidas, linhas após limpeza, linhas salvas
```

- [ ] **Passo 4: Criar gabarito**

Criar `modulos/05-logica-etl-elt/exercicios/gabarito.md`:

```markdown
# Gabarito — Lógica de ETL/ELT

## Ex 5.1

a) **ELT** — Snowflake tem poder de processamento. Carregar raw e transformar com SQL/dbt é mais eficiente e mantém histórico.

b) **ETL** — anonimização antes do armazenamento é um requisito de compliance. Os dados não podem chegar ao destino sem transformação.

c) **ELT** — BigQuery é otimizado para isso. Carregar e transformar com SQL é mais simples e barato.

## Ex 5.2

```python
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('recursos/datasets/vendas.csv')

# Simular updated_at
df['updated_at'] = pd.to_datetime('2024-01-01') + pd.to_timedelta(df.index, unit='D')


def extrair_incremental(df: pd.DataFrame, ultima_execucao: datetime) -> pd.DataFrame:
    return df[df['updated_at'] > ultima_execucao].copy()


# Primeira execução: tudo
primeira = extrair_incremental(df, datetime(2023, 12, 31))
print(f"Primeira execução: {len(primeira)} linhas")

# Segunda execução: apenas novas
# (simular que última execução processou até o índice 5)
ultima = df.iloc[5]['updated_at']
segunda = extrair_incremental(df, ultima)
print(f"Segunda execução: {len(segunda)} linhas")
```

## Ex 5.3 + 5.4

```python
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

DATA_DIR = Path('recursos/datasets')
OUTPUT_DIR = Path('saida')


def extrair() -> pd.DataFrame:
    logger.info("Iniciando extração")
    df = pd.read_csv(DATA_DIR / 'vendas.csv')
    logger.info(f"Extração concluída: {len(df)} linhas")
    return df


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Iniciando transformação")
    linhas_antes = len(df)

    df = df.drop_duplicates(subset=['venda_id'])
    df['valor_total'] = df['valor_total'].fillna(0)
    df['quantidade'] = df['quantidade'].fillna(1)
    df['data_venda'] = pd.to_datetime(df['data_venda'])
    df['valor_unitario'] = df['valor_total'] / df['quantidade']

    logger.info(f"Transformação concluída: {linhas_antes} → {len(df)} linhas")
    return df


def carregar(df: pd.DataFrame) -> None:
    logger.info("Iniciando carga")
    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_parquet(OUTPUT_DIR / 'vendas_processadas.parquet', index=False)
    logger.info(f"Carga concluída: {len(df)} linhas salvas")


def main():
    try:
        df_raw = extrair()
        df_clean = transformar(df_raw)
        carregar(df_clean)
        logger.info(f"Pipeline finalizado | lidas={len(df_raw)} | salvas={len(df_clean)}")
    except Exception as e:
        logger.error(f"Pipeline falhou: {e}")
        raise


if __name__ == '__main__':
    main()
```

- [ ] **Passo 5: Criar roteiro da sessão ao vivo**

Criar `modulos/05-logica-etl-elt/sessao-ao-vivo.md`:

```markdown
# Sessão ao Vivo — Módulo 5: Lógica de ETL/ELT

**Duração:** 2 horas

## Abertura (10 min)
- Dúvidas do módulo

## Bloco Conceitual (15 min)
- "Vocês já fizeram ETL no módulo 4 — agora têm o vocabulário"
- Diferença ETL vs ELT com exemplo real

## Exercício em Grupo (70 min)
**Ex 5.4 ao vivo:**
1. Cada um apresenta seu pipeline com logs
2. Comparar: quem logou mais informações úteis? O que faltou?
3. Simular uma falha ao vivo (arquivo não encontrado) e ver como cada versão se comporta

Pergunta: "O seu pipeline é idempotente? Como você provaria isso?"

## Fechamento (20 min)
- Reforçar idempotência como princípio, não como detalhe
- Preview: Módulo 6 — Engenharia de Pipelines (orquestração)
```

---

## Tarefa 6: Módulo 6 — Engenharia de Pipelines

**Arquivos:**
- Criar: `modulos/06-engenharia-pipelines/README.md`
- Criar: `modulos/06-engenharia-pipelines/conteudo.md`
- Criar: `modulos/06-engenharia-pipelines/exercicios/exercicios.md`
- Criar: `modulos/06-engenharia-pipelines/exercicios/gabarito.md`
- Criar: `modulos/06-engenharia-pipelines/sessao-ao-vivo.md`

- [ ] **Passo 1: Criar README**

```markdown
# Módulo 6 — Engenharia de Pipelines

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Explicar o que é orquestração e por que é necessária
- Diferenciar as principais ferramentas de orquestração (Airflow, Prefect, Databricks Workflows)
- Modelar dependências entre tarefas de um pipeline
- Configurar retentativas e alertas básicos
- Usar Git com fluxo básico de branches e commits para código de dados

## Pré-requisito

Módulos 1–5

## Duração Estimada

8–10 horas
```

- [ ] **Passo 2: Criar conteúdo teórico**

Criar `modulos/06-engenharia-pipelines/conteudo.md`:

```markdown
# Engenharia de Pipelines — Conteúdo

## 1. O que é Orquestração

Um script Python que roda manualmente funciona em desenvolvimento. Em produção, você precisa que ele:
- Execute automaticamente no horário certo
- Saiba a ordem correta das tarefas
- Reprocesse se falhar
- Notifique quando algo der errado

**Orquestração** resolve isso.

## 2. Conceitos Fundamentais

**DAG (Directed Acyclic Graph):** grafo direcionado sem ciclos que representa as dependências entre tarefas.

```
extrair_vendas → transformar → carregar
extrair_clientes ↗
```

**Tarefas (Tasks/Steps):** unidade mínima de trabalho. Cada tarefa deve ter uma responsabilidade clara.

**Agendamento (Schedule):** quando o pipeline deve rodar.
- `@daily` — uma vez por dia
- `0 6 * * *` — às 6h todo dia (sintaxe cron)
- trigger manual ou por evento

## 3. Ferramentas Principais

| Ferramenta           | Onde roda     | Ponto forte                            |
|----------------------|---------------|----------------------------------------|
| Apache Airflow       | Infra própria | Mais completo, grande ecossistema      |
| Prefect              | Cloud/híbrido | Mais simples de desenvolver            |
| Databricks Workflows | Databricks    | Nativo no Databricks, integração total |

## 4. Airflow — Conceitos Básicos

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extrair():
    print("Extraindo dados...")

def transformar():
    print("Transformando dados...")

def carregar():
    print("Carregando dados...")

with DAG(
    dag_id='pipeline_vendas',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False,
) as dag:

    t1 = PythonOperator(task_id='extrair', python_callable=extrair)
    t2 = PythonOperator(task_id='transformar', python_callable=transformar)
    t3 = PythonOperator(task_id='carregar', python_callable=carregar)

    t1 >> t2 >> t3  # define dependências
```

## 5. Retentativas e Alertas

```python
from airflow.operators.python import PythonOperator

t1 = PythonOperator(
    task_id='extrair',
    python_callable=extrair,
    retries=3,
    retry_delay=timedelta(minutes=5),
    on_failure_callback=notificar_falha,
)
```

## 6. Git para Código de Dados

**Fluxo básico:**

```bash
# Criar branch para nova feature
git checkout -b feat/pipeline-vendas

# Fazer alterações...

# Ver o que mudou
git status
git diff

# Commitar
git add src/pipelines/vendas.py
git commit -m "feat: adiciona pipeline de vendas diário"

# Abrir pull request
git push origin feat/pipeline-vendas
```

**Boas práticas:**
- Um commit por mudança lógica (não "várias coisas")
- Mensagens de commit descritivas: `feat:`, `fix:`, `refactor:`
- Nunca commitar direto na main — use branches e PR
- Código de pipeline vive no repositório como qualquer outro código
```

- [ ] **Passo 3: Criar exercícios**

Criar `modulos/06-engenharia-pipelines/exercicios/exercicios.md`:

```markdown
# Exercícios — Engenharia de Pipelines

## Ex 6.1 — Modelar dependências

Dado o pipeline abaixo, desenhe o DAG (em texto/ASCII) com as dependências corretas:

- `extrair_vendas`: lê vendas do CSV
- `extrair_produtos`: lê produtos do CSV
- `extrair_clientes`: lê clientes do CSV
- `transformar`: faz merge das três fontes e calcula receita por categoria
- `validar`: verifica se o resultado tem registros
- `carregar`: salva o resultado em Parquet

Restrições: as três extrações podem rodar em paralelo. A transformação depende das três extrações. A validação depende da transformação. A carga depende da validação.

## Ex 6.2 — DAG com Airflow

Implemente o DAG do Ex 6.1 em Airflow. Não precisa conectar ao banco de dados real — use as funções do módulo 5 como callables.

Configure:
- Agendamento: todo dia às 7h
- Retentativas: 2 tentativas com 10 minutos de intervalo
- catchup=False

## Ex 6.3 — Git na prática

Faça os seguintes passos em um repositório Git local:
1. Inicialize um repositório na pasta do seu pipeline do módulo 5
2. Faça um commit inicial com o script
3. Crie uma branch `feat/adicionar-validacao`
4. Adicione uma função de validação ao pipeline (ex: verificar se o DataFrame tem mais de 0 linhas)
5. Commite a mudança com uma mensagem descritiva
6. Liste o histórico de commits com `git log --oneline`
```

- [ ] **Passo 4: Criar gabarito**

Criar `modulos/06-engenharia-pipelines/exercicios/gabarito.md`:

```markdown
# Gabarito — Engenharia de Pipelines

## Ex 6.1

```
extrair_vendas ─┐
extrair_clientes ─┼──→ transformar → validar → carregar
extrair_produtos ─┘
```

As três extrações têm dependência zero entre si (paralelas). Transformar depende das três. Validar depende de transformar. Carregar depende de validar.

## Ex 6.2

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

DATA_DIR = Path('recursos/datasets')
OUTPUT_DIR = Path('saida')


def extrair_vendas():
    return pd.read_csv(DATA_DIR / 'vendas.csv').to_dict()

def extrair_clientes():
    return pd.read_csv(DATA_DIR / 'clientes.csv').to_dict()

def extrair_produtos():
    return pd.read_csv(DATA_DIR / 'produtos.csv').to_dict()

def transformar(**context):
    ti = context['ti']
    vendas = pd.DataFrame(ti.xcom_pull(task_ids='extrair_vendas'))
    clientes = pd.DataFrame(ti.xcom_pull(task_ids='extrair_clientes'))
    produtos = pd.DataFrame(ti.xcom_pull(task_ids='extrair_produtos'))

    df = vendas.merge(clientes, on='cliente_id').merge(produtos, on='produto_id')
    resultado = df.groupby('categoria')['valor_total'].sum().reset_index()
    return resultado.to_dict()

def validar(**context):
    ti = context['ti']
    df = pd.DataFrame(ti.xcom_pull(task_ids='transformar'))
    assert len(df) > 0, "Pipeline produziu DataFrame vazio"

def carregar(**context):
    ti = context['ti']
    df = pd.DataFrame(ti.xcom_pull(task_ids='transformar'))
    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_parquet(OUTPUT_DIR / 'receita_categoria.parquet', index=False)


with DAG(
    dag_id='pipeline_vendas',
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 7 * * *',
    catchup=False,
    default_args={
        'retries': 2,
        'retry_delay': timedelta(minutes=10),
    }
) as dag:

    t_vendas = PythonOperator(task_id='extrair_vendas', python_callable=extrair_vendas)
    t_clientes = PythonOperator(task_id='extrair_clientes', python_callable=extrair_clientes)
    t_produtos = PythonOperator(task_id='extrair_produtos', python_callable=extrair_produtos)
    t_transform = PythonOperator(task_id='transformar', python_callable=transformar)
    t_validar = PythonOperator(task_id='validar', python_callable=validar)
    t_carregar = PythonOperator(task_id='carregar', python_callable=carregar)

    [t_vendas, t_clientes, t_produtos] >> t_transform >> t_validar >> t_carregar
```

## Ex 6.3

```bash
git init
git add pipeline.py
git commit -m "feat: pipeline ETL inicial de vendas"

git checkout -b feat/adicionar-validacao
# editar pipeline.py para adicionar função validar()
git add pipeline.py
git commit -m "feat: adiciona validação de registros pós-transformação"

git log --oneline
```

- [ ] **Passo 5: Criar roteiro da sessão ao vivo**

Criar `modulos/06-engenharia-pipelines/sessao-ao-vivo.md`:

```markdown
# Sessão ao Vivo — Módulo 6: Engenharia de Pipelines

**Duração:** 2 horas

## Abertura (10 min)

## Bloco Conceitual (15 min)
- Mostrar ao vivo a interface do Airflow (ou screenshot) para materializar o conceito de DAG

## Exercício em Grupo (70 min)
**Ex 6.1 ao vivo:** modelar o DAG coletivamente antes de codar.
- Cada um desenha no papel/whiteboard
- Comparar: paralelo vs sequencial, onde cada um colocou as dependências
- Implementar juntos em Airflow

## Fechamento (20 min)
- Git: por que código de pipeline deve viver no repositório?
- Preview: Módulo 7 — Armazenamento e Processamento
```

---

## Tarefa 7: Módulo 7 — Armazenamento e Processamento

**Arquivos:**
- Criar: `modulos/07-armazenamento-processamento/README.md`
- Criar: `modulos/07-armazenamento-processamento/conteudo.md`
- Criar: `modulos/07-armazenamento-processamento/exercicios/exercicios.md`
- Criar: `modulos/07-armazenamento-processamento/exercicios/gabarito.md`
- Criar: `modulos/07-armazenamento-processamento/sessao-ao-vivo.md`

- [ ] **Passo 1: Criar README**

```markdown
# Módulo 7 — Armazenamento e Processamento

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Diferenciar Data Warehouse, Data Lake e Lakehouse
- Descrever as zonas de um Data Lake (raw, trusted, refined)
- Explicar por que o processamento distribuído existe e quando é necessário
- Entender os conceitos básicos do Spark (sem escrever código Spark)
- Tomar decisões de particionamento e entender o impacto na performance

## Pré-requisito

Módulos 1–6

## Duração Estimada

6–8 horas
```

- [ ] **Passo 2: Criar conteúdo teórico**

Criar `modulos/07-armazenamento-processamento/conteudo.md`:

```markdown
# Armazenamento e Processamento — Conteúdo

## 1. Data Warehouse

Repositório estruturado e otimizado para consultas analíticas. Dados organizados em schemas relacionais ou dimensionais.

**Características:**
- Schema-on-write: schema definido antes da carga
- Dados limpos e modelados
- Otimizado para leitura analítica (SQL)
- Exemplos: Snowflake, BigQuery, Redshift, Synapse

**Quando usar:** relatórios, dashboards, análises recorrentes com dados bem definidos.

## 2. Data Lake

Repositório de dados brutos em seu formato original (arquivos). Sem schema obrigatório na entrada.

**Características:**
- Schema-on-read: schema interpretado na leitura
- Armazena tudo: estruturado, semiestruturado, não estruturado
- Barato (armazenamento de objeto: S3, ADLS, GCS)
- Pode virar um "data swamp" sem governança

**Zonas típicas:**
```
raw/        → dados brutos, nunca modificados
trusted/    → dados limpos e validados
refined/    → dados modelados, prontos para consumo
```

## 3. Lakehouse

Combina o melhor dos dois: armazenamento barato do Data Lake com as garantias do Data Warehouse (ACID, schema, performance).

**Habilitado por:** Delta Lake, Apache Iceberg, Apache Hudi.
**Plataformas:** Databricks, Snowflake (com Iceberg), BigQuery (com tabelas abertas).

## 4. Processamento Distribuído

**Por que existe?**
Um arquivo de 1 TB não cabe na memória de um único computador. A solução é dividir o trabalho entre muitas máquinas (cluster).

**Como funciona (simplificado):**
1. O dado é particionado em blocos
2. Cada bloco é processado por um nó do cluster em paralelo
3. Os resultados são agregados

**Apache Spark:**
- Motor de processamento distribuído open source
- Lê/escreve de S3, ADLS, Delta, Parquet, CSV...
- APIs em Python (PySpark), Scala, SQL
- Conceito de DataFrame distribuído — similar ao pandas, mas escala para TBs

```python
# PySpark — mesma lógica do pandas, sintaxe diferente
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.getOrCreate()

df = spark.read.parquet('caminho/vendas.parquet')

resultado = (
    df
    .filter(F.col('valor_total') > 100)
    .groupBy('categoria')
    .agg(F.sum('valor_total').alias('receita'))
    .orderBy('receita', ascending=False)
)

resultado.show()
```

Compare com pandas do módulo 4 — mesma intenção, escala diferente.

## 5. Particionamento

Particionar divide os dados em subdiretórios por valor de coluna. Queries que filtram pela coluna de partição leem apenas os arquivos relevantes.

```
vendas/
  ano=2024/
    mes=01/
      part-000.parquet
      part-001.parquet
    mes=02/
      ...
```

```python
# Escrever com partição
df.to_parquet('vendas/', partition_cols=['ano', 'mes'])

# Ler com filtro na partição (não lê outros meses)
df_jan = pd.read_parquet('vendas/', filters=[('mes', '==', '01')])
```

**Escolha de coluna de partição:** use colunas que aparecem frequentemente em filtros (data, região, status). Evite colunas de alta cardinalidade (cliente_id, venda_id).
```

- [ ] **Passo 3: Criar exercícios**

Criar `modulos/07-armazenamento-processamento/exercicios/exercicios.md`:

```markdown
# Exercícios — Armazenamento e Processamento

## Ex 7.1 — DW vs Data Lake vs Lakehouse

Para cada cenário, qual arquitetura é mais adequada? Justifique.

a) Uma empresa precisa armazenar logs brutos de servidor (JSON, ~500 GB/dia) que podem ser analisados eventualmente.

b) Um time de BI precisa de relatórios diários de vendas com SLA de 5 segundos por query.

c) Uma equipe de dados quer armazenar dados brutos, fazer transformações e servir para BI e ML com ACID e time travel.

## Ex 7.2 — Zonas do Data Lake

Dado o pipeline de vendas construído nos módulos anteriores, defina a estrutura de pastas de um Data Lake para esse domínio:
- O que vai em `raw/`?
- O que vai em `trusted/`?
- O que vai em `refined/`?

Liste os arquivos que existiriam em cada zona após uma execução completa do pipeline.

## Ex 7.3 — Particionamento

Você tem uma tabela de vendas com 3 anos de histórico (2022, 2023, 2024), ~10 milhões de linhas.

a) Escreva o dataset de vendas particionado por ano e mês usando pandas.

b) Leia apenas as vendas de março de 2024 usando filtro de partição.

c) Por que particionar por `venda_id` seria uma má escolha?

## Ex 7.4 — Leitura de PySpark

Leia o trecho de código PySpark abaixo e explique o que ele faz, traduzindo para pandas equivalente:

```python
resultado = (
    df
    .filter(F.col('data_venda') >= '2024-01-01')
    .join(df_clientes, on='cliente_id', how='left')
    .groupBy('cidade')
    .agg(
        F.sum('valor_total').alias('receita'),
        F.countDistinct('venda_id').alias('total_vendas')
    )
    .orderBy('receita', ascending=False)
    .limit(10)
)
```
```

- [ ] **Passo 4: Criar gabarito**

Criar `modulos/07-armazenamento-processamento/exercicios/gabarito.md`:

```markdown
# Gabarito — Armazenamento e Processamento

## Ex 7.1

a) **Data Lake** — dados brutos, semiestruturados, volume alto, consumo eventual. Armazenamento barato em S3/ADLS.

b) **Data Warehouse** — dados estruturados, relatórios com SLA, consultas SQL recorrentes. Snowflake/BigQuery/Redshift.

c) **Lakehouse** — combina armazenamento barato + ACID + schema + time travel. Delta Lake no Databricks ou Iceberg.

## Ex 7.2

```
raw/
  vendas/
    2024/01/vendas_20240101.csv
    2024/01/vendas_20240102.csv
    ...
  clientes/
    clientes_20240101.csv
  produtos/
    produtos_20240101.csv

trusted/
  vendas/
    vendas_limpo.parquet          # duplicatas removidas, tipos corrigidos
  clientes/
    clientes_limpo.parquet
  produtos/
    produtos_limpo.parquet

refined/
  receita_por_categoria.parquet   # agregado por categoria
  receita_por_cidade.parquet      # agregado por cidade
  vendas_enriquecidas.parquet     # join de vendas + clientes + produtos
```

## Ex 7.3

```python
import pandas as pd

df = pd.read_csv('recursos/datasets/vendas.csv')
df['data_venda'] = pd.to_datetime(df['data_venda'])
df['ano'] = df['data_venda'].dt.year
df['mes'] = df['data_venda'].dt.month.astype(str).str.zfill(2)

# a) Escrever particionado
df.to_parquet('saida/vendas_particionado/', partition_cols=['ano', 'mes'], index=False)

# b) Ler apenas março de 2024
df_mar = pd.read_parquet('saida/vendas_particionado/', filters=[('ano', '==', 2024), ('mes', '==', '03')])
print(df_mar)
```

c) `venda_id` é de alta cardinalidade — criaria uma pasta por venda, gerando milhões de pequenos arquivos. Isso destrói a performance de leitura e sobrecarrega o sistema de metadados.

## Ex 7.4

```python
# Equivalente pandas:
import pandas as pd

resultado = (
    df[df['data_venda'] >= '2024-01-01']                      # filter
    .merge(df_clientes, on='cliente_id', how='left')           # left join
    .groupby('cidade')                                         # groupBy
    .agg(
        receita=('valor_total', 'sum'),                        # sum alias
        total_vendas=('venda_id', 'nunique')                   # countDistinct
    )
    .reset_index()
    .sort_values('receita', ascending=False)                   # orderBy
    .head(10)                                                  # limit
)
```

- [ ] **Passo 5: Criar roteiro da sessão ao vivo**

Criar `modulos/07-armazenamento-processamento/sessao-ao-vivo.md`:

```markdown
# Sessão ao Vivo — Módulo 7: Armazenamento e Processamento

**Duração:** 2 horas

## Abertura (10 min)

## Bloco Conceitual (20 min)
- Diagrama DW vs Data Lake vs Lakehouse no whiteboard
- "Onde nosso pipeline atual se encaixaria?"

## Exercício em Grupo (70 min)
**Ex 7.2 + Ex 7.4 ao vivo:**
- Definir a estrutura do Data Lake do pipeline de vendas (Ex 7.2) em grupo
- Ler e traduzir o código PySpark para pandas (Ex 7.4) — sem rodar, só leitura e raciocínio

Discussão: "Se tivéssemos 10 bilhões de linhas em vez de 10, o que mudaria no nosso pipeline?"

## Fechamento (20 min)
- A lógica que vocês aprenderam em Python/pandas é a mesma do PySpark
- Preview: Módulo 8 — Qualidade e Observabilidade (o que acontece quando os dados estão errados)
```

---

## Tarefa 8: Módulo 8 — Qualidade e Observabilidade

**Arquivos:**
- Criar: `modulos/08-qualidade-observabilidade/README.md`
- Criar: `modulos/08-qualidade-observabilidade/conteudo.md`
- Criar: `modulos/08-qualidade-observabilidade/exercicios/exercicios.md`
- Criar: `modulos/08-qualidade-observabilidade/exercicios/gabarito.md`
- Criar: `modulos/08-qualidade-observabilidade/sessao-ao-vivo.md`

- [ ] **Passo 1: Criar README**

```markdown
# Módulo 8 — Qualidade e Observabilidade

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Definir qualidade de dados com dimensões concretas (completude, consistência, acurácia, timeliness)
- Escrever validações de dados em um pipeline
- Estruturar testes de pipeline (unitário e de integração)
- Implementar logging estruturado e útil
- Definir métricas básicas de monitoramento para um pipeline

## Pré-requisito

Módulos 1–7

## Duração Estimada

8–10 horas
```

- [ ] **Passo 2: Criar conteúdo teórico**

Criar `modulos/08-qualidade-observabilidade/conteudo.md`:

```markdown
# Qualidade e Observabilidade — Conteúdo

## 1. Dimensões de Qualidade de Dados

| Dimensão      | Pergunta                                          | Exemplo de problema                       |
|---------------|---------------------------------------------------|-------------------------------------------|
| Completude    | Todos os campos obrigatórios estão preenchidos?   | 30% de emails nulos                       |
| Consistência  | Os dados são consistentes entre si e entre fontes?| Produto_id existe em vendas mas não em produtos |
| Acurácia      | Os valores são corretos?                          | valor_total < 0, quantidade = 0           |
| Timeliness    | Os dados chegaram no tempo esperado?              | Pipeline de ontem ainda não rodou         |
| Unicidade     | Existem duplicatas?                               | Mesma venda_id aparece duas vezes         |

## 2. Validações em Pipeline

```python
import pandas as pd


class ValidacaoError(Exception):
    pass


def validar_schema(df: pd.DataFrame, colunas_obrigatorias: list[str]) -> None:
    ausentes = [c for c in colunas_obrigatorias if c not in df.columns]
    if ausentes:
        raise ValidacaoError(f"Colunas ausentes: {ausentes}")


def validar_completude(df: pd.DataFrame, colunas: list[str], tolerancia: float = 0.0) -> None:
    for col in colunas:
        pct_nulos = df[col].isna().mean()
        if pct_nulos > tolerancia:
            raise ValidacaoError(f"Coluna '{col}' tem {pct_nulos:.1%} nulos (limite: {tolerancia:.1%})")


def validar_unicidade(df: pd.DataFrame, chave: str) -> None:
    duplicatas = df[chave].duplicated().sum()
    if duplicatas > 0:
        raise ValidacaoError(f"Coluna '{chave}' tem {duplicatas} duplicatas")


def validar_valores(df: pd.DataFrame) -> None:
    invalidos = df[df['valor_total'] < 0]
    if len(invalidos) > 0:
        raise ValidacaoError(f"{len(invalidos)} linhas com valor_total negativo")
```

## 3. Testes de Pipeline

**Teste unitário:** testa uma função isolada com entrada e saída conhecidas.

```python
import pytest
import pandas as pd
from pipeline import transformar, limpar_dados


def test_limpar_dados_remove_duplicatas():
    df = pd.DataFrame({
        'venda_id': [1, 1, 2],
        'valor_total': [100.0, 100.0, 200.0]
    })
    resultado = limpar_dados(df)
    assert len(resultado) == 2


def test_limpar_dados_preenche_nulos():
    df = pd.DataFrame({
        'venda_id': [1],
        'valor_total': [None]
    })
    resultado = limpar_dados(df)
    assert resultado['valor_total'].iloc[0] == 0.0


def test_transformar_calcula_valor_unitario():
    df = pd.DataFrame({
        'venda_id': [1],
        'valor_total': [300.0],
        'quantidade': [3]
    })
    resultado = transformar(df)
    assert resultado['valor_unitario'].iloc[0] == 100.0
```

**Teste de integração:** testa o pipeline de ponta a ponta com dados reais (ou fixtures).

```python
def test_pipeline_completo(tmp_path):
    # Setup: copiar dataset de teste para pasta temporária
    df_vendas = pd.read_csv('recursos/datasets/vendas.csv')
    df_vendas.to_csv(tmp_path / 'vendas.csv', index=False)

    # Executar pipeline
    executar_pipeline(input_dir=tmp_path, output_dir=tmp_path / 'saida')

    # Verificar saída
    resultado = pd.read_parquet(tmp_path / 'saida' / 'vendas_processadas.parquet')
    assert len(resultado) > 0
    assert 'valor_unitario' in resultado.columns
    assert resultado['valor_total'].min() >= 0
```

## 4. Logging Estruturado

```python
import logging
import json
from datetime import datetime


def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )


logger = logging.getLogger(__name__)


def processar_lote(df: pd.DataFrame, batch_id: str) -> pd.DataFrame:
    logger.info("inicio_processamento", extra={
        'batch_id': batch_id,
        'linhas': len(df),
        'timestamp': datetime.utcnow().isoformat()
    })

    resultado = transformar(df)

    logger.info("fim_processamento", extra={
        'batch_id': batch_id,
        'linhas_entrada': len(df),
        'linhas_saida': len(resultado),
    })

    return resultado
```

**O que logar:**
- Início e fim de cada etapa com timestamps
- Volume de dados (linhas lidas, linhas processadas, linhas descartadas)
- Erros com contexto suficiente para reproduzir
- Alertas quando métricas estão fora do esperado

**O que NÃO logar:**
- Dados sensíveis (PII, senhas, tokens)
- Conteúdo de linhas individuais (em produção)

## 5. Métricas de Monitoramento

Métricas básicas para qualquer pipeline:

| Métrica                  | O que indica                              |
|--------------------------|-------------------------------------------|
| Tempo de execução        | Degradação de performance                 |
| Volume processado        | Anomalias (muito pouco = problema na fonte)|
| Taxa de erros            | Falhas de transformação                   |
| Freshness (atraso)       | Pipeline atrasado em relação ao SLA       |
| Taxa de nulos por coluna | Deterioração da qualidade da fonte        |
```

- [ ] **Passo 3: Criar exercícios**

Criar `modulos/08-qualidade-observabilidade/exercicios/exercicios.md`:

```markdown
# Exercícios — Qualidade e Observabilidade

## Ex 8.1 — Identificar problemas de qualidade

Dado o dataset abaixo, identifique quais dimensões de qualidade estão violadas e como você as trataria:

```csv
venda_id,cliente_id,produto_id,quantidade,data_venda,valor_total
1,1,1,1,2024-01-10,3500.00
1,1,1,1,2024-01-10,3500.00
2,2,99,3,2024-01-15,
3,,3,0,2024-02-01,-299.00
4,3,5,1,31/13/2024,799.00
```

## Ex 8.2 — Validações em pipeline

Escreva uma função `validar_dataframe(df)` que verifica:
- Schema: colunas `venda_id`, `cliente_id`, `produto_id`, `quantidade`, `data_venda`, `valor_total` existem
- Unicidade: `venda_id` não tem duplicatas
- Completude: `cliente_id` e `produto_id` não têm nulos
- Valores: `valor_total >= 0` e `quantidade > 0`

A função deve levantar `ValidacaoError` com mensagem descritiva para cada violação encontrada.

## Ex 8.3 — Testes unitários

Escreva testes unitários para a função `transformar` do módulo 5. Cubra pelo menos:
- Caso feliz: transformação correta com dados válidos
- Duplicatas: verifica que são removidas
- Nulos em `valor_total`: verifica que são preenchidos com 0
- Cálculo de `valor_unitario`: verifica que está correto

## Ex 8.4 — Pipeline com qualidade integrada

Adicione ao pipeline do módulo 5 (`etl_idempotente.py`):
1. Validação dos dados antes da transformação (usando Ex 8.2)
2. Log de métricas: linhas lidas, linhas após validação, linhas salvas
3. Log de alertas se mais de 5% das linhas forem descartadas na validação
```

- [ ] **Passo 4: Criar gabarito**

Criar `modulos/08-qualidade-observabilidade/exercicios/gabarito.md`:

```markdown
# Gabarito — Qualidade e Observabilidade

## Ex 8.1

| Linha | Problema                           | Dimensão       | Tratamento                        |
|-------|------------------------------------|----------------|-----------------------------------|
| 1+2   | venda_id=1 duplicado               | Unicidade      | drop_duplicates(subset=['venda_id'])|
| 2     | produto_id=99 não existe           | Consistência   | validar FK contra tabela produtos |
| 2     | valor_total nulo                   | Completude     | fillna(0) ou rejeitar a linha     |
| 3     | cliente_id nulo                    | Completude     | rejeitar a linha                  |
| 3     | quantidade=0 e valor_total negativo| Acurácia       | rejeitar a linha                  |
| 4     | data_venda em formato inválido     | Acurácia       | pd.to_datetime com errors='coerce'|

## Ex 8.2

```python
class ValidacaoError(Exception):
    pass


def validar_dataframe(df: pd.DataFrame) -> None:
    colunas = ['venda_id', 'cliente_id', 'produto_id', 'quantidade', 'data_venda', 'valor_total']
    ausentes = [c for c in colunas if c not in df.columns]
    if ausentes:
        raise ValidacaoError(f"Colunas ausentes: {ausentes}")

    duplicatas = df['venda_id'].duplicated().sum()
    if duplicatas > 0:
        raise ValidacaoError(f"venda_id tem {duplicatas} duplicatas")

    for col in ['cliente_id', 'produto_id']:
        nulos = df[col].isna().sum()
        if nulos > 0:
            raise ValidacaoError(f"Coluna '{col}' tem {nulos} nulos")

    negativos = (df['valor_total'] < 0).sum()
    if negativos > 0:
        raise ValidacaoError(f"{negativos} linhas com valor_total negativo")

    zeros = (df['quantidade'] <= 0).sum()
    if zeros > 0:
        raise ValidacaoError(f"{zeros} linhas com quantidade <= 0")
```

## Ex 8.3

```python
import pytest
import pandas as pd
from pipeline import transformar, limpar_dados


def make_df(**kwargs):
    defaults = {
        'venda_id': [1],
        'cliente_id': [1],
        'produto_id': [1],
        'quantidade': [2],
        'data_venda': ['2024-01-01'],
        'valor_total': [200.0],
    }
    defaults.update(kwargs)
    return pd.DataFrame(defaults)


def test_transformar_caso_feliz():
    df = make_df(valor_total=[300.0], quantidade=[3])
    resultado = transformar(df)
    assert resultado['valor_unitario'].iloc[0] == 100.0


def test_transformar_remove_duplicatas():
    df = pd.concat([make_df(), make_df()]).reset_index(drop=True)
    resultado = transformar(df)
    assert len(resultado) == 1


def test_transformar_preenche_nulos_valor():
    df = make_df(valor_total=[None])
    resultado = transformar(df)
    assert resultado['valor_total'].iloc[0] == 0.0


def test_transformar_calcula_valor_unitario():
    df = make_df(valor_total=[100.0], quantidade=[4])
    resultado = transformar(df)
    assert resultado['valor_unitario'].iloc[0] == 25.0
```

## Ex 8.4

```python
import logging
logger = logging.getLogger(__name__)


def main():
    try:
        df_raw = extrair()
        logger.info(f"Extraídas {len(df_raw)} linhas")

        try:
            validar_dataframe(df_raw)
        except ValidacaoError as e:
            logger.warning(f"Validação encontrou problemas: {e}")

        df_valido = df_raw.dropna(subset=['cliente_id', 'produto_id'])
        df_valido = df_valido[df_valido['valor_total'] >= 0]
        df_valido = df_valido[df_valido['quantidade'] > 0]

        descartadas = len(df_raw) - len(df_valido)
        pct_descartadas = descartadas / len(df_raw) if len(df_raw) > 0 else 0
        if pct_descartadas > 0.05:
            logger.warning(f"ALERTA: {pct_descartadas:.1%} das linhas descartadas na validação")

        df_clean = transformar(df_valido)
        carregar(df_clean)

        logger.info(f"Pipeline OK | lidas={len(df_raw)} | válidas={len(df_valido)} | salvas={len(df_clean)}")
    except Exception as e:
        logger.error(f"Falha: {e}")
        raise
```

- [ ] **Passo 5: Criar roteiro da sessão ao vivo**

Criar `modulos/08-qualidade-observabilidade/sessao-ao-vivo.md`:

```markdown
# Sessão ao Vivo — Módulo 8: Qualidade e Observabilidade

**Duração:** 2 horas

## Abertura (10 min)
- "Algum de vocês já encontrou dado errado em produção? O que aconteceu?"

## Bloco Conceitual (15 min)
- Revisar as dimensões de qualidade com exemplos reais do time

## Exercício em Grupo (75 min)
**Ex 8.1 ao vivo:** análise coletiva do dataset com problemas.
- Cada um identifica os problemas individualmente (5 min)
- Comparar os achados — alguém viu algo que os outros não viram?
- Propor estratégia de tratamento para cada problema

Bonus: rodar os testes do Ex 8.3 ao vivo e ver os erros antes de implementar (TDD na prática).

## Fechamento (20 min)
- "Qualidade não é uma etapa separada — é parte do pipeline"
- Parabéns pelo percurso: do SELECT ao pipeline com qualidade e observabilidade
- Próximos passos: ferramentas específicas (Databricks, dbt, PySpark avançado)
```
