# Módulo 4 — Python para Dados: Conteúdo

---

## Seção 1 — Estruturas de Dados Essenciais

Antes de trabalhar com pandas, é importante dominar as estruturas nativas do Python mais usadas em pipelines de dados.

### Listas

Listas são coleções ordenadas e mutáveis. Em dados, usamos listas para acumular resultados, iterar registros e passar parâmetros.

```python
estados = ["SP", "RJ", "MG", "BA"]

# Adicionar elemento
estados.append("RS")

# Iterar
for estado in estados:
    print(estado)

# Slicing — primeiros 3
print(estados[:3])
```

### Dicionários

Dicionários mapeiam chave a valor. São a estrutura mais próxima de um registro de banco ou de uma linha JSON.

```python
cliente = {
    "nome": "Ana Lima",
    "cidade": "São Paulo",
    "estado": "SP",
    "total_compras": 3450.00
}

# Acessar valor
print(cliente["nome"])

# Acessar com valor padrão (evita KeyError)
print(cliente.get("email", "não informado"))

# Iterar chaves e valores
for campo, valor in cliente.items():
    print(f"{campo}: {valor}")
```

### Sets

Sets são coleções sem ordem e sem duplicatas. Úteis para encontrar valores únicos rapidamente.

```python
cidades_vendas = {"São Paulo", "Rio de Janeiro", "São Paulo", "Belo Horizonte"}
print(cidades_vendas)
# {'São Paulo', 'Rio de Janeiro', 'Belo Horizonte'}

# Verificar presença
print("São Paulo" in cidades_vendas)  # True
```

### List comprehension

List comprehension é uma forma compacta e legível de construir listas a partir de iteráveis — muito comum em código de dados.

```python
# Sem comprehension
valores = []
for v in [100, 200, None, 350, None]:
    if v is not None:
        valores.append(v)

# Com comprehension (equivalente)
valores = [v for v in [100, 200, None, 350, None] if v is not None]

# Transformação + filtro
nomes_maiusculo = [nome.upper() for nome in ["ana", "carlos", "julia"]]
# ['ANA', 'CARLOS', 'JULIA']
```

---

## Seção 2 — Lendo do SQLite com Python

O banco `recursos/dados.db` contém os dados que usaremos ao longo de toda a trilha. Existem duas formas principais de lê-lo com Python.

### Forma 1 — sqlite3 puro

O módulo `sqlite3` já vem com o Python. É adequado quando você precisa de controle granular ou está escrevendo um script sem dependências externas.

```python
import sqlite3

conn = sqlite3.connect('recursos/dados.db')

cursor = conn.execute("""
    SELECT c.nome, SUM(v.valor_total) as total
    FROM vendas v
    JOIN clientes c ON v.cliente_id = c.cliente_id
    GROUP BY c.cliente_id
    ORDER BY total DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

conn.close()
```

Cada `row` é uma tupla — você acessa os campos por posição (`row[0]`, `row[1]`).

### Forma 2 — pandas com read_sql

`pd.read_sql` executa a query e já devolve um DataFrame, que é a estrutura ideal para análise e transformação.

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('recursos/dados.db')

df = pd.read_sql("""
    SELECT c.nome, c.cidade, c.estado,
           COUNT(v.venda_id) as qtd_compras,
           SUM(v.valor_total) as total_gasto
    FROM clientes c
    LEFT JOIN vendas v ON c.cliente_id = v.cliente_id
    GROUP BY c.cliente_id
""", conn)

conn.close()

print(df.head())
```

Use `LEFT JOIN` quando quiser manter todos os clientes, mesmo os que nunca compraram (esses terão `qtd_compras` e `total_gasto` como `NaN`).

### Boas práticas de conexão

```python
# Usando context manager — fecha a conexão automaticamente
with sqlite3.connect('recursos/dados.db') as conn:
    df = pd.read_sql("SELECT * FROM produtos", conn)
```

---

## Seção 3 — Operações Essenciais com Pandas

### Inspeção inicial

Ao receber qualquer DataFrame, comece sempre com estas checagens:

```python
print(df.shape)        # (linhas, colunas)
print(df.dtypes)       # tipo de cada coluna
print(df.head(10))     # primeiras 10 linhas
print(df.describe())   # estatísticas descritivas das colunas numéricas
print(df.isnull().sum())  # contagem de nulos por coluna
```

### Filtros

```python
# Filtro simples
vendas_sp = df[df["estado"] == "SP"]

# Múltiplas condições — use & (E) e | (OU) com parênteses
vendas_sp_2024 = df[(df["estado"] == "SP") & (df["ano"] == 2024)]

# Filtro por lista de valores (equivalente ao IN do SQL)
estados_sul = df[df["estado"].isin(["RS", "SC", "PR"])]
```

### Seleção de colunas

```python
# Selecionar colunas específicas
df_resumo = df[["nome", "cidade", "total_gasto"]]

# Excluir uma coluna
df_sem_id = df.drop(columns=["cliente_id"])
```

### Nova coluna calculada

```python
# Coluna derivada de outras
df["ticket_medio"] = df["total_gasto"] / df["qtd_compras"]

# Coluna condicional com apply
df["perfil"] = df["total_gasto"].apply(
    lambda x: "alto valor" if x > 1000 else "padrão"
)
```

### merge — equivalente ao JOIN do SQL

```python
# INNER JOIN entre vendas e clientes
df_enriquecido = pd.merge(
    df_vendas,
    df_clientes[["cliente_id", "nome", "estado"]],
    on="cliente_id",
    how="inner"
)

# LEFT JOIN
df_enriquecido = pd.merge(
    df_clientes,
    df_vendas,
    on="cliente_id",
    how="left"
)
```

### groupby + agg

```python
# Receita e quantidade de vendas por categoria
resumo = (
    df
    .groupby("categoria")
    .agg(
        receita_total=("valor_total", "sum"),
        qtd_vendas=("venda_id", "count"),
        ticket_medio=("valor_total", "mean")
    )
    .reset_index()
    .sort_values("receita_total", ascending=False)
)
```

O `reset_index()` transforma o índice do groupby em colunas normais. O `sort_values` ordena o resultado.

### Tratamento de nulos

```python
# Substituir nulos por zero
df["valor_total"] = df["valor_total"].fillna(0)

# Remover linhas com nulo em colunas críticas
df = df.dropna(subset=["cliente_id", "valor_total"])

# Verificar se há nulos
print(df["valor_total"].isnull().any())
```

### Leitura e escrita de arquivos

```python
# CSV
df.to_csv("saida/resultado.csv", index=False)
df_lido = pd.read_csv("saida/resultado.csv")

# JSON
df.to_json("saida/resultado.json", orient="records", force_ascii=False)
df_lido = pd.read_json("saida/resultado.json")

# Parquet — formato colunar recomendado para pipelines
df.to_parquet("saida/resultado.parquet", index=False)
df_lido = pd.read_parquet("saida/resultado.parquet")
```

O Parquet é o formato preferido em pipelines de dados por ser comprimido, tipado e de leitura muito mais rápida que CSV para grandes volumes.

---

## Seção 4 — Funções Reutilizáveis

### Por que funções?

Código de análise escrito de forma linear — célula por célula ou bloco por bloco — se torna difícil de testar, reutilizar e manter. Organizar as transformações em funções com responsabilidade única é a base de qualquer pipeline de qualidade.

**Responsabilidade única**: cada função faz uma coisa só e faz bem.

### Padrão de assinatura para funções de transformação

```python
import pandas as pd


def top_clientes(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    Retorna os N clientes com maior receita total.

    Parâmetros
    ----------
    df : DataFrame com colunas 'nome' e 'valor_total'
    n  : quantidade de clientes a retornar

    Retorna
    -------
    DataFrame com colunas 'nome' e 'receita_total', ordenado decrescente
    """
    return (
        df
        .groupby("nome")
        .agg(receita_total=("valor_total", "sum"))
        .reset_index()
        .sort_values("receita_total", ascending=False)
        .head(n)
    )


def receita_por_periodo(df: pd.DataFrame, coluna_data: str) -> pd.DataFrame:
    """
    Agrega receita total por mês/ano a partir de uma coluna de data.

    Parâmetros
    ----------
    df           : DataFrame com colunas 'valor_total' e a coluna de data informada
    coluna_data  : nome da coluna de data (ex: 'data_venda')

    Retorna
    -------
    DataFrame com 'periodo' (YYYY-MM) e 'receita_total'
    """
    df = df.copy()
    df["periodo"] = pd.to_datetime(df[coluna_data]).dt.to_period("M").astype(str)
    return (
        df
        .groupby("periodo")
        .agg(receita_total=("valor_total", "sum"))
        .reset_index()
        .sort_values("periodo")
    )
```

### Boas práticas

- Use type hints (`df: pd.DataFrame`, `n: int`) para deixar a intenção clara
- Docstrings curtas descrevendo parâmetros e retorno
- Use `df.copy()` dentro da função quando for modificar o DataFrame — evita efeitos colaterais
- Funções que recebem DataFrame e retornam DataFrame são fáceis de encadear e testar

---

## Seção 5 — Estrutura de um Script Python para Dados

### O padrão ETL

Um script de dados bem estruturado separa claramente três responsabilidades:

1. **Extrair** — ler os dados da fonte (banco, arquivo, API)
2. **Transformar** — aplicar limpeza, enriquecimento e cálculos
3. **Carregar** — persistir o resultado no destino (arquivo, banco, cloud)

Essa estrutura é a base de um ETL (Extract, Transform, Load) — tema central do Módulo 5.

### Script completo de exemplo

O script abaixo lê dados do banco `recursos/dados.db`, calcula receita por categoria e por estado, e salva os resultados em Parquet.

```python
"""
pipeline_exemplo.py
Lê dados de vendas do banco SQLite, calcula receita por categoria e por estado,
e salva os resultados em arquivos Parquet.
"""

import os
import sqlite3
import pandas as pd


# ─────────────────────────────────────────────
# EXTRAIR
# ─────────────────────────────────────────────

def extrair_vendas(caminho_db: str) -> pd.DataFrame:
    """Lê vendas enriquecidas com cliente e produto do banco."""
    query = """
        SELECT
            v.venda_id,
            v.data_venda,
            v.valor_total,
            c.nome        AS cliente_nome,
            c.estado,
            p.nome        AS produto_nome,
            cat.nome      AS categoria
        FROM vendas v
        JOIN clientes  c   ON v.cliente_id  = c.cliente_id
        JOIN produtos  p   ON v.produto_id  = p.produto_id
        JOIN categorias cat ON p.categoria_id = cat.categoria_id
    """
    with sqlite3.connect(caminho_db) as conn:
        return pd.read_sql(query, conn)


# ─────────────────────────────────────────────
# TRANSFORMAR
# ─────────────────────────────────────────────

def receita_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega receita total e quantidade de vendas por categoria."""
    return (
        df
        .groupby("categoria")
        .agg(
            receita_total=("valor_total", "sum"),
            qtd_vendas=("venda_id", "count")
        )
        .reset_index()
        .sort_values("receita_total", ascending=False)
    )


def receita_por_estado(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega receita total e quantidade de vendas por estado."""
    return (
        df
        .groupby("estado")
        .agg(
            receita_total=("valor_total", "sum"),
            qtd_vendas=("venda_id", "count")
        )
        .reset_index()
        .sort_values("receita_total", ascending=False)
    )


# ─────────────────────────────────────────────
# CARREGAR
# ─────────────────────────────────────────────

def carregar_parquet(df: pd.DataFrame, caminho: str) -> None:
    """Salva DataFrame em Parquet, criando o diretório se necessário."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_parquet(caminho, index=False)
    print(f"Salvo: {caminho} ({len(df)} linhas)")


# ─────────────────────────────────────────────
# PONTO DE ENTRADA
# ─────────────────────────────────────────────

def main():
    caminho_db = "recursos/dados.db"

    # Extrair
    df_vendas = extrair_vendas(caminho_db)
    print(f"Vendas carregadas: {len(df_vendas)} registros")

    # Transformar
    df_categoria = receita_por_categoria(df_vendas)
    df_estado    = receita_por_estado(df_vendas)

    # Carregar
    carregar_parquet(df_categoria, "saida/receita_por_categoria.parquet")
    carregar_parquet(df_estado,    "saida/receita_por_estado.parquet")

    print("Pipeline concluído.")


if __name__ == "__main__":
    main()
```

### Por que `if __name__ == "__main__"`?

Esse bloco garante que o código de execução só roda quando o arquivo é chamado diretamente (`python pipeline_exemplo.py`), não quando é importado por outro módulo. É uma convenção importante para manter o código reutilizável.

### Conexão com o Módulo 5

A estrutura `extrair → transformar → carregar` que você pratica aqui é exatamente o esqueleto de um pipeline orquestrado. No Módulo 5, você aprenderá a agendar, monitorar e escalar esse mesmo padrão usando ferramentas de orquestração.
