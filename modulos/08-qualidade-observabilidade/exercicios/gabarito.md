# Módulo 8 — Gabarito

---

## Gabarito 8.1 — Identificar Problemas de Qualidade

### Análise do DataFrame

```python
import pandas as pd

df = pd.DataFrame({
    "venda_id":   [101, 102, 103, 103, 104, 105, 106],
    "cliente_id": [10,  20,  30,  30,  None, 50,  60],
    "produto_id": [1,   2,   3,   3,   4,   999, 6],
    "quantidade": [2,   1,   3,   3,   0,   1,   2],
    "data_venda": ["2024-01-10", "2024-01-11", "2024-01-12",
                   "2024-01-12", "2024-01-13", "2024-01-14", "32-13-2024"],
    "valor_total": [100.0, 80.0, 150.0, 150.0, 60.0, 90.0, -40.0],
})

produtos_validos = {1, 2, 3, 4, 5, 6, 7, 8}
```

### Tabela de problemas

| # | Linha(s) afetada(s) | Descrição do problema | Dimensão violada | Como tratar |
|---|---|---|---|---|
| 1 | Linhas 2 e 3 (venda_id=103) | `venda_id` duplicado — mesma venda aparece duas vezes | **Unicidade** | `df.drop_duplicates(subset=["venda_id"], keep="first")` |
| 2 | Linha 4 (venda_id=104) | `cliente_id` é nulo — venda sem cliente identificado | **Completude** | `df.dropna(subset=["cliente_id"])` ou `ValidacaoError` se tolerância = 0% |
| 3 | Linha 5 (venda_id=105) | `produto_id = 999` não existe no catálogo | **Acurácia** | Validar contra tabela de referência: `df[~df["produto_id"].isin(produtos_validos)]` |
| 4 | Linha 4 (venda_id=104) | `quantidade = 0` — impossível calcular `valor_unitario` | **Consistência** | `df[df["quantidade"] > 0]` — descartar ou levantar `ValidacaoError` |
| 5 | Linha 6 (venda_id=106) | `valor_total = -40.0` — valor negativo não faz sentido de negócio | **Consistência** | Descartar ou corrigir (se for erro de sinal): `df[df["valor_total"] >= 0]` |
| 6 | Linha 6 (venda_id=106) | `data_venda = "32-13-2024"` — data com dia=32 e mês=13 é impossível | **Acurácia** | `pd.to_datetime(df["data_venda"], errors="coerce")` converte para NaT — depois `df.dropna(subset=["data_venda"])` |

### Respostas às perguntas de reflexão

**1. Qual problema é mais grave para faturamento?**

O `valor_total = -40.0` é provavelmente o mais grave para um pipeline de faturamento, pois um valor negativo somado à receita total vai subtrair incorretamente. O `cliente_id` nulo é grave para atribuição de receita por cliente. A duplicata de `venda_id=103` contaria a mesma venda duas vezes no total. Em produção, todos são críticos — mas o `valor_total` negativo afeta diretamente indicadores financeiros.

**2. O que `errors="coerce"` faz?**

`pd.to_datetime(df["data_venda"], errors="coerce")` transforma valores que não podem ser interpretados como datas em `NaT` (Not a Time) — o equivalente ao `NaN` para datas. Isso permite que o DataFrame continue existindo sem erros, mas os valores inválidos ficam como nulos que podem ser detectados depois.

Sozinho, não é suficiente como tratamento: é necessário também descartar ou tratar os `NaT` resultantes. `errors="coerce"` é a detecção; `dropna(subset=["data_venda"])` é o tratamento.

**3. Como detectar `produto_id = 999` automaticamente?**

```python
# Carregar IDs válidos da tabela de referência
with sqlite3.connect("recursos/dados.db") as conn:
    df_produtos = pd.read_sql("SELECT produto_id FROM produtos", conn)

ids_validos = set(df_produtos["produto_id"])

# Detectar referências inválidas
invalidos = df[~df["produto_id"].isin(ids_validos)]
if len(invalidos) > 0:
    raise ValidacaoError(
        f"{len(invalidos)} linha(s) com produto_id inválido: "
        f"{invalidos['produto_id'].unique().tolist()}"
    )
```

Isso é uma validação de **integridade referencial** — verificar que uma chave estrangeira aponta para um registro existente.

---

## Gabarito 8.2 — Validações em Pipeline

```python
import pandas as pd


class ValidacaoError(Exception):
    """Levantada quando os dados não atendem às expectativas de qualidade."""
    pass


def validar_dataframe(df: pd.DataFrame) -> None:
    """
    Valida um DataFrame de vendas.

    Verifica, nesta ordem:
    1. Schema (colunas obrigatórias presentes)
    2. Unicidade de venda_id
    3. Completude de cliente_id (sem nulos)
    4. Completude de produto_id (sem nulos)
    5. valor_total >= 0
    6. quantidade > 0

    Levanta ValidacaoError com mensagem descritiva se qualquer
    verificação falhar. Não modifica o DataFrame.
    """
    COLUNAS_OBRIGATORIAS = [
        "venda_id", "cliente_id", "produto_id",
        "quantidade", "data_venda", "valor_total"
    ]

    # 1. Schema
    ausentes = [col for col in COLUNAS_OBRIGATORIAS if col not in df.columns]
    if ausentes:
        raise ValidacaoError(
            f"Colunas obrigatórias ausentes: {ausentes}. "
            f"Colunas recebidas: {list(df.columns)}"
        )

    # 2. Unicidade de venda_id
    duplicatas = df.duplicated(subset=["venda_id"]).sum()
    if duplicatas > 0:
        raise ValidacaoError(
            f"{duplicatas} linha(s) com venda_id duplicado"
        )

    # 3. Completude de cliente_id
    nulos_cliente = df["cliente_id"].isnull().sum()
    if nulos_cliente > 0:
        raise ValidacaoError(
            f"cliente_id tem {nulos_cliente} valor(es) nulo(s) — tolerância: 0%"
        )

    # 4. Completude de produto_id
    nulos_produto = df["produto_id"].isnull().sum()
    if nulos_produto > 0:
        raise ValidacaoError(
            f"produto_id tem {nulos_produto} valor(es) nulo(s) — tolerância: 0%"
        )

    # 5. valor_total >= 0
    negativos = (df["valor_total"] < 0).sum()
    if negativos > 0:
        raise ValidacaoError(
            f"{negativos} linha(s) com valor_total negativo"
        )

    # 6. quantidade > 0
    invalidos = (df["quantidade"] <= 0).sum()
    if invalidos > 0:
        raise ValidacaoError(
            f"{invalidos} linha(s) com quantidade <= 0"
        )


# ── Testes manuais ───────────────────────────────────────────────────────────

df_valido = pd.DataFrame({
    "venda_id": [1, 2, 3],
    "cliente_id": [10, 20, 30],
    "produto_id": [100, 200, 300],
    "quantidade": [1, 2, 3],
    "data_venda": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "valor_total": [50.0, 100.0, 75.0],
})

# Caso 1 — DataFrame válido
try:
    validar_dataframe(df_valido)
    print("Caso 1 OK — nenhuma exceção levantada")
except ValidacaoError as e:
    print(f"FALHOU: {e}")

# Caso 2 — coluna ausente
df_sem_coluna = df_valido.drop(columns=["valor_total"])
try:
    validar_dataframe(df_sem_coluna)
    print("FALHOU — deveria ter levantado ValidacaoError")
except ValidacaoError as e:
    print(f"Caso 2 OK — {e}")

# Caso 3 — duplicata em venda_id
df_duplicata = pd.concat([df_valido, df_valido.iloc[[0]]], ignore_index=True)
try:
    validar_dataframe(df_duplicata)
    print("FALHOU — deveria ter levantado ValidacaoError")
except ValidacaoError as e:
    print(f"Caso 3 OK — {e}")

# Caso 4 — valor_total negativo
df_negativo = df_valido.copy()
df_negativo.loc[0, "valor_total"] = -10.0
try:
    validar_dataframe(df_negativo)
    print("FALHOU — deveria ter levantado ValidacaoError")
except ValidacaoError as e:
    print(f"Caso 4 OK — {e}")
```

**Saída esperada:**
```
Caso 1 OK — nenhuma exceção levantada
Caso 2 OK — Colunas obrigatórias ausentes: ['valor_total']. Colunas recebidas: [...]
Caso 3 OK — 1 linha(s) com venda_id duplicado
Caso 4 OK — 1 linha(s) com valor_total negativo
```

### Resposta à reflexão: coletar todos os erros vs. falhar no primeiro

Falhar no **primeiro erro** (como implementado acima) é mais simples e seguro para pipelines de produção: o dado está errado, pare agora, não gaste recursos processando o resto.

Coletar **todos os erros** de uma vez é útil quando o objetivo é **diagnóstico**: o engenheiro de dados quer saber tudo que está errado no dataset antes de começar a corrigir. Ferramentas como Great Expectations fazem isso — geram um relatório completo de todas as expectativas violadas em vez de parar no primeiro problema.

---

## Gabarito 8.3 — Testes Unitários com pytest

```python
# exercicios/test_pipeline.py
"""
Testes unitários e de integração para a função transformar do pipeline.

Executar:
    pytest exercicios/test_pipeline.py -v
"""

import os
import sqlite3
import tempfile

import pandas as pd
import pytest


# ── Função a ser testada (copiada do pipeline do Módulo 5) ───────────────────

def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma o DataFrame de vendas:
    - Remove duplicatas por venda_id
    - Descarta linhas com cliente_id, valor_total ou quantidade nulos
    - Descarta linhas com quantidade <= 0
    - Converte data_venda para datetime
    - Calcula valor_unitario = valor_total / quantidade
    """
    df = df.copy()
    df = df.drop_duplicates(subset=["venda_id"], keep="first")
    df = df.dropna(subset=["cliente_id", "valor_total", "quantidade"])
    df = df[df["quantidade"] > 0]
    df["data_venda"] = pd.to_datetime(df["data_venda"])
    df["valor_unitario"] = df["valor_total"] / df["quantidade"]
    return df.reset_index(drop=True)


# ── Função auxiliar para criar DataFrames de teste ───────────────────────────

def make_df(**kwargs) -> pd.DataFrame:
    """
    Cria um DataFrame de uma linha com valores padrão válidos.
    Use kwargs para sobrescrever qualquer campo.

    Exemplos:
        make_df()                              # linha padrão válida
        make_df(quantidade=[0])                # testa quantidade inválida
        make_df(venda_id=[1, 1])               # testa duplicata (2 linhas)
        make_df(valor_total=[None])            # testa nulo em valor_total
    """
    defaults = {
        "venda_id":   [1],
        "cliente_id": [10],
        "produto_id": [100],
        "quantidade": [2],
        "data_venda": ["2024-01-15"],
        "valor_total": [100.0],
    }
    defaults.update(kwargs)
    return pd.DataFrame(defaults)


# ── Testes unitários ─────────────────────────────────────────────────────────

def test_caso_feliz():
    """DataFrame válido passa sem erro; valor_unitario é calculado."""
    df = make_df()
    resultado = transformar(df)
    assert len(resultado) == 1
    assert "valor_unitario" in resultado.columns
    assert resultado["valor_unitario"].iloc[0] == pytest.approx(50.0)


def test_remove_duplicatas():
    """Duas linhas com mesmo venda_id resultam em uma linha."""
    df = pd.DataFrame({
        "venda_id":   [1, 1],
        "cliente_id": [10, 10],
        "produto_id": [100, 100],
        "quantidade": [2, 2],
        "data_venda": ["2024-01-15", "2024-01-15"],
        "valor_total": [100.0, 100.0],
    })
    resultado = transformar(df)
    assert len(resultado) == 1, "Duplicatas devem ser removidas"
    assert resultado["venda_id"].iloc[0] == 1


def test_descarta_valor_total_nulo():
    """Linha com valor_total=None é descartada."""
    df = pd.DataFrame({
        "venda_id":   [1, 2],
        "cliente_id": [10, 20],
        "produto_id": [100, 200],
        "quantidade": [2, 1],
        "data_venda": ["2024-01-15", "2024-01-16"],
        "valor_total": [100.0, None],
    })
    resultado = transformar(df)
    assert len(resultado) == 1, "Linha com valor_total nulo deve ser descartada"
    assert resultado["venda_id"].iloc[0] == 1


def test_descarta_quantidade_zero():
    """Linha com quantidade=0 é descartada (evita divisão por zero)."""
    df = make_df(quantidade=[0])
    resultado = transformar(df)
    assert len(resultado) == 0, "Linha com quantidade=0 deve ser descartada"


def test_valor_unitario_correto():
    """valor_unitario = valor_total / quantidade com precisão de ponto flutuante."""
    df = make_df(quantidade=[4], valor_total=[200.0])
    resultado = transformar(df)
    assert resultado["valor_unitario"].iloc[0] == pytest.approx(50.0)


def test_valor_unitario_nao_inteiro():
    """valor_unitario correto quando o resultado não é inteiro."""
    df = make_df(quantidade=[3], valor_total=[100.0])
    resultado = transformar(df)
    assert resultado["valor_unitario"].iloc[0] == pytest.approx(100.0 / 3)


def test_data_venda_convertida_para_datetime():
    """data_venda deve ser convertida para tipo datetime após transformação."""
    df = make_df(data_venda=["2024-01-15"])
    resultado = transformar(df)
    assert pd.api.types.is_datetime64_any_dtype(resultado["data_venda"])


def test_descarta_cliente_id_nulo():
    """Linha com cliente_id=None é descartada."""
    df = make_df(cliente_id=[None])
    resultado = transformar(df)
    assert len(resultado) == 0, "Linha com cliente_id nulo deve ser descartada"


def test_multiplas_linhas_validas_preservadas():
    """Múltiplas linhas válidas são todas preservadas."""
    df = pd.DataFrame({
        "venda_id":   [1, 2, 3],
        "cliente_id": [10, 20, 30],
        "produto_id": [100, 200, 300],
        "quantidade": [1, 2, 3],
        "data_venda": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "valor_total": [50.0, 100.0, 75.0],
    })
    resultado = transformar(df)
    assert len(resultado) == 3


# ── Teste de integração ───────────────────────────────────────────────────────

def test_integracao_com_banco_temporario():
    """
    Testa extração + transformação com banco SQLite temporário.
    Verifica que o pipeline descarrega a duplicata e calcula valor_unitario.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_db = os.path.join(tmpdir, "test.db")

        # Criar banco com dados conhecidos (inclui uma duplicata)
        with sqlite3.connect(caminho_db) as conn:
            conn.execute("""
                CREATE TABLE vendas (
                    venda_id    INTEGER,
                    cliente_id  INTEGER,
                    produto_id  INTEGER,
                    quantidade  INTEGER,
                    data_venda  TEXT,
                    valor_total REAL
                )
            """)
            conn.executemany(
                "INSERT INTO vendas VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (1, 10, 100, 2, "2024-01-15", 100.0),
                    (2, 20, 200, 1, "2024-01-16",  80.0),
                    (1, 10, 100, 2, "2024-01-15", 100.0),  # duplicata de venda_id=1
                ]
            )

        # Extrair do banco temporário
        with sqlite3.connect(caminho_db) as conn:
            df_raw = pd.read_sql("SELECT * FROM vendas", conn)

        # Transformar
        df_resultado = transformar(df_raw)

        # Verificar resultado
        assert len(df_resultado) == 2, "Pipeline deve descartar a duplicata"
        assert "valor_unitario" in df_resultado.columns
        venda_1 = df_resultado[df_resultado["venda_id"] == 1].iloc[0]
        assert venda_1["valor_unitario"] == pytest.approx(50.0)
```

---

## Gabarito 8.4 — Pipeline com Qualidade Integrada

```python
# exercicios/pipeline_qualidade.py
"""
Pipeline ETL com validação, logging estruturado e alerta de qualidade.
Módulo 8 — Qualidade e Observabilidade.

Uso:
    python exercicios/pipeline_qualidade.py
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


# ── Erro de validação ────────────────────────────────────────────────────────

class ValidacaoError(Exception):
    """Levantada quando os dados não atendem às expectativas de qualidade."""
    pass


# ── Validação ────────────────────────────────────────────────────────────────

COLUNAS_OBRIGATORIAS = [
    "venda_id", "cliente_id", "produto_id",
    "quantidade", "data_venda", "valor_total"
]


def validar_dataframe(df: pd.DataFrame) -> None:
    """
    Valida o DataFrame de vendas antes da transformação.
    Levanta ValidacaoError com mensagem descritiva se qualquer verificação falhar.
    """
    # 1. Schema
    ausentes = [col for col in COLUNAS_OBRIGATORIAS if col not in df.columns]
    if ausentes:
        raise ValidacaoError(
            f"Colunas obrigatórias ausentes: {ausentes}. "
            f"Colunas recebidas: {list(df.columns)}"
        )

    # 2. Unicidade de venda_id
    duplicatas = df.duplicated(subset=["venda_id"]).sum()
    if duplicatas > 0:
        raise ValidacaoError(f"{duplicatas} linha(s) com venda_id duplicado")

    # 3. Completude de cliente_id e produto_id
    for coluna in ["cliente_id", "produto_id"]:
        nulos = df[coluna].isnull().sum()
        if nulos > 0:
            raise ValidacaoError(
                f"{coluna} tem {nulos} valor(es) nulo(s) — tolerância: 0%"
            )

    # 4. Valores válidos
    negativos = (df["valor_total"] < 0).sum()
    if negativos > 0:
        raise ValidacaoError(f"{negativos} linha(s) com valor_total negativo")

    invalidos_qtd = (df["quantidade"] <= 0).sum()
    if invalidos_qtd > 0:
        raise ValidacaoError(f"{invalidos_qtd} linha(s) com quantidade <= 0")


# ── Extração ─────────────────────────────────────────────────────────────────

def extrair(caminho_db: str) -> pd.DataFrame:
    """Extrai todas as vendas do banco SQLite."""
    logger.info("EXTRAIR | inicio | fonte=%s", caminho_db)
    try:
        with sqlite3.connect(caminho_db) as conn:
            df = pd.read_sql("SELECT * FROM vendas", conn)
        logger.info("EXTRAIR | fim | linhas=%d", len(df))
        return df
    except Exception as e:
        logger.error("EXTRAIR | erro | %s", e)
        raise


# ── Transformação ─────────────────────────────────────────────────────────────

def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica limpeza e cálculos ao DataFrame de vendas."""
    logger.info("TRANSFORMAR | inicio | linhas_entrada=%d", len(df))
    try:
        df = df.copy()
        df = df.drop_duplicates(subset=["venda_id"], keep="first")
        df = df.dropna(subset=["cliente_id", "valor_total", "quantidade"])
        df = df[df["quantidade"] > 0]
        df["data_venda"] = pd.to_datetime(df["data_venda"])
        df["valor_unitario"] = df["valor_total"] / df["quantidade"]
        logger.info("TRANSFORMAR | fim | linhas_saida=%d", len(df))
        return df.reset_index(drop=True)
    except Exception as e:
        logger.error("TRANSFORMAR | erro | %s", e)
        raise


# ── Carga ─────────────────────────────────────────────────────────────────────

def carregar(df: pd.DataFrame, caminho: str) -> None:
    """Salva o DataFrame em Parquet (sobrescreve o arquivo anterior)."""
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
    CAMINHO_DB = "recursos/dados.db"
    CAMINHO_SAIDA = "saida/vendas_processadas.parquet"
    LIMITE_DESCARTE = 0.05  # 5%

    inicio = datetime.now()
    logger.info("PIPELINE | inicio | %s", inicio.isoformat())

    try:
        # Extração
        df_raw = extrair(CAMINHO_DB)
        linhas_extraidas = len(df_raw)

        # Validação — falha rápida antes de qualquer transformação
        try:
            validar_dataframe(df_raw)
            logger.info(
                "VALIDACAO | ok | %d linhas passaram em todas as verificações",
                linhas_extraidas
            )
        except ValidacaoError as e:
            logger.error("VALIDACAO | falhou | %s", e)
            sys.exit(1)  # não processa dado ruim

        # Transformação
        df_limpo = transformar(df_raw)
        linhas_salvas = len(df_limpo)

        # Alerta de descarte
        descartadas = linhas_extraidas - linhas_salvas
        pct_descarte = (descartadas / linhas_extraidas) if linhas_extraidas > 0 else 0

        if pct_descarte > LIMITE_DESCARTE:
            logger.warning(
                "QUALIDADE | alerta | %.1f%% das linhas foram descartadas "
                "(limite: %.0f%%) — verifique a qualidade dos dados de entrada",
                pct_descarte * 100,
                LIMITE_DESCARTE * 100,
            )

        # Carga
        carregar(df_limpo, CAMINHO_SAIDA)

        # Resumo final
        duracao = (datetime.now() - inicio).total_seconds()
        logger.info(
            "PIPELINE | concluido | duracao=%.1fs | linhas_salvas=%d",
            duracao, linhas_salvas
        )

        print("\n=== RESUMO DA EXECUÇÃO ===")
        print(f"Linhas extraídas:      {linhas_extraidas}")
        print(f"Linhas após validação: {linhas_extraidas}  (passou em todas as verificações)")
        print(f"Linhas após limpeza:   {linhas_salvas}")
        print(f"Linhas salvas:         {linhas_salvas}")
        print(f"Descartadas:           {descartadas} ({pct_descarte:.1%})")
        print(f"Duração:               {duracao:.1f}s")
        print(f"Status:                SUCESSO")

    except SystemExit:
        raise  # propaga sys.exit sem logar como erro genérico

    except Exception as e:
        duracao = (datetime.now() - inicio).total_seconds()
        logger.error(
            "PIPELINE | falhou | duracao=%.1fs | erro=%s",
            duracao, e
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Saída esperada (execução com dados.db)

```
2024-03-15 10:00:00,123 | INFO | PIPELINE | inicio | 2024-03-15T10:00:00.123
2024-03-15 10:00:00,201 | INFO | EXTRAIR | inicio | fonte=recursos/dados.db
2024-03-15 10:00:00,389 | INFO | EXTRAIR | fim | linhas=3000
2024-03-15 10:00:00,391 | INFO | VALIDACAO | ok | 3000 linhas passaram em todas as verificações
2024-03-15 10:00:00,392 | INFO | TRANSFORMAR | inicio | linhas_entrada=3000
2024-03-15 10:00:00,410 | INFO | TRANSFORMAR | fim | linhas_saida=2990
2024-03-15 10:00:00,411 | INFO | CARREGAR | inicio | destino=saida/vendas_processadas.parquet
2024-03-15 10:00:00,428 | INFO | CARREGAR | fim | linhas=2990 | destino=saida/vendas_processadas.parquet
2024-03-15 10:00:00,429 | INFO | PIPELINE | concluido | duracao=0.3s | linhas_salvas=2990

=== RESUMO DA EXECUÇÃO ===
Linhas extraídas:      3000
Linhas após validação: 3000  (passou em todas as verificações)
Linhas após limpeza:   2990
Linhas salvas:         2990
Descartadas:           10 (0.3%)
Duração:               0.3s
Status:                SUCESSO
```

### Saída esperada (banco inexistente)

```
2024-03-15 10:00:00,201 | INFO | EXTRAIR | inicio | fonte=recursos/nao_existe.db
2024-03-15 10:00:00,203 | ERROR | EXTRAIR | erro | unable to open database file
2024-03-15 10:00:00,204 | ERROR | PIPELINE | falhou | duracao=0.0s | erro=unable to open database file
```

O script termina com código de saída 1. O arquivo `saida/vendas_processadas.parquet` não é criado (ou não é sobrescrito se já existia).
