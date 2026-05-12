# Trilha de Engenharia de Dados — NTT DATA UNIVERSITY

Formação prática em fundamentos de engenharia de dados estruturada em 9 módulos sequenciais. Cada módulo cobre um tema com conteúdo teórico, exercícios práticos e roteiro de sessão ao vivo de 2 horas.

---

## Quick Start

```bash
# 1. Clone o repositório
git clone https://github.com/devdiasbr/upskilling-engenharia-dados.git
cd upskilling-engenharia-dados

# 2. Crie o banco de dados (SQLite — sem instalação extra)
python recursos/setup_db.py

# 3. Instale as dependências Python
pip install pandas pyarrow

# 4. Comece pelo Módulo 1
cat modulos/01-sql-fundamentals/README.md
```

> Todos os exercícios dos 9 módulos usam o mesmo banco gerado no passo 2.

---

## Estrutura do Repositório

```
apresentacao-curso/          ← docs de apresentação da trilha
  para-participantes.md
  para-gestores.md
  para-facilitadores.md
  apresentacao-curso.pptx

modulos/
  01-sql-fundamentals/
  02-modelagem-dados/
  03-formatos-dados/
  04-python-dados/
  05-logica-etl-elt/
  06-engenharia-pipelines/
  07-armazenamento-processamento/
  08-qualidade-observabilidade/
  09-troubleshooting/

recursos/
  dados.db                   ← banco SQLite (gerado pelo setup_db.py)
  schema.md                  ← descrição das tabelas
  setup_db.py                ← script de geração do banco
  exports/                   ← CSVs das tabelas para exercícios de formato
```

Cada pasta de módulo tem:

```
0X-nome/
  README.md             ← objetivos, pré-requisitos, duração
  conteudo.md           ← material teórico com exemplos
  sessao-ao-vivo.md     ← roteiro da sessão ao vivo (para facilitadores)
  sessao-ao-vivo-*.pptx ← apresentação gerada
  exercicios/
    exercicios.md
    gabarito.md
```

---

## Os 9 Módulos

| # | Tema | O que você vai construir |
|---|------|--------------------------|
| 01 | [SQL Fundamentals](modulos/01-sql-fundamentals/) | Queries, JOINs, CTEs, window functions |
| 02 | [Modelagem de Dados](modulos/02-modelagem-dados/) | Modelo relacional, chaves, normalização |
| 03 | [Formatos de Dados](modulos/03-formatos-dados/) | CSV, JSON, Parquet — quando usar cada um |
| 04 | [Python para Dados](modulos/04-python-dados/) | Primeiro pipeline ETL com pandas + sqlite3 |
| 05 | [Lógica de ETL/ELT](modulos/05-logica-etl-elt/) | Idempotência, logging, tratamento de erros |
| 06 | [Engenharia de Pipelines](modulos/06-engenharia-pipelines/) | Airflow, DAGs, Git para pipelines |
| 07 | [Armazenamento e Processamento](modulos/07-armazenamento-processamento/) | Data Lake, Lakehouse, Spark |
| 08 | [Qualidade e Observabilidade](modulos/08-qualidade-observabilidade/) | 5 dimensões, validações, TDD com pytest |
| 09 | [Troubleshooting](modulos/09-troubleshooting/) | Reproduzir → Isolar → Corrigir → Prevenir |

---

## Pré-requisitos

- Python 3.10+
- Lógica de programação básica
- Familiaridade com terminal

SQL, pandas e banco de dados são ensinados do zero na trilha.

---

## Banco de Dados

Dataset fictício de e-commerce com dados em português gerados com Faker e seeds fixas — todos os participantes têm os mesmos dados.

| Tabela | Registros | Descrição |
|--------|-----------|-----------|
| `categorias` | 8 | Categorias de produto |
| `produtos` | 60 | Catálogo de produtos com preços |
| `clientes` | 300 | Clientes com cidade e estado |
| `vendas` | 3.000 | Transações 2023–2024 |

Veja o schema completo em [`recursos/schema.md`](recursos/schema.md).

---

## Apresentação da Trilha

Para apresentar o curso a diferentes públicos:

- [`apresentacao-curso/para-participantes.md`](apresentacao-curso/para-participantes.md) — o que vão aprender, estrutura, carga horária
- [`apresentacao-curso/para-gestores.md`](apresentacao-curso/para-gestores.md) — problema resolvido, ROI, recursos necessários
- [`apresentacao-curso/para-facilitadores.md`](apresentacao-curso/para-facilitadores.md) — como preparar e conduzir cada sessão
- [`apresentacao-curso/apresentacao-curso.pptx`](apresentacao-curso/apresentacao-curso.pptx) — deck de 14 slides

---

## Sumário Completo

Navegação detalhada por módulo e seção: [`SUMARIO.md`](SUMARIO.md)
