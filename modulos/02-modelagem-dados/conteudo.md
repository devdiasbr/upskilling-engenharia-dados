# Conteúdo — Módulo 2: Modelagem de Dados

> Antes de começar, leia o `recursos/schema.md` para entender as tabelas `categorias`, `produtos`, `clientes` e `vendas`.

---

## Seção 1 — Modelagem Relacional

### Conceitos fundamentais

Um **modelo relacional** organiza dados em tabelas com linhas e colunas, onde cada tabela representa uma **entidade** do mundo real. As relações entre entidades são estabelecidas por meio de **chaves**.

**Entidade** é qualquer coisa sobre a qual precisamos armazenar dados. Em um e-commerce:
- `clientes` → a entidade "Cliente"
- `produtos` → a entidade "Produto"
- `categorias` → a entidade "Categoria"
- `vendas` → a entidade "Venda" (ou Transação)

**Atributo** é uma característica da entidade. A entidade `clientes` possui os atributos `nome`, `email`, `cidade`, `estado` e `data_cadastro`.

**Chave primária (PK)** é o atributo (ou conjunto de atributos) que identifica unicamente cada linha de uma tabela. Nunca pode ser nulo e nunca deve se repetir.

```
clientes
+-----------+-----------------------+----------------------------+--------+--------+---------------+
| cliente_id| nome                  | email                      | cidade | estado | data_cadastro |
+-----------+-----------------------+----------------------------+--------+--------+---------------+
|     1     | Maria Souza           | maria@email.com            | SP     | SP     | 2023-03-15    |
|     2     | João Oliveira         | joao@email.com             | RJ     | RJ     | 2023-07-22    |
+-----------+-----------------------+----------------------------+--------+--------+---------------+
     ^
     PK
```

**Chave estrangeira (FK)** é um atributo em uma tabela que referencia a chave primária de outra tabela. Ela cria o vínculo entre entidades.

```
produtos
+------------+--------------------+-------------+--------+
| produto_id | nome               | categoria_id| preco  |
+------------+--------------------+-------------+--------+
|     1      | Notebook Pro       |      1      | 3500.00|
|     2      | Camiseta Básica    |      2      |   89.90|
+------------+--------------------+-------------+--------+
                                        ^
                                        FK → categorias(categoria_id)
```

---

### Cardinalidade dos relacionamentos

A **cardinalidade** descreve quantas instâncias de uma entidade se relacionam com instâncias de outra. Os três padrões principais são:

#### 1:1 — Um para Um

Cada registro de A se relaciona com no máximo um registro de B, e vice-versa.

Exemplo: cada usuário tem um único perfil estendido.

```
usuarios (1) ──── (1) perfis_usuarios
```

Esse padrão é raro no banco atual mas aparece quando dividimos uma tabela grande por razões de acesso ou performance.

#### 1:N — Um para Muitos

Um registro de A se relaciona com vários registros de B, mas cada registro de B pertence a apenas um A.

Exemplos no nosso e-commerce:

```
categorias (1) ──────< (N) produtos
```
Uma categoria como "Eletronicos" contém muitos produtos. Cada produto pertence a apenas uma categoria.

```
clientes (1) ──────< (N) vendas
```
Um cliente pode realizar muitas compras. Cada venda pertence a apenas um cliente.

```
produtos (1) ──────< (N) vendas
```
Um produto pode aparecer em muitas vendas. Cada linha de venda referencia um único produto.

Para implementar um relacionamento 1:N, a chave primária do lado "1" torna-se uma chave estrangeira no lado "N":

```sql
-- O produto_id na tabela vendas é a FK que implementa o relacionamento 1:N
SELECT v.venda_id, p.nome AS produto, v.quantidade, v.valor_total
FROM vendas v
JOIN produtos p ON v.produto_id = p.produto_id
LIMIT 5;
```

#### N:M — Muitos para Muitos

Um registro de A pode se relacionar com vários registros de B, e cada registro de B pode se relacionar com vários de A.

Exemplo clássico: pedidos e produtos em um e-commerce real. Um pedido contém muitos produtos, e um produto pode estar em muitos pedidos.

Relacionamentos N:M **não podem ser implementados diretamente** entre duas tabelas. Precisamos de uma **tabela associativa** (ou tabela de junção):

```
pedidos (N) ──────< (1) itens_pedido (1) >────── (N) produtos
```

```
itens_pedido
+------------+-----------+-----------+----------+
| item_id    | pedido_id | produto_id| qtd      |
+------------+-----------+-----------+----------+
|     1      |    101    |     5     |    2     |
|     2      |    101    |    12     |    1     |
|     3      |    102    |     5     |    3     |
+------------+-----------+-----------+----------+
```

> Observação: no `dados.db`, a tabela `vendas` simplifica esse modelo — cada linha de venda é um único produto comprado por um único cliente. Em um sistema de produção real, teríamos as entidades `pedidos` e `itens_pedido` separadas.

---

### Como o schema atual implementa esses conceitos

Veja o schema completo do `dados.db` e como ele se encaixa no modelo relacional:

```
+---------------+          +------------------+
|  categorias   |          |     produtos     |
+---------------+          +------------------+
| categoria_id PK|<--------| produto_id PK    |
| nome          |    1:N   | nome             |
+---------------+          | categoria_id FK  |
                            | preco            |
                            +------------------+
                                    |
                                   1:N
                                    |
+---------------+          +------------------+
|   clientes    |          |     vendas       |
+---------------+          +------------------+
| cliente_id PK |<---------| venda_id PK      |
| nome          |    1:N   | cliente_id FK    |
| email         |          | produto_id FK    |----> produtos
| cidade        |          | quantidade       |
| estado        |          | data_venda       |
| data_cadastro |          | valor_total      |
+---------------+          +------------------+
```

A tabela `vendas` é uma tabela de **fatos** (eventos que ocorreram no negócio) com FKs para as entidades de contexto. Essa estrutura é a base do modelo dimensional que veremos na Seção 3.

---

## Seção 2 — Normalização

**Normalização** é o processo de organizar uma base de dados para reduzir redundância e garantir integridade dos dados. O objetivo é que cada dado esteja armazenado em um único lugar — qualquer atualização, então, precisa ser feita em apenas um ponto.

### Primeira Forma Normal (1FN)

**Regra:** cada célula deve conter um valor atômico (indivisível). Sem listas, conjuntos ou grupos repetidos dentro de uma coluna.

**Violação típica — lista de produtos numa célula:**

```
vendas_desnormalizada
+-----------+-----------+----------------------------------+--------+
| venda_id  | cliente   | produtos_comprados               | total  |
+-----------+-----------+----------------------------------+--------+
|     1     | Maria S.  | Notebook Pro, Camiseta Básica    | 3589.90|
|     2     | João O.   | Livro de Python                  |   89.00|
+-----------+-----------+----------------------------------+--------+
```

O campo `produtos_comprados` viola a 1FN porque armazena múltiplos valores numa única célula. Problemas:
- Impossível filtrar por produto com `WHERE`
- Impossível calcular quantidade por produto
- Impossível fazer JOIN com a tabela de produtos

**Correção — separar em linhas atômicas:**

```
vendas_normalizada_1fn
+-----------+-----------+-------------------+----------+--------+
| venda_id  | cliente   | produto           | qtd      | preco  |
+-----------+-----------+-------------------+----------+--------+
|     1     | Maria S.  | Notebook Pro      |    1     |3500.00 |
|     2     | Maria S.  | Camiseta Básica   |    1     |  89.90 |
|     3     | João O.   | Livro de Python   |    1     |  89.00 |
+-----------+-----------+-------------------+----------+--------+
```

O banco `dados.db` já respeita a 1FN: cada linha de `vendas` contém um único produto, cliente, quantidade e valor.

---

### Segunda Forma Normal (2FN)

**Regra:** a tabela deve estar em 1FN, e todos os atributos não-chave devem depender **completamente** da chave primária. Aplicável principalmente quando a PK é composta (formada por mais de uma coluna).

**Violação típica — dependência parcial da PK:**

Imagine uma tabela de itens de pedido com PK composta (`pedido_id`, `produto_id`):

```
itens_pedido_violacao
+-----------+------------+------------------+----------+--------+
| pedido_id | produto_id | nome_produto     | qtd      | preco  |
+-----------+------------+------------------+----------+--------+
|    101    |     5      | Notebook Pro     |    1     |3500.00 |
|    101    |    12      | Camiseta Básica  |    2     |  89.90 |
|    102    |     5      | Notebook Pro     |    1     |3500.00 |
+-----------+------------+------------------+----------+--------+
```

O atributo `nome_produto` depende apenas de `produto_id`, não da PK composta inteira (`pedido_id` + `produto_id`). Isso é uma **dependência parcial** — violação da 2FN.

Consequências:
- `nome_produto` se repete em toda linha que tem o mesmo produto (redundância)
- Atualizar o nome de um produto exige atualizar múltiplas linhas
- Risco de inconsistência: duas linhas com o mesmo `produto_id` podem ter `nome_produto` diferente

**Correção — separar na tabela de produtos:**

```
itens_pedido (2FN)           produtos (2FN)
+-----------+------------+   +------------+------------------+--------+
| pedido_id | produto_id |   | produto_id | nome_produto     | preco  |
| qtd       |            |   +------------+------------------+--------+
+-----------+------------+   |     5      | Notebook Pro     |3500.00 |
                             |    12      | Camiseta Básica  |  89.90 |
                             +------------+------------------+--------+
```

O schema do `dados.db` já está em 2FN: `produtos` tem sua própria PK simples, e `vendas` armazena apenas FKs para `clientes` e `produtos`.

---

### Terceira Forma Normal (3FN)

**Regra:** a tabela deve estar em 2FN, e nenhum atributo não-chave deve depender de outro atributo não-chave. Ou seja, sem **dependências transitivas**.

**Violação — `cidade` determinando `estado`:**

Imagine que a tabela `produtos` tivesse colunas de localização do fornecedor:

```
produtos_violacao
+------------+-----------+----------+--------+---------+
| produto_id | nome      | preco    | cidade | estado  |
+------------+-----------+----------+--------+---------+
|     1      | Notebook  | 3500.00  | SP     | SP      |
|     2      | Camiseta  |   89.90  | RJ     | RJ      |
|     3      | Livro     |   89.00  | SP     | SP      |
+------------+-----------+----------+--------+---------+
```

Aqui `estado` depende de `cidade`, não de `produto_id`. A cadeia de dependência é:
```
produto_id → cidade → estado  (dependência transitiva)
```

Consequências:
- Se a cidade "SP" mudar de estado (hipotético), precisamos atualizar vários produtos
- A relação cidade-estado fica embutida em cada linha de produto

**Correção — extrair para tabela própria:**

```
produtos (3FN)              cidades (3FN)
+------------+------+------+ +--------+--------+
| produto_id | nome | preco| | cidade | estado |
+------------+------+------+ +--------+--------+
                             | SP     | SP     |
                             | RJ     | RJ     |
                             +--------+--------+
```

**Agora, vejamos o schema real do `dados.db`:**

A tabela `clientes` armazena `cidade` e `estado` como atributos separados:

```sql
SELECT cidade, estado, COUNT(*) AS qtd_clientes
FROM clientes
GROUP BY cidade, estado
ORDER BY qtd_clientes DESC
LIMIT 5;
```

Isso está correto para o contexto do módulo. Em um sistema de produção, `cidade` e `estado` provavelmente viveriam em tabelas separadas de localização — mas isso depende da granularidade necessária e da taxa de mudança desses dados. Normalização é sempre uma decisão de trade-off.

---

### Quando desnormalizar

Normalização maximiza integridade e elimina redundância. Mas há cenários onde a desnormalização é justificada:

| Cenário | Justificativa |
|---|---|
| Relatórios com muitas tabelas | Reduzir o número de JOINs melhora performance |
| Leitura muito mais frequente que escrita | A redundância tem custo baixo se os dados raramente mudam |
| Data warehouses e sistemas de BI | O foco é velocidade de leitura analítica, não integridade transacional |
| Dashboards com consultas repetitivas | Agregar previamente os dados reduz carga no banco |

**Exemplo prático:** em vez de fazer JOIN entre `vendas`, `produtos` e `categorias` a cada consulta de relatório, podemos criar uma tabela desnormalizada:

```
vendas_desnormalizada
+-----------+------------+------------------+-----------+-------------------+--------+----------+------------+
| venda_id  | cliente_id | nome_cliente     | produto_id| nome_produto      | preco  | qtd      | data_venda |
+-----------+------------+------------------+-----------+-------------------+--------+----------+------------+
```

Essa tabela viola a 3FN mas acelera consultas analíticas — é exatamente o padrão de uma tabela fato no modelo dimensional.

---

## Seção 3 — Modelagem Dimensional

A **modelagem dimensional** é uma técnica de design de banco de dados otimizada para consultas analíticas (OLAP). Em vez de minimizar redundância como na normalização, o objetivo é maximizar a **velocidade de leitura** e a **facilidade de entendimento** dos dados.

### Tabela Fato

A **tabela fato** registra eventos ou transações do negócio. Seus atributos principais são:

- **Métricas numéricas** (o que medimos): `quantidade`, `valor_total`, `desconto`
- **Chaves estrangeiras** para as dimensões (o contexto do evento)
- **Grão**: o nível de detalhe de cada linha — "uma linha por venda de um produto para um cliente em uma data"

```
fato_vendas
+-----------+------------+-----------+----------+------------------+
| venda_id  | cliente_sk | produto_sk| tempo_sk | valor_total      |
| (SK)      | (FK)       | (FK)      | (FK)     | quantidade       |
+-----------+------------+-----------+----------+------------------+
```

> SK = surrogate key (chave substituta, gerada pelo DW). Não confundir com as PKs do sistema transacional.

### Tabela Dimensão

A **tabela dimensão** fornece o contexto descritivo do evento — quem, o quê, quando e onde. Seus atributos são principalmente textuais e descritivos.

```
dim_cliente               dim_produto               dim_tempo
+-----------+             +------------+            +----------+
| cliente_sk|             | produto_sk |            | tempo_sk |
| cliente_id|             | produto_id |            | data     |
| nome      |             | nome       |            | dia      |
| email     |             | preco      |            | mes      |
| cidade    |             | categoria  |            | trimestre|
| estado    |             | nome_cat   |            | ano      |
| regiao    |             +------------+            | dia_semana|
+-----------+                                       | eh_fimdesemana|
                                                    +----------+
```

### Star Schema

O **star schema** (esquema estrela) coloca a tabela fato no centro, conectada diretamente a tabelas de dimensão desnormalizadas. Visualmente forma uma estrela.

```
                    +------------------+
                    |   dim_cliente    |
                    | cliente_sk (PK)  |
                    | nome             |
                    | cidade           |
                    | estado           |
                    +--------+---------+
                             |
                             | FK
                             |
+-----------------+  FK      v         FK  +------------------+
|   dim_tempo     +----> fato_vendas <-----+   dim_produto    |
| tempo_sk (PK)   |    +----------------+  | produto_sk (PK)  |
| data            |    | venda_id (PK)  |  | nome             |
| dia             |    | cliente_sk (FK)|  | preco            |
| mes             |    | produto_sk (FK)|  | categoria_id     |
| trimestre       |    | tempo_sk (FK)  |  | nome_categoria   |
| ano             |    | valor_total    |  +------------------+
| dia_da_semana   |    | quantidade     |
+-----------------+    +----------------+
```

Vantagens do star schema:
- Queries simples com poucos JOINs
- Alta performance em ferramentas de BI
- Fácil de entender por analistas de negócio

### Snowflake Schema

O **snowflake schema** normaliza as dimensões do star schema, criando tabelas adicionais para atributos hierárquicos. As dimensões "floreiam" a partir da tabela fato.

```
                    dim_categoria
                    +---------------+
                    | categoria_id  |
                    | nome_categoria|
                    +-------+-------+
                            |
                           1:N
                            |
dim_tempo              dim_produto              dim_cliente
+-----------+          +-----------+            +-----------+
| tempo_sk  |          | produto_sk|            | cliente_sk|
| data      |          | nome      |            | nome      |
| dia       |          | preco     |            | cidade_id |----> dim_cidade
| mes       |          | categ_id FK|           | ...       |       (cidade, estado)
| trimestre |          +-----------+            +-----------+
| ano       |               |
+-----------+               |
            \             FK|
             \              v
              +--------> fato_vendas
                         +-----------+
                         | venda_id  |
                         | cliente_sk|
                         | produto_sk|
                         | tempo_sk  |
                         | valor     |
                         | qtd       |
                         +-----------+
```

Vantagens do snowflake:
- Menor redundância nas dimensões
- Útil quando dimensões são muito grandes (ex: 500 cidades, 27 estados)

Desvantagens:
- Mais JOINs para chegar ao atributo desejado
- Queries mais complexas
- Ferramentas de BI podem ter dificuldade

**Regra prática:** prefira star schema. Use snowflake somente quando dimensões tiverem hierarquias muito profundas e alto volume de dados que tornem a redundância custosa.

---

### Aplicando ao e-commerce: do schema atual para o modelo dimensional

O schema do `dados.db` é um modelo relacional transacional. Para transformá-lo em um data warehouse dimensional, precisamos:

**1. Criar a dimensão de tempo** — `data_venda` em `vendas` é apenas uma coluna DATE. No modelo dimensional, explodir essa data em atributos analíticos:

```sql
-- No modelo relacional atual, data é apenas uma string ISO
SELECT data_venda, COUNT(*) AS vendas
FROM vendas
GROUP BY data_venda
ORDER BY data_venda;

-- No modelo dimensional, a dim_tempo permitiria:
-- GROUP BY ano, trimestre, mes
-- WHERE dia_da_semana = 'segunda'
-- WHERE eh_fimdesemana = TRUE
```

**2. Desnormalizar dimensões** — `dim_produto` no modelo dimensional incluiria `nome_categoria` diretamente, eliminando o JOIN com `categorias`:

```
dim_produto (star schema — desnormalizada)
+------------+--------------------+-------------------+--------+
| produto_sk | nome               | nome_categoria    | preco  |
+------------+--------------------+-------------------+--------+
|     1      | Notebook Pro       | Eletronicos       |3500.00 |
|     2      | Camiseta Básica    | Roupas            |  89.90 |
+------------+--------------------+-------------------+--------+
```

**3. Projetar a tabela fato** com todas as FKs e métricas:

```sql
-- Query equivalente à fato_vendas no schema atual
SELECT
    v.venda_id,
    v.cliente_id,
    v.produto_id,
    v.data_venda,
    v.quantidade,
    v.valor_total
FROM vendas v;
```

---

## Seção 4 — Quando Usar Cada Modelagem

### Modelagem Relacional — para sistemas transacionais (OLTP)

**Online Transaction Processing (OLTP)** são sistemas que processam operações do dia a dia: inserir um pedido, atualizar um estoque, cadastrar um cliente.

| Característica | OLTP (Relacional) |
|---|---|
| Operações dominantes | INSERT, UPDATE, DELETE |
| Volume por transação | Poucas linhas |
| Foco | Integridade e consistência |
| Exemplo | E-commerce, ERP, CRM |
| Técnica de modelagem | Normalizada (3FN) |

O schema do `dados.db` simula um OLTP: cada `venda` é uma transação pontual, as FKs garantem que não vendemos produtos ou clientes inexistentes.

### Modelagem Dimensional — para análise e BI (OLAP)

**Online Analytical Processing (OLAP)** são sistemas que respondem perguntas analíticas: "Qual categoria vendeu mais no Q3? Qual estado tem o maior ticket médio?"

| Característica | OLAP (Dimensional) |
|---|---|
| Operações dominantes | SELECT com agregações |
| Volume por consulta | Milhões de linhas |
| Foco | Performance de leitura e intuitividade |
| Exemplo | Data warehouse, BI, dashboards |
| Técnica de modelagem | Dimensional (star/snowflake) |

### O mesmo dado, dois propósitos

Na prática, o mesmo dado percorre dois caminhos:

```
[Sistema Transacional] ──ETL──> [Data Warehouse]
    (OLTP / Relacional)            (OLAP / Dimensional)
    dados.db (3FN)                 fato_vendas + dims

    Garante que:                   Permite responder:
    - a venda foi registrada       - quais produtos vendem mais
    - o cliente existe             - sazonalidade por mês
    - o estoque foi atualizado     - performance por região
```

**ETL** (Extract, Transform, Load) é o processo que move dados do OLTP para o OLAP, aplicando as transformações necessárias — incluindo a criação da `dim_tempo` e a desnormalização das dimensões.

### Guia de decisão rápida

```
Pergunta                              Resposta → Modelo
---------------------------------------------------------------------------
Preciso garantir integridade          Sim → Relacional (OLTP)
Preciso responder perguntas analíticas Sim → Dimensional (OLAP)
Tenho INSERT/UPDATE frequentes        Sim → Relacional
Tenho SELECT com GROUP BY pesados     Sim → Dimensional
Está em produção (app/site)?          Sim → Relacional
Está em um dashboard/relatório?       Sim → Dimensional
```

### Resumo do módulo

| Conceito | Definição curta |
|---|---|
| Entidade | Objeto do mundo real sobre o qual armazenamos dados |
| Atributo | Característica de uma entidade |
| Chave primária (PK) | Identificador único de cada linha |
| Chave estrangeira (FK) | Referência à PK de outra tabela |
| 1FN | Valores atômicos, sem grupos repetidos |
| 2FN | Dependência total da PK (sem dependência parcial) |
| 3FN | Sem dependência transitiva entre atributos |
| Tabela Fato | Registra eventos com métricas e FKs para dimensões |
| Tabela Dimensão | Fornece contexto descritivo para os eventos |
| Star Schema | Fato no centro, dimensões desnormalizadas ao redor |
| Snowflake Schema | Dimensões normalizadas com hierarquias explícitas |
| OLTP | Sistemas transacionais — foco em escrita e integridade |
| OLAP | Sistemas analíticos — foco em leitura e performance |
