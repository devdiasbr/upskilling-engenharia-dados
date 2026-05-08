# Módulo 8 — Qualidade e Observabilidade: Conteúdo

---

## Seção 1 — Dimensões de Qualidade de Dados

Qualidade de dados não é um conceito abstrato. É a resposta objetiva a perguntas concretas: "esses dados estão completos?", "esses dados fazem sentido?", "esses dados chegaram a tempo?". O framework de dimensões organiza essas perguntas em categorias, tornando mais fácil identificar exatamente o que está errado — e o que precisa ser validado.

As cinco dimensões abaixo cobrem a maioria dos problemas que aparecem em pipelines reais de e-commerce.

| Dimensão | Pergunta central | Exemplo de problema em e-commerce |
|---|---|---|
| **Completude** | Os campos obrigatórios estão preenchidos? | `cliente_id` nulo em 15% das vendas — impossível atribuir receita ao cliente |
| **Consistência** | Os dados fazem sentido em conjunto e seguem as regras de negócio? | `valor_total` = R$ 150 mas `quantidade` = 3 e preço unitário = R$ 80 — os números não fecham |
| **Acurácia** | Os valores refletem a realidade? | `estado` = "XX" — sigla inexistente, provavelmente erro de digitação |
| **Timeliness** | Os dados chegaram dentro do prazo esperado? | Pipeline de vendas do dia deveria rodar às 06h; às 10h ainda não há dados do dia anterior |
| **Unicidade** | Cada entidade aparece exatamente uma vez? | `venda_id` 4821 aparece três vezes — provavelmente reprocessamento sem tratamento de duplicatas |

### Por que usar esse framework?

Quando um dado está errado, a primeira pergunta é "qual tipo de erro é esse?". A dimensão indica a causa provável e a solução adequada:

- Problema de **completude** → validação de nulos antes da carga
- Problema de **consistência** → regras de negócio nas transformações
- Problema de **acurácia** → validação contra tabelas de referência
- Problema de **timeliness** → monitoramento de freshness com alertas de SLA
- Problema de **unicidade** → deduplicação por chave primária

Sem esse vocabulário, equipes passam horas debatendo "o dado está errado" sem conseguir articular exatamente o que está errado — o que torna a correção mais lenta e mais propensa a erros.

---

## Seção 2 — Validações em Pipeline

Validação é o ato de verificar, programaticamente, que os dados atendem às expectativas antes de qualquer transformação ou carga. Uma validação que falha deve interromper o pipeline com uma mensagem clara — não silenciar o problema e continuar.

### A classe de erro personalizada

```python
class ValidacaoError(Exception):
    """Levantada quando os dados não atendem às expectativas de qualidade."""
    pass
```

Criar uma exception própria (em vez de usar `ValueError` genérico) permite que o código chamador trate erros de validação de forma específica:

```python
try:
    validar_dataframe(df)
except ValidacaoError as e:
    logger.error("Validação falhou: %s", e)
    sys.exit(1)
except Exception as e:
    logger.error("Erro inesperado: %s", e)
    raise
```

### Validar schema

Verifica que as colunas obrigatórias existem no DataFrame. Se o pipeline receber um arquivo com colunas renomeadas ou ausentes, a transformação vai falhar em algum ponto obscuro — melhor falhar cedo com uma mensagem clara.

```python
def validar_schema(df: pd.DataFrame, colunas_obrigatorias: list[str]) -> None:
    """
    Verifica que todas as colunas obrigatórias estão presentes.

    Levanta ValidacaoError se alguma coluna estiver ausente.
    """
    ausentes = [col for col in colunas_obrigatorias if col not in df.columns]
    if ausentes:
        raise ValidacaoError(
            f"Colunas obrigatórias ausentes: {ausentes}. "
            f"Colunas recebidas: {list(df.columns)}"
        )
```

### Validar completude

Verifica que a proporção de nulos em cada coluna está dentro do limite tolerável. Uma coluna com 40% de nulos pode ser aceitável para um campo opcional; para `cliente_id`, qualquer nulo é um problema.

```python
def validar_completude(
    df: pd.DataFrame,
    colunas: list[str],
    tolerancia: float = 0.0
) -> None:
    """
    Verifica que a proporção de nulos em cada coluna não excede a tolerância.

    Parâmetros
    ----------
    df          : DataFrame a validar
    colunas     : colunas a verificar
    tolerancia  : proporção máxima de nulos permitida (0.0 = nenhum nulo aceito)
    """
    for coluna in colunas:
        if coluna not in df.columns:
            continue
        pct_nulos = df[coluna].isnull().mean()
        if pct_nulos > tolerancia:
            raise ValidacaoError(
                f"Coluna '{coluna}' tem {pct_nulos:.1%} de nulos "
                f"(limite: {tolerancia:.1%})"
            )
```

### Validar unicidade

Verifica que não há duplicatas na chave primária. Duplicatas de `venda_id` significam que a mesma venda seria processada múltiplas vezes.

```python
def validar_unicidade(df: pd.DataFrame, chave: list[str]) -> None:
    """
    Verifica que não existem duplicatas na chave informada.

    Parâmetros
    ----------
    df    : DataFrame a validar
    chave : lista de colunas que formam a chave (ex: ["venda_id"])
    """
    duplicatas = df.duplicated(subset=chave).sum()
    if duplicatas > 0:
        raise ValidacaoError(
            f"{duplicatas} linha(s) duplicada(s) encontrada(s) na chave {chave}"
        )
```

### Validar valores

Verifica regras de negócio que nenhum schema consegue capturar automaticamente: valores negativos, quantidades zero, referências inválidas.

```python
def validar_valores(df: pd.DataFrame) -> None:
    """
    Verifica regras de negócio sobre os valores das colunas.

    Validações aplicadas:
    - valor_total não pode ser negativo
    - quantidade deve ser maior que zero (divisão por zero em valor_unitario)
    """
    if "valor_total" in df.columns:
        negativos = (df["valor_total"] < 0).sum()
        if negativos > 0:
            raise ValidacaoError(
                f"{negativos} linha(s) com valor_total negativo"
            )

    if "quantidade" in df.columns:
        invalidos = (df["quantidade"] <= 0).sum()
        if invalidos > 0:
            raise ValidacaoError(
                f"{invalidos} linha(s) com quantidade <= 0 "
                "(causaria divisão por zero no cálculo de valor_unitario)"
            )
```

### Integrando validações no pipeline do Módulo 5

As validações devem ser executadas **antes** de qualquer transformação — não depois. Se o dado está ruim, não faz sentido transformá-lo.

```python
COLUNAS_OBRIGATORIAS = [
    "venda_id", "cliente_id", "produto_id",
    "quantidade", "data_venda", "valor_total"
]


def pipeline(caminho_db: str, caminho_saida: str) -> None:
    """Pipeline ETL com validações integradas."""
    # 1. Extração
    df = extrair(caminho_db)

    # 2. Validação — interrompe se os dados não atendem às expectativas
    try:
        validar_schema(df, COLUNAS_OBRIGATORIAS)
        validar_unicidade(df, ["venda_id"])
        validar_completude(df, ["cliente_id", "produto_id"], tolerancia=0.0)
        validar_valores(df)
        logger.info("VALIDACAO | ok | %d linhas validadas", len(df))
    except ValidacaoError as e:
        logger.error("VALIDACAO | falhou | %s", e)
        raise

    # 3. Transformação — só chega aqui se a validação passou
    df = transformar(df)

    # 4. Carga
    carregar(df, caminho_saida)
```

A validação acontece no nível de entrada de dados — antes do dado "contaminar" o destino. Isso é chamado de **fail fast**: falhar cedo, com contexto claro, é sempre melhor do que descobrir o problema horas depois em uma análise de BI.

---

## Seção 3 — Testes de Pipeline

Validações protegem contra dados ruins em produção. Testes protegem contra **código errado** em desenvolvimento. São duas camadas complementares de qualidade.

### Teste unitário

Um teste unitário testa **uma função isolada** com uma entrada conhecida e verifica que a saída é exatamente a esperada. Não usa banco de dados real, não lê arquivos do disco — toda a entrada é criada na própria função de teste.

```python
# test_pipeline.py
import pandas as pd
import pytest
from pipeline import transformar


def make_df(**kwargs) -> pd.DataFrame:
    """
    Cria um DataFrame mínimo para testes com valores padrão sensatos.
    Aceita kwargs para sobrescrever qualquer coluna.

    Uso:
        make_df()                          # linha padrão
        make_df(valor_total=None)          # testa nulo em valor_total
        make_df(quantidade=0)              # testa quantidade inválida
    """
    defaults = {
        "venda_id": [1],
        "cliente_id": [10],
        "produto_id": [100],
        "quantidade": [2],
        "data_venda": ["2024-01-15"],
        "valor_total": [100.0],
    }
    defaults.update(kwargs)
    return pd.DataFrame(defaults)
```

### Casos de teste para `transformar`

```python
def test_pipeline_caso_feliz():
    """Dado válido passa pela transformação sem erros."""
    df = make_df()
    resultado = transformar(df)
    assert len(resultado) == 1
    assert "valor_unitario" in resultado.columns
    assert resultado["valor_unitario"].iloc[0] == 50.0


def test_pipeline_remove_duplicatas():
    """Linhas com venda_id duplicado são reduzidas a uma."""
    df = pd.DataFrame({
        "venda_id": [1, 1],        # mesma venda duas vezes
        "cliente_id": [10, 10],
        "produto_id": [100, 100],
        "quantidade": [2, 2],
        "data_venda": ["2024-01-15", "2024-01-15"],
        "valor_total": [100.0, 100.0],
    })
    resultado = transformar(df)
    assert len(resultado) == 1, "Duplicatas devem ser removidas"


def test_pipeline_preenche_nulos():
    """Linhas com campos críticos nulos são descartadas."""
    df = pd.DataFrame({
        "venda_id": [1, 2],
        "cliente_id": [10, 10],
        "produto_id": [100, 100],
        "quantidade": [2, 2],
        "data_venda": ["2024-01-15", "2024-01-15"],
        "valor_total": [100.0, None],   # linha 2 tem valor_total nulo
    })
    resultado = transformar(df)
    assert len(resultado) == 1, "Linha com valor_total nulo deve ser descartada"
    assert resultado["venda_id"].iloc[0] == 1


def test_valor_unitario_calculado_corretamente():
    """valor_unitario deve ser valor_total / quantidade."""
    df = make_df(quantidade=[4], valor_total=[200.0])
    resultado = transformar(df)
    assert resultado["valor_unitario"].iloc[0] == pytest.approx(50.0)


def test_pipeline_quantidade_zero_descartada():
    """Linhas com quantidade nula ou zero são descartadas (evita divisão por zero)."""
    df = make_df(quantidade=[0])
    resultado = transformar(df)
    assert len(resultado) == 0, "Linha com quantidade=0 deve ser descartada"
```

### Teste de integração

Um teste de integração testa o **pipeline de ponta a ponta**: extração, transformação e carga, usando um banco de dados ou arquivo real (ou uma versão de teste deles).

```python
import sqlite3
import tempfile
import os


def test_pipeline_integracao_completa():
    """
    Testa o pipeline do início ao fim com um banco de dados temporário.
    Verifica que o arquivo de saída existe e tem o número correto de linhas.
    """
    # Arrange — criar banco temporário com dados conhecidos
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_db = os.path.join(tmpdir, "test.db")
        caminho_saida = os.path.join(tmpdir, "saida.parquet")

        with sqlite3.connect(caminho_db) as conn:
            conn.execute("""
                CREATE TABLE vendas (
                    venda_id INTEGER, cliente_id INTEGER,
                    produto_id INTEGER, quantidade INTEGER,
                    data_venda TEXT, valor_total REAL
                )
            """)
            conn.executemany(
                "INSERT INTO vendas VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (1, 10, 100, 2, "2024-01-15", 100.0),
                    (2, 20, 200, 1, "2024-01-16", 80.0),
                    (1, 10, 100, 2, "2024-01-15", 100.0),  # duplicata de venda_id=1
                ]
            )

        # Act — rodar o pipeline
        pipeline(caminho_db, caminho_saida)

        # Assert — verificar resultado
        import pandas as pd
        df_resultado = pd.read_parquet(caminho_saida)
        assert len(df_resultado) == 2, "Pipeline deve descartar a duplicata"
        assert "valor_unitario" in df_resultado.columns
```

### Executando os testes

```bash
# Instalar pytest (uma vez)
pip install pytest

# Rodar todos os testes
pytest test_pipeline.py -v

# Rodar um teste específico
pytest test_pipeline.py::test_pipeline_remove_duplicatas -v
```

A flag `-v` (verbose) mostra o nome de cada teste e se passou ou falhou, tornando mais fácil identificar exatamente o que quebrou.

---

## Seção 4 — Logging Estruturado

### Por que logging importa

Quando um pipeline falha em produção às 3h da manhã, você não está lá para observar. O log é a única evidência do que aconteceu — é a diferença entre "o pipeline falhou, não sei por quê" e "o pipeline falhou porque 23% das linhas tinham `cliente_id` nulo, o que excedeu o limite de 0%".

Logs também servem para:
- **Reproduzir problemas**: "na execução de terça-feira, quantas linhas foram processadas?"
- **Auditar comportamento**: "quando foi a última vez que o alerta de qualidade disparou?"
- **Medir performance**: "quanto tempo cada etapa levou?"

### O que logar

| O que logar | Exemplo de mensagem |
|---|---|
| Início de etapa com parâmetros | `EXTRAIR \| inicio \| fonte=recursos/dados.db` |
| Fim de etapa com volume | `EXTRAIR \| fim \| linhas=3000` |
| Erros com contexto completo | `TRANSFORMAR \| erro \| etapa=drop_duplicates \| mensagem=...` |
| Alertas de qualidade | `TRANSFORMAR \| alerta \| 8.2% das linhas descartadas (limite: 5%)` |
| Duração total e resultado | `PIPELINE \| concluido \| duracao=0.4s \| linhas_salvas=2990` |

### O que NÃO logar

| O que NÃO logar | Por quê |
|---|---|
| Dados pessoais (nome, CPF, e-mail) | PII em logs é uma violação de LGPD/GDPR — logs são armazenados por meses em sistemas de terceiros |
| Tokens e credenciais de API | Logs são frequentemente enviados para sistemas de observabilidade; expor credenciais é um risco de segurança grave |
| Senhas de banco de dados | Mesmo princípio — logs não são um destino seguro para segredos |
| Linhas completas de dados em volume | Logs não são banco de dados; registrar cada linha processada cria arquivos enormes e inúteis |

### Configuração de logging com o módulo padrão Python

```python
import logging
import os
import sys

os.makedirs("saida", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),          # imprime no terminal
        logging.FileHandler("saida/pipeline.log"),  # persiste em arquivo
    ]
)

logger = logging.getLogger(__name__)
```

O formato `%(asctime)s | %(levelname)s | %(message)s` produz mensagens como:

```
2024-03-15 10:00:00,389 | INFO | EXTRAIR | fim | linhas=3000
2024-03-15 10:00:00,412 | WARNING | TRANSFORMAR | alerta | 8.2% das linhas descartadas
2024-03-15 10:00:00,415 | ERROR | CARREGAR | erro | destino=saida/vendas.parquet | [Errno 2] No such file
```

Esse formato é legível por humanos e também por ferramentas como Datadog, CloudWatch e Grafana Loki — o que permite criar dashboards e alertas sem nenhuma mudança no código do pipeline.

### Logging em cada etapa do pipeline

```python
def extrair(caminho_db: str) -> pd.DataFrame:
    logger.info("EXTRAIR | inicio | fonte=%s", caminho_db)
    try:
        with sqlite3.connect(caminho_db) as conn:
            df = pd.read_sql("SELECT * FROM vendas", conn)
        logger.info("EXTRAIR | fim | linhas=%d", len(df))
        return df
    except Exception as e:
        logger.error("EXTRAIR | erro | %s", e)
        raise  # nunca silencia — o erro precisa propagar


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("TRANSFORMAR | inicio | linhas_entrada=%d", len(df))
    linhas_antes = len(df)

    df = df.drop_duplicates(subset=["venda_id"])
    df = df.dropna(subset=["cliente_id", "valor_total", "quantidade"])
    df = df[df["quantidade"] > 0]
    df["data_venda"] = pd.to_datetime(df["data_venda"])
    df["valor_unitario"] = df["valor_total"] / df["quantidade"]

    descartadas = linhas_antes - len(df)
    pct = (descartadas / linhas_antes * 100) if linhas_antes > 0 else 0

    logger.info(
        "TRANSFORMAR | fim | linhas_saida=%d | descartadas=%d (%.1f%%)",
        len(df), descartadas, pct
    )

    if pct > 5:
        logger.warning(
            "TRANSFORMAR | alerta | %.1f%% das linhas descartadas (limite: 5%%)",
            pct
        )

    return df
```

---

## Seção 5 — Métricas de Monitoramento

Logging registra o que aconteceu em cada execução. Métricas permitem observar **tendências ao longo do tempo**: o pipeline está ficando mais lento? O volume caiu de repente? A taxa de nulos está crescendo?

### Cinco métricas básicas para qualquer pipeline

| Métrica | O que medir | Sinal de problema |
|---|---|---|
| **Tempo de execução** | Duração total do pipeline em segundos | Crescimento gradual indica degradação; salto brusco indica problema novo |
| **Volume processado** | Número de linhas lidas e salvas | Volume muito baixo = problema na fonte; volume zero = pipeline não rodou ou fonte vazia |
| **Taxa de erros** | % de execuções que falharam nos últimos N dias | Taxa > 0 em pipeline estável indica problema estrutural |
| **Freshness (atraso)** | Diferença entre a data mais recente dos dados e o horário atual | Atraso crescente indica que o pipeline está atrasado em relação ao SLA |
| **Taxa de nulos por coluna** | % de nulos em colunas críticas a cada execução | Crescimento indica deterioração da fonte — o sistema upstream parou de enviar algum campo |

### Coletando métricas no pipeline

A forma mais simples é registrar as métricas no próprio log ao final da execução:

```python
from datetime import datetime


def main():
    inicio = datetime.now()
    metricas = {}

    try:
        df_raw = extrair("recursos/dados.db")
        metricas["linhas_extraidas"] = len(df_raw)

        df_valido = transformar(df_raw)
        metricas["linhas_transformadas"] = len(df_valido)
        metricas["taxa_descarte"] = (
            (metricas["linhas_extraidas"] - metricas["linhas_transformadas"])
            / metricas["linhas_extraidas"]
        ) if metricas["linhas_extraidas"] > 0 else 0

        carregar(df_valido, "saida/vendas_processadas.parquet")
        metricas["status"] = "sucesso"

    except Exception as e:
        metricas["status"] = "falhou"
        metricas["erro"] = str(e)
        logger.error("PIPELINE | falhou | %s", e)
        sys.exit(1)

    finally:
        metricas["duracao_segundos"] = (datetime.now() - inicio).total_seconds()
        logger.info(
            "PIPELINE | metricas | status=%s | linhas_extraidas=%s | "
            "linhas_salvas=%s | taxa_descarte=%.1f%% | duracao=%.1fs",
            metricas.get("status"),
            metricas.get("linhas_extraidas"),
            metricas.get("linhas_transformadas"),
            metricas.get("taxa_descarte", 0) * 100,
            metricas.get("duracao_segundos", 0),
        )
```

Essa linha de log `PIPELINE | metricas | ...` pode ser parseada por qualquer ferramenta de observabilidade para construir dashboards automáticos.

### Ferramentas que automatizam isso em produção

As métricas acima são suficientes para começar. Quando a complexidade cresce, ferramentas especializadas assumem esse trabalho:

- **Great Expectations** — define expectativas sobre os dados (ex: "coluna X deve ter valores entre 0 e 1000") e gera relatórios de qualidade automaticamente
- **dbt tests** — adiciona testes diretamente nos modelos SQL: `not_null`, `unique`, `accepted_values`, `relationships`
- **Monte Carlo** — observabilidade de dados em escala: detecta anomalias automaticamente sem configuração prévia
- **Soda** — validações baseadas em YAML, integradas a pipelines existentes

Essas ferramentas fazem em escala o que você aprendeu a fazer manualmente neste módulo. Entender o fundamento é o que permite usá-las com discernimento — e não apenas copiar configurações sem saber o que elas verificam.
