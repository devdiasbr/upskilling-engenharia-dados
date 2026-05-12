# Conteúdo — Módulo 9: Troubleshooting em Engenharia de Dados

> **Premissa central:** todo problema tem causa raiz. Troubleshooting eficiente é a habilidade de ir da observação do sintoma à causa raiz sem dar passos em falso.

---

## Seção 1 — Metodologia: Os Quatro Passos

Independentemente do tipo de problema — pipeline quebrado, dado errado ou query lenta — a mesma sequência se aplica:

```
REPRODUZIR → ISOLAR → CORRIGIR → PREVENIR
```

### 1. Reproduzir

Antes de qualquer coisa, confirme que o problema é real e consistente.

- **Problema intermitente?** Execute o pipeline mais de uma vez. Problemas de concorrência, locks ou timeouts aparecem só sob carga.
- **Problema de ambiente?** Reproduza no mesmo ambiente onde ocorreu. "Funciona na minha máquina" não resolve o problema em produção.
- **Dados de entrada mudam?** Isole a run que falhou: qual foi o input exato?

Se você não consegue reproduzir o problema, você não pode ter certeza de que o corrigiu.

### 2. Isolar

Reduza o espaço do problema ao mínimo possível.

- **Bisection:** divida o pipeline ao meio. A primeira metade funciona? Então o problema está na segunda. Repita até isolar a tarefa específica.
- **Input mínimo:** qual é o menor dataset que reproduz o problema? Um pipeline que falha com 1 linha é mais fácil de debugar do que um com 1 milhão.
- **Hipóteses explícitas:** antes de mudar qualquer coisa, escreva sua hipótese. "Acredito que o problema está em X porque Y." Isso evita mudar várias coisas ao mesmo tempo e perder a causa real.

### 3. Corrigir

Corrija apenas o que foi isolado. Não aproveite para refatorar.

- Uma mudança por vez.
- Verifique que a correção resolve o problema reproduzível.
- Verifique que não quebra nada que funcionava.

### 4. Prevenir

Todo problema encontrado em produção é um teste que ainda não existia.

```python
# Antes: o bug existia e ninguém sabia
# Depois: escreva o teste que teria capturado o bug antes

def test_pipeline_nao_produz_duplicatas():
    resultado = transformar(df_com_duplicatas_na_entrada)
    assert resultado['venda_id'].is_unique
```

Se você corrige sem prevenir, o mesmo bug vai aparecer de novo.

---

## Seção 2 — Pilar 1: Pipelines Quebrados

### 2.1 Tipos de Falha

| Tipo | Sintoma | Risco |
|------|---------|-------|
| **Falha explícita** | Exception, exit code != 0, alerta disparado | Baixo — você sabe que falhou |
| **Falha silenciosa** | Pipeline termina "com sucesso", mas saída está errada | Alto — ninguém sabe até o cliente reclamar |
| **Falha intermitente** | Funciona em 9 de 10 execuções | Médio — difícil de reproduzir |
| **Degradação gradual** | Pipeline fica mais lento ou produz menos linhas a cada run | Alto — passa despercebido por semanas |

A falha mais perigosa é a silenciosa. Um pipeline que salva um Parquet com 0 linhas sem gerar alerta pode passar semanas sem ser detectado.

### 2.2 Leitura de Logs

Logs bem escritos contêm:
1. **Timestamp** — quando aconteceu
2. **Nível** (INFO, WARNING, ERROR, CRITICAL) — severidade
3. **Contexto** — qual tarefa, qual arquivo, quantas linhas processadas
4. **Mensagem** — o que aconteceu

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log"),
    ]
)
logger = logging.getLogger(__name__)

def extrair(caminho_db):
    logger.info(f"Iniciando extração de {caminho_db}")
    try:
        conn = sqlite3.connect(caminho_db)
        df = pd.read_sql("SELECT * FROM vendas", conn)
        logger.info(f"Extração concluída: {len(df)} linhas")
        return df
    except FileNotFoundError as e:
        logger.error(f"Banco não encontrado: {e}")
        raise
```

**Como ler um log de falha:**

1. Encontre a primeira linha de ERROR ou CRITICAL — essa é a causa raiz, não o sintoma.
2. Olhe o timestamp: o erro aconteceu no início, no meio ou no fim do pipeline?
3. Verifique o volume: o INFO antes do erro reportava o número esperado de linhas?

### 2.3 Checklist de Diagnóstico de Pipeline

```
□ O pipeline terminou com exit code 0?
□ O arquivo de saída foi criado?
□ O arquivo de saída tem o número esperado de linhas?
□ O log reporta volume em cada etapa?
□ Há WARNING de descarte de linhas?
□ O último checkpoint de sucesso foi quando?
□ O ambiente (banco, paths, dependências) está igual ao da última run bem-sucedida?
```

---

## Seção 3 — Pilar 2: Anomalias em Dados

### 3.1 As 5 Dimensões como Guia de Investigação

Do Módulo 8, as 5 dimensões agora funcionam como checklist de investigação:

```python
def investigar_dataset(df):
    problemas = []

    # 1. Completude
    nulos = df.isnull().sum()
    for col, n in nulos[nulos > 0].items():
        problemas.append(f"COMPLETUDE: {col} tem {n} nulos ({n/len(df)*100:.1f}%)")

    # 2. Unicidade
    duplicatas = df.duplicated().sum()
    if duplicatas > 0:
        problemas.append(f"UNICIDADE: {duplicatas} linhas duplicadas")

    # 3. Validade
    if 'quantidade' in df.columns:
        inv = (df['quantidade'] <= 0).sum()
        if inv > 0:
            problemas.append(f"VALIDADE: {inv} linhas com quantidade <= 0")

    if 'valor_total' in df.columns:
        inv = (df['valor_total'] < 0).sum()
        if inv > 0:
            problemas.append(f"VALIDADE: {inv} linhas com valor_total negativo")

    # 4. Consistência
    if 'produto_id' in df.columns:
        conn = sqlite3.connect("recursos/dados.db")
        produtos_validos = pd.read_sql("SELECT produto_id FROM produtos", conn)['produto_id']
        invalidos = ~df['produto_id'].isin(produtos_validos)
        if invalidos.sum() > 0:
            problemas.append(f"CONSISTÊNCIA: {invalidos.sum()} produto_ids inexistentes")

    # 5. Timeliness
    if 'data_venda' in df.columns:
        futuras = (pd.to_datetime(df['data_venda']) > pd.Timestamp.now()).sum()
        if futuras > 0:
            problemas.append(f"TIMELINESS: {futuras} datas no futuro")

    return problemas
```

### 3.2 Isolar a Origem da Anomalia

Quando você encontra um problema nos dados, a primeira pergunta é: **o problema veio da fonte ou foi introduzido pelo pipeline?**

```
Fonte (banco/API/arquivo) → Extração → Transformação → Carga → Destino
         ↑                      ↑              ↑            ↑
   Problema aqui?         Extração ok?   Transform ok?  Carga ok?
```

**Estratégia:** inspecione o dado em cada etapa, começando pela mais próxima da saída com problema e indo em direção à fonte.

```python
# Adicione pontos de inspeção no pipeline
def transformar(df_raw):
    logger.info(f"[transformar] entrada: {len(df_raw)} linhas")

    df = df_raw.dropna(subset=['cliente_id', 'valor_total'])
    logger.info(f"[transformar] após dropna: {len(df)} linhas (descartadas: {len(df_raw)-len(df)})")

    df = df[df['quantidade'] > 0]
    logger.info(f"[transformar] após filtro quantidade: {len(df)} linhas")

    return df
```

---

## Seção 4 — Pilar 3: Performance SQL

### 4.1 Identificar Queries Lentas

Antes de otimizar, meça:

```python
import time

t0 = time.time()
df = pd.read_sql(query, conn)
elapsed = time.time() - t0
print(f"Query executou em {elapsed:.3f}s, retornou {len(df)} linhas")
```

Uma query é "lenta" em contexto. 500ms para um dashboard interativo pode ser inaceitável. 30s para um relatório batch pode ser aceitável.

### 4.2 EXPLAIN QUERY PLAN no SQLite

```sql
EXPLAIN QUERY PLAN
SELECT c.nome, SUM(v.valor_total) AS receita
FROM vendas v
JOIN clientes c ON v.cliente_id = c.cliente_id
GROUP BY c.nome
ORDER BY receita DESC;
```

**O que procurar no plano:**

| Operação | Significado | Impacto |
|----------|-------------|---------|
| `SCAN tabela` | Varredura completa | Alto — lê todas as linhas |
| `SEARCH tabela USING INDEX` | Usa índice | Baixo — lê só o necessário |
| `USE TEMP B-TREE FOR ORDER BY` | Sort sem índice | Médio — materializa resultado |
| `CORRELATED SCALAR SUBQUERY` | Subquery executada por linha | Muito alto |

### 4.3 Padrões Comuns de Problema

**Subquery correlacionada (O(n²)):**
```sql
-- RUIM: subquery executa uma vez para cada linha de vendas
SELECT v.venda_id,
       v.valor_total,
       (SELECT AVG(valor_total) FROM vendas) AS media  -- recalcula n vezes
FROM vendas v
WHERE v.valor_total > (SELECT AVG(valor_total) FROM vendas);  -- recalcula n vezes

-- BOM: calcule uma vez, use em JOIN ou CTE
WITH media AS (SELECT AVG(valor_total) AS m FROM vendas)
SELECT v.venda_id, v.valor_total, m.m AS media
FROM vendas v, media
WHERE v.valor_total > m.m;
```

**SELECT * desnecessário:**
```sql
-- RUIM: lê e transfere todas as colunas
SELECT * FROM vendas WHERE data_venda >= '2024-01-01';

-- BOM: lê só o que vai usar
SELECT venda_id, cliente_id, valor_total, data_venda
FROM vendas
WHERE data_venda >= '2024-01-01';
```

**JOIN sem índice na coluna de join:**
```sql
-- Verificar se o índice existe
PRAGMA index_list('vendas');

-- Criar índice se não existir
CREATE INDEX IF NOT EXISTS idx_vendas_cliente ON vendas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_vendas_data    ON vendas(data_venda);
```

### 4.4 Fluxo de Otimização

```
1. Meça o tempo atual
2. Rode EXPLAIN QUERY PLAN
3. Identifique o SCAN mais custoso
4. Hipótese: "Se eu adicionar índice em X, o SCAN vai virar SEARCH"
5. Aplique uma mudança
6. Meça de novo
7. O ganho justifica a complexidade adicionada?
```

Nunca otimize sem medir antes e depois. Uma "otimização" que não tem número não é uma otimização.

---

## Seção 5 — Integrando os Três Pilares

Na prática, os três problemas aparecem juntos. Um incidente típico:

1. **Alerta dispara:** pipeline do dia falhou (pilar 1)
2. **Investigação:** o pipeline falhou porque recebeu dados com nulos inesperados (pilar 2)
3. **Raiz mais profunda:** a query que alimenta o pipeline ficou 10x mais lenta depois que a tabela de vendas cresceu, causando timeout (pilar 3)

A metodologia é sempre a mesma: reproduzir → isolar → corrigir → prevenir. O que muda é o domínio onde você aplica cada passo.

```
INCIDENTE
   │
   ├── Pipeline falhou? → Leia os logs, encontre a primeira linha de ERROR
   │                       ↓
   │                   Dado de entrada com problema? → Investigue as 5 dimensões
   │                       ↓
   │                   Query lenta causou timeout? → EXPLAIN QUERY PLAN
   │
   └── Após corrigir: escreva o teste que teria capturado isso
```
