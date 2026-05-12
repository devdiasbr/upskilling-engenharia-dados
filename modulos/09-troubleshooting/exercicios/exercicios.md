# Exercícios — Módulo 9: Troubleshooting em Engenharia de Dados

> Aplique sempre a metodologia: **reproduzir → isolar → corrigir → prevenir**.

---

## Exercício 9.1 — Pipeline com Falha Silenciosa

**Nível:** intermediário  
**Tempo estimado:** 45 min

O pipeline abaixo roda sem erros, mas o arquivo de saída está sempre vazio ou com poucas linhas. Ninguém percebeu por dois dias.

```python
import sqlite3
import pandas as pd
from pathlib import Path

def extrair(caminho_db):
    conn = sqlite3.connect(caminho_db)
    df = pd.read_sql("SELECT * FROM vendas", conn)
    conn.close()
    return df

def transformar(df):
    # Remove linhas com problema
    df = df[df['valor_total'] > 10000]          # (A)
    df = df.dropna(subset=['cliente_id'])
    df = df[df['quantidade'] == df['quantidade']]
    df['valor_unitario'] = df['valor_total'] / df['quantidade']
    return df

def carregar(df, caminho_saida):
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(caminho_saida, index=False)
    print("Pipeline concluído.")             # (B)

if __name__ == "__main__":
    df_raw  = extrair("recursos/dados.db")
    df_ok   = transformar(df_raw)
    carregar(df_ok, "saida/vendas_processadas.parquet")
```

### Parte A — Reproduzir e diagnosticar

1. Rode o pipeline. Quantas linhas tem o Parquet gerado?
2. Adicione um `print(len(df))` após cada etapa de `transformar` para ver onde as linhas desaparecem.
3. Qual linha de código é responsável pelo problema? Qual era a intenção do autor e o que o código realmente faz?

### Parte B — Corrigir

4. Corrija o filtro para que reflita a intenção real (manter vendas com valor positivo).
5. Substitua os `print` por `logging` com nível INFO em cada etapa, incluindo volume de entrada e saída.
6. Adicione uma verificação após a carga: se o Parquet tiver 0 linhas, levante um `RuntimeError`.

### Parte C — Prevenir

7. Escreva um teste pytest que detectaria esse bug antes do deploy:

```python
def test_transformar_nao_descarta_vendas_normais():
    df = pd.DataFrame({
        'venda_id':    [1, 2, 3],
        'cliente_id':  [10, 20, 30],
        'valor_total': [150.0, 899.50, 3200.0],
        'quantidade':  [1, 2, 1],
    })
    resultado = transformar(df)
    assert len(resultado) == 3  # todas as 3 linhas devem sobrar
```

---

## Exercício 9.2 — Dataset com Anomalias

**Nível:** intermediário  
**Tempo estimado:** 45 min

O arquivo abaixo representa uma extração real que chegou com problemas. Sua tarefa é identificar, classificar e corrigir cada anomalia.

```python
import pandas as pd
import sqlite3

# Dataset com problemas injetados
dados_problematicos = {
    'venda_id':    [1,    2,    3,    3,    5,    6   ],
    'cliente_id':  [10,   None, 30,   30,   50,   60  ],
    'produto_id':  [1,    2,    3,    3,    999,  2   ],
    'quantidade':  [2,    1,    0,    0,    1,    -1  ],
    'valor_total': [300., 50.,  0.,   0.,   99.,  -80.],
    'data_venda':  ['2024-01-10', '2024-02-15', '2024-03-01',
                    '2024-03-01', '2099-12-31', '2024-04-20'],
}
df = pd.DataFrame(dados_problematicos)
```

### Parte A — Identificar e classificar

1. Liste todos os problemas encontrados no dataset.
2. Para cada problema, classifique em qual(is) das 5 dimensões ele se enquadra:
   - Completude, Unicidade, Validade, Consistência, Timeliness

### Parte B — Corrigir

3. Implemente uma função `limpar(df, conn)` que:
   - Remove duplicatas (mantendo a primeira ocorrência)
   - Remove linhas com `cliente_id` nulo
   - Remove linhas com `quantidade <= 0`
   - Remove linhas com `valor_total <= 0`
   - Remove linhas com `produto_id` que não existe na tabela `produtos` do banco
   - Remove linhas com `data_venda` no futuro

4. Quantas linhas sobram após a limpeza?

### Parte C — Prevenir

5. Transforme a função `limpar` em validações que **levantam exceção** ao invés de silenciosamente descartar linhas — quando o percentual descartado superar 10%:

```python
def validar_volume_descartado(df_antes, df_depois, limite_pct=0.10):
    descartado = 1 - len(df_depois) / len(df_antes)
    if descartado > limite_pct:
        raise RuntimeError(
            f"Validação falhou: {descartado*100:.1f}% das linhas descartadas "
            f"(limite: {limite_pct*100:.0f}%)"
        )
```

---

## Exercício 9.3 — Query Lenta

**Nível:** avançado  
**Tempo estimado:** 45 min

A query abaixo funciona corretamente mas fica cada vez mais lenta conforme a tabela de vendas cresce. Analise e otimize.

```sql
SELECT
    c.nome,
    c.estado,
    COUNT(*) AS total_compras,
    SUM(v.valor_total) AS receita_total,
    (
        SELECT AVG(valor_total)
        FROM vendas
    ) AS media_geral,
    SUM(v.valor_total) - (
        SELECT AVG(valor_total) * COUNT(*)
        FROM vendas
        WHERE cliente_id = v.cliente_id
    ) AS desvio_da_media_pessoal
FROM vendas v
JOIN clientes c ON v.cliente_id = c.cliente_id
WHERE v.data_venda >= '2024-01-01'
GROUP BY c.cliente_id, c.nome, c.estado
ORDER BY receita_total DESC
LIMIT 10;
```

### Parte A — Diagnosticar

1. Execute `EXPLAIN QUERY PLAN` na query. Quais operações de `SCAN` aparecem?
2. Meça o tempo de execução com `time.time()`.
3. Identifique as subqueries problemáticas. Quantas vezes cada uma executa em relação ao número de linhas?

### Parte B — Otimizar

4. Reescreva a query usando CTEs para calcular a média geral e a média pessoal por cliente uma única vez.
5. Verifique se existem índices nas colunas `data_venda` e `cliente_id` de `vendas`:

```sql
PRAGMA index_list('vendas');
```

6. Se não existirem, crie-os e meça o tempo novamente. Qual foi o speedup?

### Parte C — Prevenir

7. Escreva um comentário no topo da query otimizada explicando:
   - Por que as subqueries originais eram O(n²)
   - Como as CTEs resolvem o problema
   - Quais índices são necessários para a performance esperada
