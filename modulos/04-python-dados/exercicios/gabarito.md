# Módulo 4 — Gabarito

---

## Exercício 4.1 — Manipulação Básica com Pandas

### a) Carregar os dados de vendas

```python
import sqlite3
import pandas as pd

with sqlite3.connect('recursos/dados.db') as conn:
    df = pd.read_sql("""
        SELECT
            v.venda_id,
            v.data_venda,
            v.valor_total,
            c.nome        AS cliente_nome,
            p.nome        AS produto_nome,
            cat.nome      AS categoria
        FROM vendas v
        JOIN clientes   c   ON v.cliente_id   = c.cliente_id
        JOIN produtos   p   ON v.produto_id   = p.produto_id
        JOIN categorias cat ON p.categoria_id = cat.categoria_id
    """, conn)

print(f"Total de registros: {len(df)}")
print(df.head())
print(df.dtypes)
```

### b) Filtrar o primeiro trimestre de 2024

```python
df["data_venda"] = pd.to_datetime(df["data_venda"])

inicio = pd.Timestamp("2024-01-01")
fim    = pd.Timestamp("2024-03-31")

df_q1 = df[(df["data_venda"] >= inicio) & (df["data_venda"] <= fim)]

print(f"Vendas no Q1/2024: {len(df_q1)}")
```

### c) Receita total por categoria no primeiro trimestre

```python
receita_categoria = (
    df_q1
    .groupby("categoria")
    .agg(
        receita_total=("valor_total", "sum"),
        qtd_vendas=("venda_id", "count")
    )
    .reset_index()
    .sort_values("receita_total", ascending=False)
)

print(receita_categoria.to_string(index=False))
```

---

## Exercício 4.2 — Funções de Transformação

**Arquivo: `exercicios/funcoes.py`**

```python
import sqlite3
import pandas as pd


def top_clientes(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Retorna os N clientes com maior receita total."""
    return (
        df
        .groupby("cliente_nome")
        .agg(receita_total=("valor_total", "sum"))
        .reset_index()
        .sort_values("receita_total", ascending=False)
        .head(n)
    )


def vendas_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna receita e quantidade de vendas agrupadas por mês."""
    df = df.copy()
    df["periodo"] = pd.to_datetime(df["data_venda"]).dt.to_period("M").astype(str)
    return (
        df
        .groupby("periodo")
        .agg(
            receita_total=("valor_total", "sum"),
            qtd_vendas=("venda_id", "count")
        )
        .reset_index()
        .sort_values("periodo")
    )


def ticket_medio_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna o ticket médio (valor médio por venda) por categoria."""
    return (
        df
        .groupby("categoria")
        .agg(ticket_medio=("valor_total", "mean"))
        .reset_index()
        .sort_values("ticket_medio", ascending=False)
        .round({"ticket_medio": 2})
    )


if __name__ == "__main__":
    with sqlite3.connect("recursos/dados.db") as conn:
        df = pd.read_sql("""
            SELECT
                v.venda_id,
                v.data_venda,
                v.valor_total,
                c.nome    AS cliente_nome,
                cat.nome  AS categoria
            FROM vendas v
            JOIN clientes   c   ON v.cliente_id   = c.cliente_id
            JOIN produtos   p   ON v.produto_id   = p.produto_id
            JOIN categorias cat ON p.categoria_id = cat.categoria_id
        """, conn)

    print("=== Top 5 clientes ===")
    print(top_clientes(df, 5).to_string(index=False))

    print("\n=== Vendas por mês ===")
    print(vendas_por_mes(df).to_string(index=False))

    print("\n=== Ticket médio por categoria ===")
    print(ticket_medio_por_categoria(df).to_string(index=False))
```

---

## Exercício 4.3 — Script ETL Estruturado

**Arquivo: `exercicios/pipeline.py`**

```python
"""
pipeline.py
ETL: lê dados de vendas do banco SQLite, calcula receita por estado e por
categoria, e salva os resultados em arquivos Parquet.
"""

import os
import sqlite3
import pandas as pd


# ─────────────────────────────────────────────
# EXTRAIR
# ─────────────────────────────────────────────

def extrair_vendas(caminho_db: str) -> pd.DataFrame:
    """
    Lê todas as vendas do banco, enriquecidas com cliente, produto e categoria.

    Parâmetros
    ----------
    caminho_db : caminho relativo ou absoluto para o arquivo dados.db

    Retorna
    -------
    DataFrame com: venda_id, data_venda, valor_total, cliente_nome,
                   estado, produto_nome, categoria
    """
    query = """
        SELECT
            v.venda_id,
            v.data_venda,
            v.valor_total,
            c.nome    AS cliente_nome,
            c.estado,
            p.nome    AS produto_nome,
            cat.nome  AS categoria
        FROM vendas v
        JOIN clientes   c   ON v.cliente_id   = c.cliente_id
        JOIN produtos   p   ON v.produto_id   = p.produto_id
        JOIN categorias cat ON p.categoria_id = cat.categoria_id
    """
    with sqlite3.connect(caminho_db) as conn:
        return pd.read_sql(query, conn)


# ─────────────────────────────────────────────
# TRANSFORMAR
# ─────────────────────────────────────────────

def receita_por_estado(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega receita total e quantidade de vendas por estado.

    Nulos em valor_total são ignorados na soma (comportamento padrão do pandas).
    """
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


def receita_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega receita total e quantidade de vendas por categoria.

    Nulos em valor_total são ignorados na soma (comportamento padrão do pandas).
    """
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


# ─────────────────────────────────────────────
# CARREGAR
# ─────────────────────────────────────────────

def carregar_parquet(df: pd.DataFrame, caminho: str) -> None:
    """
    Salva DataFrame em Parquet.
    Cria o diretório de destino se ele não existir.
    """
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
    df_estado    = receita_por_estado(df_vendas)
    df_categoria = receita_por_categoria(df_vendas)

    # Carregar
    carregar_parquet(df_estado,    "saida/receita_por_estado.parquet")
    carregar_parquet(df_categoria, "saida/receita_por_categoria.parquet")

    print("Pipeline concluído.")


if __name__ == "__main__":
    main()
```

---

### Resposta à pergunta de reflexão (Ex 4.3)

**O que acontece se `valor_total` vier com valores nulos?**

Por padrão, `pandas` ignora `NaN` em operações de agregação como `sum` e `count`, então o pipeline não quebraria. No entanto, o resultado pode ser silenciosamente incorreto: vendas com `valor_total` nulo contribuem para a contagem (`qtd_vendas`) mas não para a receita, distorcendo métricas como ticket médio.

**Como tratar:**

```python
def extrair_vendas(caminho_db: str) -> pd.DataFrame:
    df = ...  # leitura do banco

    # Verificar e registrar nulos antes de descartar
    nulos = df["valor_total"].isnull().sum()
    if nulos > 0:
        print(f"Atenção: {nulos} vendas com valor_total nulo — registros descartados.")

    # Remover registros sem valor (não faz sentido somar zero implícito)
    df = df.dropna(subset=["valor_total"])

    return df
```

A decisão de descartar ou substituir por zero depende da regra de negócio: vendas canceladas (nulo = sem receita) vs. vendas em processamento (nulo = dado ainda não disponível). Documentar essa decisão no código é tão importante quanto implementá-la.
