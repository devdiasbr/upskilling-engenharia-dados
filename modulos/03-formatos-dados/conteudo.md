# Conteúdo — Módulo 3: Formatos de Dados

> Antes de começar, confirme que o banco e os exports existem. Caso necessário, rode `python recursos/setup_db.py`.

---

## Seção 1 — Visão Geral dos Formatos

Nenhum formato é universalmente melhor. A escolha certa depende do contexto: quem vai ler o arquivo, com que frequência, quais colunas, e se os dados precisam evoluir com o tempo.

### Tabela comparativa

| Formato | Orientação | Legibilidade humana | Compressão nativa | Schema embutido | Melhor caso de uso |
|---|---|---|---|---|---|
| **CSV** | Linha | Alta (texto plano) | Nenhuma | Não | Troca de dados entre sistemas, imports manuais |
| **JSON** | Linha | Alta (texto estruturado) | Nenhuma | Parcial (inferida) | APIs REST, configurações, dados aninhados |
| **Parquet** | Coluna | Baixa (binário) | Sim (Snappy, GZIP, ZSTD) | Sim | Analytics, data lakes, pipelines de leitura intensiva |
| **Avro** | Linha | Baixa (binário) | Sim | Sim (evolução de schema) | Streaming de eventos, Kafka, integração entre sistemas |
| **Delta Lake** | Coluna (Parquet + log) | Baixa (binário) | Sim (herda do Parquet) | Sim + ACID | Lakehouse, tabelas com updates/deletes, auditoria |

### O que significa "orientação de coluna"?

Em um arquivo orientado a **linhas** (CSV, JSON, Avro), os dados de cada registro ficam contíguos no disco:

```
registro 1: [venda_id=1, cliente_id=42, valor=150.00, data=2024-01-15]
registro 2: [venda_id=2, cliente_id=17, valor=89.90,  data=2024-01-15]
registro 3: [venda_id=3, cliente_id=42, valor=320.00, data=2024-01-16]
```

Em um arquivo orientado a **colunas** (Parquet), os dados de cada coluna ficam contíguos:

```
coluna venda_id:    [1, 2, 3, ...]
coluna cliente_id:  [42, 17, 42, ...]
coluna valor:       [150.00, 89.90, 320.00, ...]
coluna data:        [2024-01-15, 2024-01-15, 2024-01-16, ...]
```

Isso significa que uma query `SELECT SUM(valor) FROM vendas` lê apenas a coluna `valor` — ignora completamente `venda_id`, `cliente_id` e `data`. Em tabelas com dezenas de colunas e bilhões de linhas, a diferença é de ordens de magnitude.

---

## Seção 2 — CSV

### O que é

CSV (Comma-Separated Values) é um arquivo de texto onde cada linha representa um registro e os campos são separados por um delimitador (vírgula por padrão, mas pode ser ponto-e-vírgula, tab, pipe etc.). A primeira linha geralmente contém os nomes das colunas.

```
venda_id,cliente_id,produto_id,quantidade,valor_total,data_venda
1,42,7,2,150.00,2024-01-15
2,17,3,1,89.90,2024-01-15
```

### Casos de uso

- Exportação de relatórios para Excel ou Google Sheets
- Troca de dados entre sistemas legados
- Cargas iniciais de dados (seed data)
- Configurações simples tabulares

### Limitações

- **Sem tipos de dados**: tudo é texto; datas, números e booleanos dependem de parsing pelo consumidor
- **Sem schema**: renomear colunas ou mudar a ordem quebra consumidores
- **Sem compressão nativa**: um CSV de 1 GB ocupa 1 GB em disco (mesmo que os dados sejam muito repetitivos)
- **Dados aninhados impossíveis**: uma coluna não pode conter uma lista ou um objeto

### Lendo CSV com a biblioteca padrão

```python
import csv

with open('recursos/exports/vendas.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)
# Cada `row` é um dict: {'venda_id': '1', 'cliente_id': '42', ...}
# Nota: todos os valores são strings — use int(), float() para converter
```

### Lendo CSV com pandas

```python
import pandas as pd

df = pd.read_csv('recursos/exports/vendas.csv')
print(df.head())
print(df.dtypes)
# pandas infere os tipos automaticamente: int64, float64, object
```

### Escrevendo CSV com pandas

```python
import pandas as pd

df = pd.read_csv('recursos/exports/clientes.csv')
# Filtrar e salvar um subconjunto
df[df['estado'] == 'SP'].to_csv('saida/clientes_sp.csv', index=False)
```

O parâmetro `index=False` evita que o pandas escreva o índice do DataFrame como uma coluna extra.

---

## Seção 3 — JSON

### O que é

JSON (JavaScript Object Notation) é um formato de texto que representa dados como objetos aninhados e listas. Suporta tipos primitivos (string, number, boolean, null) e estruturas compostas (arrays, objects).

```json
[
  {
    "venda_id": 1,
    "cliente_id": 42,
    "itens": [
      {"produto_id": 7, "quantidade": 2, "preco_unit": 75.00}
    ],
    "data_venda": "2024-01-15"
  }
]
```

### Casos de uso

- Respostas de APIs REST
- Configurações de aplicações
- Logs estruturados
- Dados com estrutura hierárquica ou variável entre registros

### Limitações

- **Sem schema formal**: qualquer campo pode aparecer em qualquer registro (ou não aparecer)
- **Sem compressão nativa**: assim como CSV, é texto puro
- **Verboso**: os nomes das chaves se repetem em cada registro, inflando o tamanho
- **Leitura linha a linha é ineficiente**: para grandes volumes, parsing de JSON é mais lento que leitura de Parquet

### Exportando uma tabela do SQLite para JSON

```python
import sqlite3
import json

conn = sqlite3.connect('recursos/dados.db')
cursor = conn.execute("SELECT * FROM clientes LIMIT 5")
cols = [d[0] for d in cursor.description]
rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
conn.close()

import os
os.makedirs('saida', exist_ok=True)

with open('saida/clientes.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

print(f"Exportados {len(rows)} registros")
```

O parâmetro `ensure_ascii=False` preserva caracteres especiais (acentos, cedilha) no arquivo.

### Exportando com pandas

```python
import pandas as pd

df = pd.read_csv('recursos/exports/vendas.csv')

import os
os.makedirs('saida', exist_ok=True)

# orient='records' → lista de objetos JSON, um por linha lógica
df.to_json('saida/vendas.json', orient='records', indent=2, force_ascii=False)
```

### Lendo JSON com pandas

```python
import pandas as pd

df = pd.read_json('saida/clientes.json', orient='records')
print(df.head())
```

---

## Seção 4 — Parquet

### O que é

Parquet é um formato binário colunar desenvolvido pelo Apache, amplamente usado em ecossistemas de big data (Spark, Hive, Presto, Athena, BigQuery). Cada arquivo Parquet contém:

- **Schema embutido**: tipos de dados precisos (INT32, FLOAT, STRING, DATE, etc.)
- **Dados organizados por coluna**: otimizado para leitura seletiva
- **Compressão por coluna**: cada coluna é comprimida independentemente (Snappy por padrão, GZIP para maior compressão, ZSTD para o melhor custo-benefício)
- **Estatísticas por chunk**: min/max de cada coluna em cada group, permitindo ao engine pular blocos irrelevantes (predicate pushdown)

### Por que Parquet é mais eficiente para analytics

| Operação | CSV (95 KB, vendas) | Parquet (estimativa com Snappy) |
|---|---|---|
| `SELECT *` | Lê 100% do arquivo | Lê 100% do arquivo |
| `SELECT SUM(valor_total)` | Lê 100% do arquivo | Lê apenas a coluna valor_total (~15% do arquivo) |
| `SELECT * WHERE data_venda = '2024-06'` | Lê 100% do arquivo | Pode pular grupos fora do range (predicate pushdown) |

### Dependência

```bash
pip install pyarrow
```

pandas usa pyarrow (ou fastparquet) como engine de leitura/escrita de Parquet.

### Ler CSV e salvar como Parquet

```python
import pandas as pd

# Ler o CSV de vendas
df = pd.read_csv('recursos/exports/vendas.csv')

# Converter data_venda para tipo datetime (melhora compressão e queries)
df['data_venda'] = pd.to_datetime(df['data_venda'])

import os
os.makedirs('saida', exist_ok=True)

# Salvar como Parquet com compressão Snappy
df.to_parquet('saida/vendas.parquet', compression='snappy', index=False)

print("Arquivo gerado: saida/vendas.parquet")
```

### Leitura seletiva de colunas

A vantagem mais imediata do Parquet no dia a dia é poder ler apenas as colunas necessárias:

```python
import pandas as pd

# Ler APENAS duas colunas — o restante nem é lido do disco
df = pd.read_parquet(
    'saida/vendas.parquet',
    columns=['data_venda', 'valor_total']
)

# Calcular receita por mês
df['mes'] = df['data_venda'].dt.to_period('M')
receita_por_mes = df.groupby('mes')['valor_total'].sum().sort_index()
print(receita_por_mes)
```

### Comparando tamanhos

```python
import os

arquivos = {
    'CSV':     'recursos/exports/vendas.csv',
    'JSON':    'saida/vendas.json',
    'Parquet': 'saida/vendas.parquet',
}

for nome, caminho in arquivos.items():
    if os.path.exists(caminho):
        tamanho = os.path.getsize(caminho)
        print(f"{nome:10s}: {tamanho:>10,} bytes  ({tamanho / 1024:.1f} KB)")
```

Resultado típico com os dados deste curso:

```
CSV       :     97,493 bytes  (95.2 KB)
JSON      :    220,000 bytes  (215 KB)   ← verboso: repete nomes de chaves
Parquet   :     18,000 bytes  (17.6 KB)  ← compressão + schema eficiente
```

JSON é maior que CSV porque os nomes de todas as chaves se repetem em cada registro.

---

## Seção 5 — Delta Lake e Avro (conceitual)

### Delta Lake

Delta Lake é uma camada de armazenamento open-source (originalmente criada pela Databricks) que adiciona propriedades ACID sobre arquivos Parquet em um data lake.

**Como funciona:**
- Os dados ficam em arquivos Parquet normais
- Um **transaction log** (pasta `_delta_log/`) registra cada operação (INSERT, UPDATE, DELETE) como um arquivo JSON
- A combinação dos arquivos Parquet + o log garante consistência e suporte a operações transacionais

**Funcionalidades principais:**

| Funcionalidade | O que significa |
|---|---|
| **ACID transactions** | Múltiplos writers não corrompem a tabela; reads sempre veem um estado consistente |
| **Time travel** | Consultar versões anteriores da tabela: `SELECT * FROM tabela VERSION AS OF 5` |
| **Schema enforcement** | Escrever dados com schema incompatível falha com erro claro, não silenciosamente |
| **Schema evolution** | Adicionar colunas sem reescrever todos os dados históricos |
| **Upsert (MERGE)** | Atualizar registros existentes ou inserir novos em uma só operação |

**Quando usar Delta Lake:**
- Tabelas em um data lake que recebem updates ou deletes (ex: tabela de clientes com endereços que mudam)
- Pipelines onde múltiplos jobs escrevem na mesma tabela em paralelo
- Qualquer cenário que exige auditoria ou rollback de dados

**Quando Delta não é necessário:**
- Dados imutáveis (logs de eventos onde você só acrescenta)
- Arquivos gerados uma vez para consumo externo
- Ambientes fora do ecossistema Spark/Databricks/Delta-rs

### Avro

Avro é um formato de serialização binário orientado a linhas, desenvolvido pelo Apache, muito popular em sistemas de streaming de eventos.

**Características:**

| Característica | Detalhe |
|---|---|
| **Schema embutido** | O schema Avro (definido em JSON) é incluído no arquivo ou transmitido separadamente via Schema Registry |
| **Schema evolution** | Suporta adicionar/remover campos com valores default, sem quebrar consumidores antigos |
| **Orientado a linhas** | Eficiente para gravar e ler registros completos — ideal para streaming |
| **Compressão** | Suporta Snappy, Deflate, Bzip2 |

**Quando usar Avro:**
- Mensagens em Apache Kafka (padrão de fato com Confluent Schema Registry)
- Integração entre sistemas onde o schema pode mudar ao longo do tempo
- Pipelines de ingestão onde os dados são gravados registro a registro

**Avro vs Parquet:**

| Critério | Avro | Parquet |
|---|---|---|
| Orientação | Linha | Coluna |
| Escrever registro a registro | Eficiente | Ineficiente (precisa acumular um batch) |
| Ler coluna selecionada | Ineficiente (lê o registro completo) | Muito eficiente |
| Caso de uso primário | Streaming, Kafka | Analytics, data lake |

---

## Seção 6 — Critério de Escolha

Use o guia abaixo como ponto de partida. Na prática, os critérios se combinam e raramente há uma resposta única.

### Guia de decisão

```
Preciso trocar dados com um humano ou sistema externo?
  ├── Dados tabulares simples → CSV
  └── Dados com estrutura hierárquica ou vindo de API → JSON

Preciso armazenar dados para processamento/analytics?
  ├── Dados imutáveis (append-only) → Parquet
  └── Dados com updates, deletes ou necessidade de histórico → Delta Lake

Preciso transmitir eventos em tempo real (streaming)?
  ├── Schema pode mudar ao longo do tempo → Avro + Schema Registry
  └── Schema estável e throughput é prioritário → qualquer binário (Avro, Protobuf)
```

### Resumo por caso de uso

| Cenário | Formato recomendado | Motivo principal |
|---|---|---|
| Export de relatório para o cliente | CSV | Legível em Excel sem instalação |
| Resposta de uma API REST | JSON | Padrão universal para HTTP APIs |
| Tabela de fatos em um data lake | Parquet | Compressão + leitura seletiva |
| Eventos de clickstream em Kafka | Avro | Schema evolution + eficiência em streaming |
| Tabela com SCD Tipo 2 ou GDPR deletes | Delta Lake | ACID + time travel + MERGE |
| Configuração trocada por e-mail | JSON ou CSV | Editável por humano sem ferramentas especiais |
| Pipeline de ML com features numéricas | Parquet | Leitura de colunas específicas, compressão alta |

### Por que Parquet virou o padrão em data engineering

Em 2015, a maioria dos data lakes armazenava dados como CSV ou JSON. O problema era óbvio: queries analíticas liam 100% dos dados mesmo para calcular uma única métrica. Com o crescimento dos volumes, o custo (tempo + dinheiro em cloud) se tornou insustentável.

Parquet resolveu isso de forma elegante: ao organizar os dados por coluna, comprimir cada coluna com algoritmos otimizados para o tipo de dado, e embutir estatísticas que permitem ao engine pular blocos inteiros, a leitura analítica passou a ser ordens de magnitude mais rápida — sem mudar o SQL escrito pelo analista.

Delta Lake veio depois para resolver o próximo problema: como fazer updates e deletes em um lake de arquivos imutáveis? A resposta foi adicionar um log transacional sobre o Parquet, criando o conceito de **lakehouse** — a confiabilidade de um data warehouse com a flexibilidade e o custo de um data lake.
