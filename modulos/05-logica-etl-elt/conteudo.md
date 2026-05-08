# Módulo 5 — Lógica de ETL/ELT: Conteúdo

---

## Seção 1 — ETL vs ELT

### O que é ETL?

ETL significa **Extract, Transform, Load** — extrair os dados da fonte, transformá-los fora do destino e só então carregá-los já no formato final.

```
Fonte → [Extrair] → [Transformar] → [Carregar] → Destino
```

O processamento acontece **antes** da carga. O destino recebe apenas dados limpos e prontos para consumo.

### O que é ELT?

ELT significa **Extract, Load, Transform** — extrair os dados, carregá-los no destino em formato bruto (raw) e só então transformá-los usando a capacidade computacional do próprio destino.

```
Fonte → [Extrair] → [Carregar raw] → Destino → [Transformar no destino]
```

O processamento acontece **dentro** do destino. Ferramentas como dbt, Spark SQL ou stored procedures executam as transformações diretamente no data warehouse.

### Quando usar ETL

Use ETL quando:

- O destino tem capacidade computacional ou de armazenamento limitada e não pode receber dados brutos
- Os dados precisam ser **anonimizados ou mascarados antes de qualquer armazenamento** — o dado sensível nunca pode tocar o destino
- Você está integrando **sistemas legados** que não têm SQL moderno ou capacidade de transformação interna
- A transformação é simples e o volume de dados é pequeno
- O time de dados não tem acesso ao destino final para rodar transformações

### Quando usar ELT

Use ELT quando:

- O destino é um **cloud data warehouse moderno** — BigQuery, Snowflake, Databricks, Redshift
- O volume de dados é grande e o destino é mais eficiente para processar do que a máquina intermediária
- Você quer preservar o dado bruto para reprocessamento futuro — o raw serve como fonte de verdade
- O time usa ferramentas como **dbt** para transformação declarativa dentro do warehouse
- Você quer flexibilidade: diferentes times podem aplicar transformações diferentes sobre os mesmos dados brutos

### Tendência atual: ELT domina em cloud

Com a adoção massiva de cloud data warehouses a partir dos anos 2010, o ELT se tornou o padrão dominante em engenharia de dados moderna. As razões são práticas:

- BigQuery, Snowflake e Databricks têm capacidade de processamento elástica — é mais barato transformar lá do que em servidores intermediários
- O dado bruto preservado permite reprocessamento quando a lógica de negócio muda
- Ferramentas como dbt tornam as transformações SQL versionáveis, testáveis e documentadas

Na prática, muitas arquiteturas modernas são **híbridas**: fazem transformações mínimas antes da carga (limpeza básica, anonimização obrigatória) e deixam transformações analíticas para dentro do warehouse.

---

## Seção 2 — Estratégias de Extração

### Full Load (Carga Completa)

Full load extrai **todos os registros da fonte** a cada execução, sem considerar o que já foi processado anteriormente.

**Quando usar:**
- Tabelas pequenas com poucos registros
- Quando não existe coluna de controle (sem `updated_at`, sem `data_venda` confiável)
- Quando a simplicidade é prioritária e o custo de reprocessar tudo é aceitável
- Após erros graves que exigem reprocessamento total

**Quando evitar:**
- Tabelas com milhões de registros — ler tudo toda vez é ineficiente
- Quando a fonte tem limitações de taxa de requisições (APIs com rate limit)

**Exemplo — full load da tabela vendas:**

```python
import sqlite3
import pandas as pd


def extrair_full_load(caminho_db: str) -> pd.DataFrame:
    """Extrai todas as vendas do banco — full load."""
    query = """
        SELECT
            v.venda_id,
            v.cliente_id,
            v.produto_id,
            v.quantidade,
            v.data_venda,
            v.valor_total
        FROM vendas v
    """
    with sqlite3.connect(caminho_db) as conn:
        df = pd.read_sql(query, conn)
    print(f"Full load: {len(df)} registros extraídos")
    return df


df_vendas = extrair_full_load("recursos/dados.db")
```

### Extração Incremental

Extração incremental busca **apenas os registros novos ou alterados** desde a última execução. Requer uma coluna de controle — geralmente uma data de criação ou atualização.

**Vantagens:**
- Muito mais eficiente para grandes volumes
- Menor carga sobre a fonte
- Execuções mais rápidas

**Requisitos:**
- A tabela fonte precisa ter uma coluna de controle confiável (`data_venda`, `created_at`, `updated_at`)
- É preciso armazenar o ponto de controle da última execução bem-sucedida

**Exemplo — extração incremental por data_venda:**

```python
import sqlite3
import pandas as pd
from datetime import date


def extrair_incremental(conn: sqlite3.Connection, ultima_execucao: str) -> pd.DataFrame:
    """
    Extrai vendas com data_venda posterior à ultima_execucao.

    Parâmetros
    ----------
    conn             : conexão aberta com o banco SQLite
    ultima_execucao  : data no formato 'YYYY-MM-DD' — extrai registros após esta data

    Retorna
    -------
    DataFrame com as vendas novas
    """
    query = """
        SELECT
            venda_id,
            cliente_id,
            produto_id,
            quantidade,
            data_venda,
            valor_total
        FROM vendas
        WHERE data_venda > :ultima_execucao
        ORDER BY data_venda
    """
    df = pd.read_sql(query, conn, params={"ultima_execucao": ultima_execucao})
    print(f"Incremental: {len(df)} registros após {ultima_execucao}")
    return df
```

### Armazenando o ponto de controle

O ponto de controle (a data da última execução bem-sucedida) precisa ser persistido entre execuções. A solução mais simples é um arquivo de texto:

```python
import os
from datetime import date


ARQUIVO_CONTROLE = "saida/ultimo_processamento.txt"


def ler_ultimo_processamento() -> str:
    """Lê a data da última execução bem-sucedida. Retorna '2022-12-31' se não existir."""
    if os.path.exists(ARQUIVO_CONTROLE):
        with open(ARQUIVO_CONTROLE, "r") as f:
            return f.read().strip()
    return "2022-12-31"  # data anterior a todos os registros — força extração total


def salvar_ultimo_processamento(data: str) -> None:
    """Persiste a data de corte para a próxima execução."""
    os.makedirs(os.path.dirname(ARQUIVO_CONTROLE), exist_ok=True)
    with open(ARQUIVO_CONTROLE, "w") as f:
        f.write(data)
```

**Simulando duas execuções incrementais:**

```python
import sqlite3

caminho_db = "recursos/dados.db"

# Primeira execução — busca registros após 2023-06-30
with sqlite3.connect(caminho_db) as conn:
    df_1 = extrair_incremental(conn, "2023-06-30")
    data_max_1 = df_1["data_venda"].max()
    print(f"Primeira execução: {len(df_1)} registros, última data: {data_max_1}")

# Simula que salvamos o ponto de controle após a primeira execução bem-sucedida
salvar_ultimo_processamento(data_max_1)

# Segunda execução — busca apenas registros após a última data processada
ponto_controle = ler_ultimo_processamento()
with sqlite3.connect(caminho_db) as conn:
    df_2 = extrair_incremental(conn, ponto_controle)
    print(f"Segunda execução: {len(df_2)} registros (0 se já processamos tudo)")
```

**Importante:** só salve o ponto de controle **após** a execução ser concluída com sucesso. Se salvar antes e o pipeline falhar, você perderá registros nas próximas execuções.

---

## Seção 3 — Transformações Comuns

Transformações são o núcleo do processamento de dados. Uma transformação bem feita garante que os dados chegam ao destino com qualidade, consistência e no formato esperado.

### Remover duplicatas

Duplicatas surgem por falhas de integração, reprocessamentos parciais ou problemas na fonte.

```python
import pandas as pd
import sqlite3

with sqlite3.connect("recursos/dados.db") as conn:
    df = pd.read_sql("SELECT * FROM vendas", conn)

# Verificar antes
print(f"Antes: {len(df)} linhas")
print(f"Duplicatas em venda_id: {df['venda_id'].duplicated().sum()}")

# Remover duplicatas mantendo a primeira ocorrência
df = df.drop_duplicates(subset=["venda_id"], keep="first")

print(f"Depois: {len(df)} linhas")
```

Para tabelas sem chave primária explícita, `drop_duplicates()` sem parâmetros remove linhas completamente idênticas:

```python
df = df.drop_duplicates()
```

### Tratar nulos

Nulos exigem **decisão consciente** — não existe resposta automática. Substitua quando fizer sentido de negócio; descarte quando o registro sem aquele campo é inútil ou enganoso.

```python
# Verificar onde estão os nulos
print(df.isnull().sum())

# Substituir nulos por zero em campos numéricos (faz sentido em quantidade)
df["quantidade"] = df["quantidade"].fillna(0)

# Substituir por valor padrão em campos de texto
df["estado"] = df["estado"].fillna("Não informado")

# Remover linhas onde campos críticos estão nulos
# (uma venda sem cliente_id ou valor_total não pode ser processada)
linhas_antes = len(df)
df = df.dropna(subset=["cliente_id", "valor_total"])
descartadas = linhas_antes - len(df)
print(f"Linhas descartadas por nulos críticos: {descartadas}")
```

### Padronizar strings

Inconsistências de formatação são causas comuns de erros de join e análise:

```python
with sqlite3.connect("recursos/dados.db") as conn:
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)

# Remover espaços extras e padronizar capitalização
df_clientes["nome"] = df_clientes["nome"].str.strip().str.title()
df_clientes["cidade"] = df_clientes["cidade"].str.strip().str.title()
df_clientes["estado"] = df_clientes["estado"].str.strip().str.upper()

# Garantir que e-mails estejam em minúsculas
df_clientes["email"] = df_clientes["email"].str.strip().str.lower()
```

### Corrigir tipos de dados

Dados lidos de bancos ou arquivos frequentemente chegam com tipos incorretos:

```python
# data_venda pode chegar como string dependendo do driver
df["data_venda"] = pd.to_datetime(df["data_venda"])

# Extrair componentes da data para análise
df["ano"] = df["data_venda"].dt.year
df["mes"] = df["data_venda"].dt.month
df["dia_semana"] = df["data_venda"].dt.day_name()

# Garantir tipo numérico
df["valor_total"] = pd.to_numeric(df["valor_total"], errors="coerce")
```

O parâmetro `errors="coerce"` transforma valores que não podem ser convertidos em `NaN` — o que permite detectá-los depois, ao invés de o script quebrar com exceção.

### Enriquecer com dados de referência

Enriquecimento é adicionar contexto que não está na tabela original — via join com tabelas de referência:

```python
import sqlite3
import pandas as pd

with sqlite3.connect("recursos/dados.db") as conn:
    df_vendas = pd.read_sql("SELECT * FROM vendas", conn)
    df_produtos = pd.read_sql("SELECT produto_id, nome, categoria_id FROM produtos", conn)
    df_categorias = pd.read_sql("SELECT categoria_id, nome AS categoria FROM categorias", conn)

# Enriquecer vendas com nome do produto e categoria
df_enriquecido = (
    df_vendas
    .merge(df_produtos, on="produto_id", how="left")
    .merge(df_categorias, on="categoria_id", how="left")
)

# Calcular valor unitário (verificação de qualidade)
df_enriquecido["valor_unitario"] = (
    df_enriquecido["valor_total"] / df_enriquecido["quantidade"]
)

print(df_enriquecido[["venda_id", "nome", "categoria", "quantidade", "valor_total", "valor_unitario"]].head())
```

---

## Seção 4 — Estratégias de Carga

A estratégia de carga define **como** os dados chegam ao destino. A escolha errada cria duplicatas, perde dados ou torna o pipeline não-idempotente.

### Full Replace (Truncate and Load)

Apaga tudo no destino e recarrega do zero.

**Quando usar:**
- Tabelas pequenas onde reprocessar tudo é barato
- Quando a tabela destino é uma visão consolidada que precisa refletir exatamente o estado atual da fonte
- Quando idempotência simples é prioritária

**Quando evitar:**
- Tabelas grandes onde o custo de reprocessamento é alto
- Quando outros processos leem a tabela destino durante a carga (janela de indisponibilidade)

```python
import sqlite3
import pandas as pd

def carregar_full_replace(df: pd.DataFrame, caminho_db: str, tabela: str) -> None:
    """Apaga e recarrega a tabela destino completamente."""
    with sqlite3.connect(caminho_db) as conn:
        # if_exists="replace" faz truncate + insert automaticamente
        df.to_sql(tabela, conn, if_exists="replace", index=False)
    print(f"Full replace: {len(df)} linhas em '{tabela}'")
```

### Append (Inserção Simples)

Adiciona novos registros sem tocar nos existentes.

**Quando usar:**
- Combinado com extração incremental — você extrai só os novos e insere só os novos
- Tabelas de log ou histórico onde nunca há updates

**Quando evitar:**
- Sem garantia de que os registros são realmente novos — cria duplicatas facilmente

```python
def carregar_append(df: pd.DataFrame, caminho_db: str, tabela: str) -> None:
    """Adiciona registros à tabela sem verificar duplicatas."""
    with sqlite3.connect(caminho_db) as conn:
        df.to_sql(tabela, conn, if_exists="append", index=False)
    print(f"Append: {len(df)} linhas inseridas em '{tabela}'")
```

### Upsert (Insert ou Update)

Insere o registro se ele não existir; atualiza se já existir. É o padrão mais seguro para pipelines que podem ser reexecutados.

**Quando usar:**
- Sempre que você precisar de idempotência
- Quando registros podem ser atualizados na fonte após a primeira carga
- Como padrão geral em pipelines de produção

No SQLite, o upsert é implementado com `INSERT OR REPLACE`, que identifica conflitos pela chave primária:

```python
def carregar_upsert(df: pd.DataFrame, caminho_db: str) -> None:
    """
    Insere registros novos ou substitui existentes por venda_id.
    Garante idempotência: rodar duas vezes com os mesmos dados produz o mesmo resultado.
    """
    dados = df[["venda_id", "cliente_id", "produto_id", "valor_unitario"]].values.tolist()

    with sqlite3.connect(caminho_db) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vendas_processadas (
                venda_id     INTEGER PRIMARY KEY,
                cliente_id   INTEGER,
                produto_id   INTEGER,
                valor_unitario REAL
            )
        """)
        conn.executemany("""
            INSERT OR REPLACE INTO vendas_processadas
                (venda_id, cliente_id, produto_id, valor_unitario)
            VALUES (?, ?, ?, ?)
        """, dados)
    print(f"Upsert: {len(dados)} linhas processadas em 'vendas_processadas'")
```

**Alternativa com pandas e SQLAlchemy** para bancos que suportam `ON CONFLICT DO UPDATE` (PostgreSQL, SQLite 3.24+):

```python
# Em PostgreSQL com SQLAlchemy:
# INSERT INTO tabela VALUES (...) ON CONFLICT (id) DO UPDATE SET campo = EXCLUDED.campo
```

---

## Seção 5 — Idempotência

### O que é idempotência?

Uma operação é **idempotente** quando executá-la N vezes com os mesmos dados produz exatamente o mesmo resultado que executar uma vez.

Em pipelines de dados: se você rodar o pipeline hoje, ele produz o arquivo X. Se você rodar de novo amanhã com os mesmos dados de entrada, ele produz o mesmo arquivo X — não uma versão acumulada, não um arquivo diferente.

### Por que idempotência importa

Pipelines falham. Servidores reiniciam. Redes caem. Datas vencem. O pipeline que você escreve hoje **vai falhar em algum momento** — e quando isso acontecer, alguém (provavelmente você) vai precisar reprocessar.

Se o pipeline não é idempotente, reprocessar cria:
- Duplicatas nos dados
- Arquivos com versões misturadas
- Resultados diferentes dependendo de quantas vezes foi executado

### Anti-padrão vs padrão idempotente

**Anti-padrão — NÃO faça isso:**

```python
# Cada execução ADICIONA linhas ao arquivo
# Após 3 execuções: 3x os dados
def carregar_nao_idempotente(df, caminho):
    df_existente = pd.read_parquet(caminho)
    df_final = pd.concat([df_existente, df])  # acumula!
    df_final.to_parquet(caminho, index=False)
```

```python
# Cada execução insere sem verificar duplicatas
def carregar_nao_idempotente_db(df, conn, tabela):
    df.to_sql(tabela, conn, if_exists="append", index=False)  # duplicata a cada run!
```

**Padrão idempotente — faça assim:**

```python
# Sempre sobrescreve — o resultado é sempre o mesmo
def carregar_idempotente_parquet(df, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_parquet(caminho, index=False)  # sobrescreve o arquivo anterior
    print(f"Salvo (idempotente): {caminho}")
```

```python
# Upsert — inserir novos, substituir existentes
def carregar_idempotente_db(df, conn):
    conn.executemany("""
        INSERT OR REPLACE INTO tabela_destino (id, valor) VALUES (?, ?)
    """, df[["id", "valor"]].values.tolist())
```

### Estratégias para garantir idempotência

| Estratégia | Quando usar | Como funciona |
|---|---|---|
| **Full replace** | Tabelas pequenas, destino é arquivo | Apaga e recria do zero a cada execução |
| **Upsert** | Tabelas grandes, banco de dados | Insere se não existe, atualiza se existe |
| **Partição por data** | Dados particionados por dia/mês | Sobrescreve apenas a partição do dia processado |

**Exemplo de partição por data:**

```python
def carregar_por_partição(df: pd.DataFrame, data: str, diretorio_base: str) -> None:
    """
    Salva os dados de uma data específica sobrescrevendo apenas aquela partição.
    Executar duas vezes para a mesma data produz o mesmo resultado.
    """
    caminho = os.path.join(diretorio_base, f"data={data}", "dados.parquet")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_parquet(caminho, index=False)
    print(f"Partição salva: {caminho} ({len(df)} linhas)")
```

### Teste de idempotência

Sempre que escrever um pipeline, execute este teste mental:

> "Se eu rodar esse pipeline 3 vezes com os mesmos dados de entrada, o destino terá exatamente os mesmos dados que após a primeira execução?"

Se a resposta for não, o pipeline não é idempotente e precisa ser corrigido antes de ir para produção.

---

## Seção 6 — Tratamento de Erros e Logging

### Por que tratar erros explicitamente?

Pipelines silenciosos são os mais perigosos. Um pipeline que silencia erros (`except: pass`) pode:
- Salvar um arquivo vazio parecendo que funcionou
- Registrar 0 linhas processadas sem alertar ninguém
- Deixar o ponto de controle desatualizado, causando gaps de dados

**Regra:** capture erros para registrar contexto e tomar decisão — nunca para esconder.

### O que logar

Logs úteis respondem: "o que aconteceu, quando, com quantos dados, e por quê falhou?"

**Logue:**
- Início e fim de cada etapa com timestamp
- Volume de dados em cada etapa (linhas lidas, linhas após limpeza, linhas salvas)
- Parâmetros da execução (data de corte, caminho do arquivo, tabela de destino)
- Erros com mensagem completa e contexto (qual etapa falhou, com quais parâmetros)
- Alertas quando o comportamento está fora do esperado (ex: mais de 5% de linhas descartadas)

**Não logue:**
- Dados pessoais (nome, CPF, e-mail, endereço) — PII não deve aparecer em logs
- Senhas, tokens, credenciais
- Linhas completas de dados em volume — logs não são banco de dados

### Estrutura de logging com o módulo `logging`

```python
import logging
import sys

# Configuração básica — deve ficar no início do script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),          # imprime no terminal
        logging.FileHandler("saida/pipeline.log"),  # salva em arquivo
    ]
)

logger = logging.getLogger(__name__)
```

### Exemplo completo de pipeline com tratamento de erros e logging

```python
"""
pipeline_robusto.py
Pipeline ETL com logging estruturado e tratamento de erros.
Usa recursos/dados.db como fonte.
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime

import pandas as pd

# ── Configuração de logging ──────────────────────────────────────────────────

os.makedirs("saida", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("saida/pipeline.log"),
    ]
)
logger = logging.getLogger(__name__)


# ── Extrair ──────────────────────────────────────────────────────────────────

def extrair(caminho_db: str) -> pd.DataFrame:
    logger.info("EXTRAIR | inicio | fonte=%s", caminho_db)
    try:
        with sqlite3.connect(caminho_db) as conn:
            df = pd.read_sql("SELECT * FROM vendas", conn)
        logger.info("EXTRAIR | fim | linhas=%d", len(df))
        return df
    except Exception as e:
        logger.error("EXTRAIR | erro | %s", e)
        raise


# ── Transformar ──────────────────────────────────────────────────────────────

def transformar(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("TRANSFORMAR | inicio | linhas_entrada=%d", len(df))
    try:
        linhas_antes = len(df)

        df = df.drop_duplicates(subset=["venda_id"])
        df = df.dropna(subset=["cliente_id", "valor_total", "quantidade"])
        df["data_venda"] = pd.to_datetime(df["data_venda"])
        df["valor_unitario"] = df["valor_total"] / df["quantidade"]

        linhas_depois = len(df)
        descartadas = linhas_antes - linhas_depois
        pct_descartada = (descartadas / linhas_antes * 100) if linhas_antes > 0 else 0

        logger.info(
            "TRANSFORMAR | fim | linhas_saida=%d | descartadas=%d (%.1f%%)",
            linhas_depois, descartadas, pct_descartada
        )

        if pct_descartada > 5:
            logger.warning(
                "TRANSFORMAR | alerta | %.1f%% das linhas foram descartadas (limite: 5%%)",
                pct_descartada
            )

        return df
    except Exception as e:
        logger.error("TRANSFORMAR | erro | %s", e)
        raise


# ── Carregar ─────────────────────────────────────────────────────────────────

def carregar(df: pd.DataFrame, caminho: str) -> None:
    logger.info("CARREGAR | inicio | destino=%s", caminho)
    try:
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        df.to_parquet(caminho, index=False)
        logger.info("CARREGAR | fim | linhas=%d | destino=%s", len(df), caminho)
    except Exception as e:
        logger.error("CARREGAR | erro | destino=%s | %s", caminho, e)
        raise


# ── Pipeline principal ───────────────────────────────────────────────────────

def main():
    inicio = datetime.now()
    logger.info("PIPELINE | inicio | %s", inicio.isoformat())

    try:
        df = extrair("recursos/dados.db")
        df = transformar(df)
        carregar(df, "saida/vendas_processadas.parquet")

        duracao = (datetime.now() - inicio).total_seconds()
        logger.info("PIPELINE | concluido | duracao=%.1fs | linhas_salvas=%d", duracao, len(df))

    except Exception as e:
        duracao = (datetime.now() - inicio).total_seconds()
        logger.error("PIPELINE | falhou | duracao=%.1fs | erro=%s", duracao, e)
        sys.exit(1)  # sinaliza falha para o orquestrador


if __name__ == "__main__":
    main()
```

### Saída esperada nos logs

```
2024-03-15 10:00:00,123 | INFO | PIPELINE | inicio | 2024-03-15T10:00:00.123
2024-03-15 10:00:00,201 | INFO | EXTRAIR | inicio | fonte=recursos/dados.db
2024-03-15 10:00:00,389 | INFO | EXTRAIR | fim | linhas=3000
2024-03-15 10:00:00,391 | INFO | TRANSFORMAR | inicio | linhas_entrada=3000
2024-03-15 10:00:00,412 | INFO | TRANSFORMAR | fim | linhas_saida=2990 | descartadas=10 (0.3%)
2024-03-15 10:00:00,414 | INFO | CARREGAR | inicio | destino=saida/vendas_processadas.parquet
2024-03-15 10:00:00,431 | INFO | CARREGAR | fim | linhas=2990 | destino=saida/vendas_processadas.parquet
2024-03-15 10:00:00,432 | INFO | PIPELINE | concluido | duracao=0.3s | linhas_salvas=2990
```

Logs nesse formato são legíveis por humanos e também por ferramentas de monitoramento como Datadog, CloudWatch e Grafana Loki.
