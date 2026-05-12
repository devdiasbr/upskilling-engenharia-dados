# Gabarito — Módulo 9: Troubleshooting em Engenharia de Dados

---

## Gabarito 9.1 — Pipeline com Falha Silenciosa

### Parte A — Diagnóstico

O problema está na linha **(A)**:

```python
df = df[df['valor_total'] > 10000]
```

A intenção era filtrar vendas com valor positivo (> 0), mas o filtro usa `10000` como threshold. Como a maioria das vendas no dataset tem valor abaixo de R$ 10.000, praticamente todas as linhas são descartadas — e o pipeline termina sem erro porque gerar um Parquet vazio é tecnicamente válido.

O problema passa despercebido porque o `print("Pipeline concluído.")` **(B)** não reporta volume — diz apenas que terminou.

```python
def transformar(df):
    print(f"entrada: {len(df)}")           # 3000
    df = df[df['valor_total'] > 10000]
    print(f"após filtro valor: {len(df)}")  # ~0 ← aqui está o problema
    df = df.dropna(subset=['cliente_id'])
    print(f"após dropna: {len(df)}")
    ...
```

### Parte B — Correção

```python
import sqlite3
import logging
import pandas as pd
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("pipeline.log")],
)
logger = logging.getLogger(__name__)


def extrair(caminho_db):
    logger.info(f"Extraindo de {caminho_db}")
    conn = sqlite3.connect(caminho_db)
    df = pd.read_sql("SELECT * FROM vendas", conn)
    conn.close()
    logger.info(f"Extração: {len(df)} linhas")
    return df


def transformar(df):
    logger.info(f"Transformando: {len(df)} linhas de entrada")

    df = df[df['valor_total'] > 0]          # corrigido: > 0, não > 10000
    logger.info(f"Após filtro valor_total > 0: {len(df)} linhas")

    df = df.dropna(subset=['cliente_id'])
    logger.info(f"Após dropna cliente_id: {len(df)} linhas")

    df = df[df['quantidade'] > 0]
    logger.info(f"Após filtro quantidade > 0: {len(df)} linhas")

    df['valor_unitario'] = df['valor_total'] / df['quantidade']
    return df


def carregar(df, caminho_saida):
    if len(df) == 0:
        raise RuntimeError("Saída com 0 linhas — abortando carga para evitar sobrescrever dados válidos.")
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(caminho_saida, index=False)
    logger.info(f"Parquet salvo em {caminho_saida} com {len(df)} linhas")


if __name__ == "__main__":
    df_raw = extrair("recursos/dados.db")
    df_ok  = transformar(df_raw)
    carregar(df_ok, "saida/vendas_processadas.parquet")
```

### Parte C — Teste

```python
import pandas as pd
import pytest
from pipeline_corrigido import transformar

def make_df(**kwargs):
    defaults = {
        'venda_id':    [1, 2, 3],
        'cliente_id':  [10, 20, 30],
        'valor_total': [150.0, 899.50, 3200.0],
        'quantidade':  [1, 2, 1],
    }
    defaults.update(kwargs)
    return pd.DataFrame(defaults)

def test_transformar_nao_descarta_vendas_normais():
    df = make_df()
    resultado = transformar(df)
    assert len(resultado) == 3

def test_transformar_descarta_valor_zero():
    df = make_df(valor_total=[0.0, 50.0, 100.0])
    resultado = transformar(df)
    assert len(resultado) == 2

def test_transformar_descarta_quantidade_zero():
    df = make_df(quantidade=[0, 1, 2])
    resultado = transformar(df)
    assert len(resultado) == 2

def test_transformar_descarta_cliente_nulo():
    df = make_df(cliente_id=[None, 20, 30])
    resultado = transformar(df)
    assert len(resultado) == 2
```

---

## Gabarito 9.2 — Dataset com Anomalias

### Parte A — Identificação e Classificação

| # | Problema | Dimensão(ões) |
|---|----------|---------------|
| 1 | `venda_id=3` aparece duas vezes (linhas 3 e 4 idênticas) | Unicidade |
| 2 | `cliente_id` nulo na linha 2 | Completude |
| 3 | `quantidade=0` nas linhas 3 e 4 | Validade |
| 4 | `valor_total=0` nas linhas 3 e 4 | Validade |
| 5 | `produto_id=999` na linha 5 (não existe em `produtos`) | Consistência |
| 6 | `quantidade=-1` e `valor_total=-80` na linha 6 | Validade |
| 7 | `data_venda='2099-12-31'` na linha 5 | Timeliness |

### Parte B — Correção

```python
import sqlite3
import pandas as pd
from datetime import datetime

def limpar(df, conn):
    n_inicial = len(df)

    # Unicidade: remove duplicatas pelo venda_id
    df = df.drop_duplicates(subset=['venda_id'], keep='first')

    # Completude: remove nulos em cliente_id
    df = df.dropna(subset=['cliente_id'])

    # Validade: quantidade e valor_total devem ser positivos
    df = df[df['quantidade'] > 0]
    df = df[df['valor_total'] > 0]

    # Consistência: produto_id deve existir na tabela produtos
    produtos_validos = pd.read_sql("SELECT produto_id FROM produtos", conn)['produto_id']
    df = df[df['produto_id'].isin(produtos_validos)]

    # Timeliness: data_venda não pode ser futura
    df['data_venda'] = pd.to_datetime(df['data_venda'])
    df = df[df['data_venda'] <= pd.Timestamp.now()]

    print(f"Entrada: {n_inicial} linhas → Saída: {len(df)} linhas "
          f"(descartadas: {n_inicial - len(df)})")
    return df.reset_index(drop=True)


conn = sqlite3.connect("recursos/dados.db")
df_limpo = limpar(pd.DataFrame(dados_problematicos), conn)
# Entrada: 6 linhas → Saída: 1 linha (descartadas: 5)
# Apenas a linha 1 (venda_id=1) passa em todos os filtros
```

### Parte C — Validação de Volume

```python
def validar_volume_descartado(df_antes, df_depois, limite_pct=0.10):
    descartado = 1 - len(df_depois) / len(df_antes)
    if descartado > limite_pct:
        raise RuntimeError(
            f"Validação falhou: {descartado*100:.1f}% das linhas descartadas "
            f"(limite: {limite_pct*100:.0f}%)"
        )
    return True

# Com o dataset problemático (5 de 6 linhas descartadas = 83%), isso levantaria:
# RuntimeError: Validação falhou: 83.3% das linhas descartadas (limite: 10%)
```

---

## Gabarito 9.3 — Query Lenta

### Parte A — Diagnóstico

O `EXPLAIN QUERY PLAN` revela dois `SCAN` na tabela `vendas` — um para o JOIN e outro para cada subquery correlacionada.

As subqueries problemáticas:

```sql
-- Executa UMA VEZ para cada linha de vendas → O(n)
(SELECT AVG(valor_total) FROM vendas)

-- Executa UMA VEZ para cada linha de vendas com cliente diferente → O(n²) no pior caso
(SELECT AVG(valor_total) * COUNT(*) FROM vendas WHERE cliente_id = v.cliente_id)
```

Com 3.000 linhas a diferença é imperceptível. Com 10 milhões de linhas, a segunda subquery pode executar milhões de vezes.

### Parte B — Query Otimizada

```sql
-- Otimização: subqueries O(n²) → CTEs calculadas uma vez cada
-- Índices necessários: vendas(cliente_id), vendas(data_venda)

CREATE INDEX IF NOT EXISTS idx_vendas_cliente ON vendas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_vendas_data    ON vendas(data_venda);

WITH
media_geral AS (
    -- Calculada uma única vez, não por linha
    SELECT AVG(valor_total) AS m FROM vendas
),
media_por_cliente AS (
    -- Calculada uma vez por cliente, não por linha do outer query
    SELECT
        cliente_id,
        AVG(valor_total) AS media_pessoal,
        COUNT(*)         AS total_compras_historico
    FROM vendas
    GROUP BY cliente_id
),
vendas_filtradas AS (
    SELECT cliente_id, SUM(valor_total) AS receita_total, COUNT(*) AS total_compras
    FROM vendas
    WHERE data_venda >= '2024-01-01'
    GROUP BY cliente_id
)
SELECT
    c.nome,
    c.estado,
    vf.total_compras,
    vf.receita_total,
    mg.m                                              AS media_geral,
    vf.receita_total - mg.m * mpc.total_compras_historico AS desvio_da_media_pessoal
FROM vendas_filtradas vf
JOIN clientes         c   ON vf.cliente_id = c.cliente_id
JOIN media_por_cliente mpc ON vf.cliente_id = mpc.cliente_id
CROSS JOIN media_geral mg
ORDER BY vf.receita_total DESC
LIMIT 10;
```

**Speedup típico com os índices no dataset de 3.000 linhas:** 2–5x. Em datasets maiores (milhões de linhas), a diferença pode ser de minutos para segundos.
