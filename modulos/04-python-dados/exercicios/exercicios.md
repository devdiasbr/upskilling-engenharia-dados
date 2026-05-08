# Módulo 4 — Exercícios

Todos os exercícios utilizam o banco `recursos/dados.db`.

---

## Exercício 4.1 — Manipulação Básica com Pandas

### a) Carregar os dados de vendas

Conecte ao banco e carregue um DataFrame com as seguintes colunas:
- `venda_id`
- `data_venda`
- `valor_total`
- `cliente_nome` (nome do cliente)
- `produto_nome` (nome do produto)
- `categoria` (nome da categoria)

Utilize `pd.read_sql` com um JOIN que una as tabelas `vendas`, `clientes`, `produtos` e `categorias`.

Ao final, imprima:
- O número total de registros carregados
- As primeiras 5 linhas com `df.head()`
- Os tipos de cada coluna com `df.dtypes`

### b) Filtrar o primeiro trimestre de 2024

A partir do DataFrame carregado no item anterior, filtre apenas as vendas ocorridas entre **01/01/2024 e 31/03/2024** (inclusive).

Dica: converta a coluna `data_venda` para datetime com `pd.to_datetime` antes de filtrar.

Imprima quantas vendas existem nesse período.

### c) Receita total por categoria no primeiro trimestre

Usando o DataFrame filtrado do item b, calcule a receita total por categoria.

O resultado deve conter:
- `categoria`
- `receita_total` (soma de `valor_total`)
- `qtd_vendas` (contagem de vendas)

Ordene do maior para o menor `receita_total` e imprima o resultado completo.

---

## Exercício 4.2 — Funções de Transformação

Crie um arquivo `exercicios/funcoes.py` e implemente as três funções abaixo. Cada função deve receber um DataFrame como entrada e retornar um DataFrame transformado.

### a) `top_clientes(df, n)`

Retorna os `n` clientes com maior receita total.

- Entrada: DataFrame com colunas `cliente_nome` e `valor_total`
- Saída: DataFrame com `cliente_nome` e `receita_total`, ordenado decrescente, limitado a `n` linhas

### b) `vendas_por_mes(df)`

Retorna a receita e a quantidade de vendas agrupadas por mês.

- Entrada: DataFrame com colunas `data_venda` e `valor_total`
- Saída: DataFrame com `periodo` (formato `YYYY-MM`), `receita_total` e `qtd_vendas`, ordenado por `periodo`

### c) `ticket_medio_por_categoria(df)`

Retorna o ticket médio por categoria (valor médio por venda).

- Entrada: DataFrame com colunas `categoria` e `valor_total`
- Saída: DataFrame com `categoria` e `ticket_medio`, ordenado decrescente pelo ticket médio

Ao final do arquivo, adicione um bloco `if __name__ == "__main__"` que:
1. Carregue os dados do banco
2. Chame cada uma das três funções
3. Imprima os resultados

---

## Exercício 4.3 — Script ETL Estruturado

Crie o arquivo `exercicios/pipeline.py` — um script Python executável com estrutura ETL completa.

### Requisitos funcionais

O script deve:

1. **Extrair** — ler do banco `recursos/dados.db` os dados de vendas enriquecidos com:
   - Nome do cliente e estado
   - Nome do produto e categoria

2. **Transformar** — calcular dois agregados:
   - Receita total e quantidade de vendas por **estado**
   - Receita total e quantidade de vendas por **categoria**

3. **Carregar** — salvar os resultados em:
   - `saida/receita_por_estado.parquet`
   - `saida/receita_por_categoria.parquet`

### Requisitos estruturais

- O código deve estar organizado em funções separadas: pelo menos uma função para cada etapa (extrair, transformar, carregar)
- As funções de transformação devem ser independentes e receber apenas DataFrames como entrada
- O ponto de entrada deve ser um bloco `if __name__ == "__main__"`
- O diretório `saida/` deve ser criado automaticamente se não existir

### Execução esperada

```
python exercicios/pipeline.py
```

Saída esperada (valores aproximados):

```
Vendas carregadas: XXXX registros
Salvo: saida/receita_por_estado.parquet (XX linhas)
Salvo: saida/receita_por_categoria.parquet (XX linhas)
Pipeline concluído.
```

### Pergunta para reflexão

O que acontece se a coluna `valor_total` vier com valores nulos para algumas vendas? Como você modificaria a função de transformação para lidar com esse caso?
