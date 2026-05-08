# Módulo 5 — Gabarito

---

## Exercício 5.1 — ETL vs ELT: Classificação de Cenários

### Cenário A — Snowflake com logs de acesso

**Resposta: ELT**

O Snowflake tem capacidade computacional elástica e foi projetado exatamente para transformar grandes volumes internamente. Carregar os ~50 GB/dia em formato bruto (raw) e transformar dentro do Snowflake com SQL ou dbt é mais eficiente e barato do que usar uma máquina intermediária para processar esse volume. Além disso, preservar o dado bruto permite recalcular métricas se a lógica de negócio mudar.

### Cenário B — Sistema legado hospitalar com dados sensíveis

**Resposta: ETL**

Este é o caso mais claro de obrigatoriedade do ETL: a LGPD exige que CPF e nome nunca toquem o destino em formato identificável. A anonimização precisa acontecer **antes** da carga — no pipeline intermediário — eliminando PII na origem. ELT aqui seria inaceitável porque o dado sensível seria armazenado no data warehouse antes de qualquer transformação, violando a exigência legal.

### Cenário C — Startup com BigQuery

**Resposta: ELT**

Para uma startup com time pequeno e baixo volume, ELT com BigQuery é a escolha natural: simplicidade de implementação (extrair do PostgreSQL, carregar no BigQuery, transformar com SQL ou dbt), custo baixo para o volume de dados, e o BigQuery já oferece toda a capacidade necessária para os cálculos de receita por categoria. ETL adicionaria complexidade desnecessária sem benefício claro.

---

## Exercício 5.2 — Extração Incremental

### Parte A — A função de extração

```python
import sqlite3
import pandas as pd


def extrair_incremental(conn: sqlite3.Connection, ultima_execucao: str) -> pd.DataFrame:
    """
    Extrai vendas com data_venda posterior à ultima_execucao.

    Parâmetros
    ----------
    conn             : conexão aberta com o banco SQLite
    ultima_execucao  : data no formato 'YYYY-MM-DD'

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


# Teste
caminho_db = "recursos/dados.db"

with sqlite3.connect(caminho_db) as conn:
    df_1 = extrair_incremental(conn, "2023-06-30")
    print(f"Execução 1: {len(df_1)} registros")
    print(f"Período: {df_1['data_venda'].min()} a {df_1['data_venda'].max()}")
```

**Saída esperada:**
```
Incremental: 1875 registros após 2023-06-30
Execução 1: 1875 registros
Período: 2023-07-01 a 2024-12-31
```

(O número exato depende da distribuição de dados gerada pelo `setup_db.py` com seed 42.)

### Parte B — Simulando duas execuções

```python
import sqlite3
import os
import pandas as pd


ARQUIVO_CONTROLE = "saida/ultimo_processamento.txt"


def ler_ultimo_processamento() -> str:
    """Lê a data da última execução bem-sucedida."""
    if os.path.exists(ARQUIVO_CONTROLE):
        with open(ARQUIVO_CONTROLE, "r") as f:
            return f.read().strip()
    return "2022-12-31"  # anterior a todos os registros


def salvar_ultimo_processamento(data: str) -> None:
    """Persiste o ponto de controle para a próxima execução."""
    os.makedirs(os.path.dirname(ARQUIVO_CONTROLE), exist_ok=True)
    with open(ARQUIVO_CONTROLE, "w") as f:
        f.write(data)


def extrair_incremental(conn: sqlite3.Connection, ultima_execucao: str) -> pd.DataFrame:
    query = """
        SELECT venda_id, cliente_id, produto_id, quantidade, data_venda, valor_total
        FROM vendas
        WHERE data_venda > :ultima_execucao
        ORDER BY data_venda
    """
    return pd.read_sql(query, conn, params={"ultima_execucao": ultima_execucao})


caminho_db = "recursos/dados.db"

# ── Primeira execução ────────────────────────────────────────────────────────
print("=== PRIMEIRA EXECUÇÃO ===")
ponto_1 = "2023-09-30"

with sqlite3.connect(caminho_db) as conn:
    df_1 = extrair_incremental(conn, ponto_1)

data_max_1 = df_1["data_venda"].max()
print(f"Registros encontrados: {len(df_1)}")
print(f"Período: {df_1['data_venda'].min()} a {data_max_1}")

# Só salvamos APÓS a execução bem-sucedida
salvar_ultimo_processamento(data_max_1)
print(f"Ponto de controle salvo: {data_max_1}")

# ── Segunda execução ─────────────────────────────────────────────────────────
print("\n=== SEGUNDA EXECUÇÃO ===")
ponto_2 = ler_ultimo_processamento()
print(f"Ponto de controle lido: {ponto_2}")

with sqlite3.connect(caminho_db) as conn:
    df_2 = extrair_incremental(conn, ponto_2)

print(f"Registros encontrados: {len(df_2)}")

# ── Verificação de sobreposição ──────────────────────────────────────────────
ids_1 = set(df_1["venda_id"])
ids_2 = set(df_2["venda_id"])
sobreposicao = ids_1 & ids_2

print(f"\n=== VERIFICAÇÃO ===")
print(f"IDs em execução 1: {len(ids_1)}")
print(f"IDs em execução 2: {len(ids_2)}")
print(f"IDs em ambas (sobreposição): {len(sobreposicao)}")
assert len(sobreposicao) == 0, "ERRO: há registros duplicados entre execuções!"
print("OK: nenhuma sobreposição de registros")
```

### Respostas às perguntas de reflexão

**O que acontece se o pipeline falhar após a extração mas antes de salvar o ponto de controle?**
Na próxima execução, o ponto de controle não foi atualizado, então o pipeline reprocessa os mesmos registros da execução anterior. Se o pipeline for idempotente (upsert), isso é seguro — os registros são inseridos/atualizados corretamente sem duplicata.

**O que acontece se o pipeline falhar após salvar o ponto de controle mas antes de concluir a carga?**
Na próxima execução, o ponto de controle já avançou, então os registros que foram extraídos mas não carregados serão **pulados para sempre** — criando um gap de dados. Esta situação é mais perigosa.

**Qual das duas é mais problemática?**
A segunda. Perder registros silenciosamente é mais grave do que reprocessar registros já processados. Por isso, sempre salve o ponto de controle somente após confirmar que a carga foi bem-sucedida.

---

## Exercício 5.3 e 5.4 — Pipeline Idempotente com Logging

O script abaixo resolve os dois exercícios. Salve como `exercicios/etl_idempotente.py`.

```python
"""
etl_idempotente.py

Pipeline ETL completo:
- Extrai vendas do banco recursos/dados.db
- Limpa, corrige tipos e calcula valor_unitario
- Salva em saida/vendas_processadas.parquet (idempotente: sobrescreve a cada execução)
- Logging estruturado para terminal e arquivo
- Tratamento de erros explícito com contexto
- Resumo de execução com alerta de qualidade

Uso:
    python exercicios/etl_idempotente.py

Para testar tratamento de erro, altere CAMINHO_DB para um caminho inválido.
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime

import pandas as pd


# ── Configuração ─────────────────────────────────────────────────────────────

CAMINHO_DB = "recursos/dados.db"
CAMINHO_SAIDA = "saida/vendas_processadas.parquet"
LIMITE_DESCARTE_PCT = 5.0  # alerta se mais de 5% das linhas forem descartadas

os.makedirs("saida", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("saida/pipeline.log"),
    ],
)
logger = logging.getLogger(__name__)


# ── Extrair ───────────────────────────────────────────────────────────────────

def extrair(caminho_db: str) -> pd.DataFrame:
    """
    Lê todas as vendas do banco SQLite.

    Parâmetros
    ----------
    caminho_db : caminho para o arquivo dados.db

    Retorna
    -------
    DataFrame com todas as colunas da tabela vendas
    """
    logger.info("EXTRAIR | inicio | fonte=%s", caminho_db)
    try:
        with sqlite3.connect(caminho_db) as conn:
            df = pd.read_sql("SELECT * FROM vendas", conn)
        logger.info("EXTRAIR | fim | linhas=%d", len(df))
        return df
    except Exception as e:
        logger.error("EXTRAIR | erro | fonte=%s | %s", caminho_db, e)
        raise


# ── Transformar ───────────────────────────────────────────────────────────────

def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica limpeza e enriquecimento:
    - Remove duplicatas por venda_id
    - Remove linhas com campos críticos nulos
    - Remove linhas com quantidade <= 0 (não é possível calcular valor_unitario)
    - Converte data_venda para datetime
    - Calcula valor_unitario = valor_total / quantidade

    Parâmetros
    ----------
    df : DataFrame bruto das vendas

    Retorna
    -------
    DataFrame limpo e enriquecido
    """
    logger.info("TRANSFORMAR | inicio | linhas_entrada=%d", len(df))
    try:
        df = df.copy()
        linhas_antes = len(df)

        # Remover duplicatas por chave primária
        df = df.drop_duplicates(subset=["venda_id"], keep="first")
        logger.info(
            "TRANSFORMAR | drop_duplicates | removidas=%d",
            linhas_antes - len(df)
        )

        # Remover linhas com campos críticos nulos
        df = df.dropna(subset=["cliente_id", "produto_id", "valor_total", "quantidade"])

        # Remover linhas com quantidade inválida (zero ou negativa)
        df = df[df["quantidade"] > 0]

        # Corrigir tipo de data
        df["data_venda"] = pd.to_datetime(df["data_venda"])

        # Enriquecer com valor unitário
        df["valor_unitario"] = df["valor_total"] / df["quantidade"]

        linhas_depois = len(df)
        descartadas = linhas_antes - linhas_depois
        pct_descartada = (descartadas / linhas_antes * 100) if linhas_antes > 0 else 0.0

        logger.info(
            "TRANSFORMAR | fim | linhas_saida=%d | descartadas=%d (%.1f%%)",
            linhas_depois,
            descartadas,
            pct_descartada,
        )

        if pct_descartada > LIMITE_DESCARTE_PCT:
            logger.warning(
                "TRANSFORMAR | alerta | %.1f%% das linhas foram descartadas "
                "(limite: %.0f%%) — verifique a qualidade dos dados de entrada",
                pct_descartada,
                LIMITE_DESCARTE_PCT,
            )

        return df

    except Exception as e:
        logger.error("TRANSFORMAR | erro | %s", e)
        raise


# ── Carregar ──────────────────────────────────────────────────────────────────

def carregar(df: pd.DataFrame, caminho: str) -> None:
    """
    Salva o DataFrame em Parquet, sobrescrevendo o arquivo anterior.
    Idempotente: executar N vezes com os mesmos dados produz o mesmo arquivo.

    Parâmetros
    ----------
    df      : DataFrame transformado
    caminho : caminho de destino do arquivo Parquet
    """
    logger.info("CARREGAR | inicio | destino=%s", caminho)
    try:
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        df.to_parquet(caminho, index=False)
        logger.info("CARREGAR | fim | linhas=%d | destino=%s", len(df), caminho)
    except Exception as e:
        logger.error("CARREGAR | erro | destino=%s | %s", caminho, e)
        raise


# ── Pipeline principal ────────────────────────────────────────────────────────

def main():
    inicio = datetime.now()
    logger.info("PIPELINE | inicio | %s", inicio.isoformat())

    try:
        # Executar etapas
        df_bruto = extrair(CAMINHO_DB)
        df_limpo = transformar(df_bruto)
        carregar(df_limpo, CAMINHO_SAIDA)

        # Resumo de execução
        linhas_lidas = len(df_bruto)
        linhas_salvas = len(df_limpo)
        descartadas = linhas_lidas - linhas_salvas
        pct_descartada = (descartadas / linhas_lidas * 100) if linhas_lidas > 0 else 0.0
        duracao = (datetime.now() - inicio).total_seconds()

        logger.info(
            "PIPELINE | concluido | duracao=%.1fs | lidas=%d | salvas=%d",
            duracao,
            linhas_lidas,
            linhas_salvas,
        )

        print("\n=== RESUMO DA EXECUÇÃO ===")
        print(f"Linhas lidas:          {linhas_lidas}")
        print(f"Linhas após limpeza:   {linhas_salvas}")
        print(f"Linhas salvas:         {linhas_salvas}")
        print(f"Linhas descartadas:    {descartadas} ({pct_descartada:.1f}%)")
        print(f"Duração:               {duracao:.1f}s")
        print("==========================\n")

        # Verificação de idempotência — lê o arquivo salvo e confirma contagem
        df_verificacao = pd.read_parquet(CAMINHO_SAIDA)
        assert len(df_verificacao) == linhas_salvas, (
            f"ERRO: arquivo tem {len(df_verificacao)} linhas, esperava {linhas_salvas}"
        )
        print(f"Verificação: arquivo contém {len(df_verificacao)} linhas (correto)")

    except Exception as e:
        duracao = (datetime.now() - inicio).total_seconds()
        logger.error("PIPELINE | falhou | duracao=%.1fs | erro=%s", duracao, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Como executar

```bash
# A partir do diretório raiz do projeto (Upskilling/)
python modulos/05-logica-etl-elt/exercicios/etl_idempotente.py
```

### Saída esperada (3 execuções consecutivas)

Todas as três execuções devem produzir o mesmo resumo:

```
2024-03-15 10:00:00,100 | INFO | PIPELINE | inicio | 2024-03-15T10:00:00.100
2024-03-15 10:00:00,102 | INFO | EXTRAIR | inicio | fonte=recursos/dados.db
2024-03-15 10:00:00,290 | INFO | EXTRAIR | fim | linhas=3000
2024-03-15 10:00:00,292 | INFO | TRANSFORMAR | inicio | linhas_entrada=3000
2024-03-15 10:00:00,295 | INFO | TRANSFORMAR | drop_duplicates | removidas=0
2024-03-15 10:00:00,310 | INFO | TRANSFORMAR | fim | linhas_saida=3000 | descartadas=0 (0.0%)
2024-03-15 10:00:00,312 | INFO | CARREGAR | inicio | destino=saida/vendas_processadas.parquet
2024-03-15 10:00:00,328 | INFO | CARREGAR | fim | linhas=3000 | destino=saida/vendas_processadas.parquet
2024-03-15 10:00:00,330 | INFO | PIPELINE | concluido | duracao=0.2s | lidas=3000 | salvas=3000

=== RESUMO DA EXECUÇÃO ===
Linhas lidas:          3000
Linhas após limpeza:   3000
Linhas salvas:         3000
Linhas descartadas:    0 (0.0%)
Duração:               0.2s
==========================

Verificação: arquivo contém 3000 linhas (correto)
```

O arquivo `saida/vendas_processadas.parquet` tem exatamente o mesmo conteúdo após cada execução — o pipeline é idempotente.

### Testando o tratamento de erro

```python
# Altere CAMINHO_DB para um caminho inválido:
CAMINHO_DB = "recursos/dados_inexistente.db"
```

Saída esperada:

```
2024-03-15 10:01:00,001 | INFO | PIPELINE | inicio | 2024-03-15T10:01:00.001
2024-03-15 10:01:00,002 | INFO | EXTRAIR | inicio | fonte=recursos/dados_inexistente.db
2024-03-15 10:01:00,004 | ERROR | EXTRAIR | erro | fonte=recursos/dados_inexistente.db | no such table: vendas
2024-03-15 10:01:00,005 | ERROR | PIPELINE | falhou | duracao=0.0s | erro=no such table: vendas
```

O script termina com código de saída 1. O arquivo `saida/vendas_processadas.parquet` não é sobrescrito — os dados anteriores estão intactos.
