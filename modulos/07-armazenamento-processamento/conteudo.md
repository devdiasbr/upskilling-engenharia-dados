# Módulo 7 — Armazenamento e Processamento: Conteúdo

---

## Seção 1 — Data Warehouse

### O que é

Um **Data Warehouse (DW)** é um sistema de armazenamento analítico projetado para consultas rápidas sobre dados históricos estruturados. Ele não é um banco transacional — não serve para registrar um pedido no momento em que ele acontece. Serve para responder perguntas como "qual foi a receita por região no último trimestre?" de forma confiável e previsível.

### Características fundamentais

**Schema-on-write:** os dados só entram no DW depois de transformados e validados. O esquema (tipos de colunas, relações, regras de negócio) é definido e aplicado antes da escrita. Se um registro não respeita o esquema, ele é rejeitado na entrada — não na hora da consulta.

**Dados limpos e modelados:** o que está no DW é a versão curada dos dados. Os scripts ETL dos módulos 4 e 5 são exatamente o trabalho que acontece *antes* dos dados chegarem ao DW.

**Otimizado para SQL analítico:** DWs modernos usam armazenamento colunar, compressão e índices especializados para acelerar queries que leem poucas colunas mas muitas linhas — o padrão de acesso analítico.

**Exemplos de ferramentas:**
- **Snowflake** — cloud-native, separa armazenamento de computação, muito usado em empresas de médio e grande porte
- **BigQuery** (Google) — serverless, escala automaticamente, cobra por dados lidos na query
- **Amazon Redshift** — integrado ao ecossistema AWS, baseado em PostgreSQL
- **Azure Synapse Analytics** — integrado ao ecossistema Microsoft, combina DW com spark

### Quando usar um Data Warehouse

Use um DW quando:
- Os dados de entrada são estruturados e têm esquema estável
- Há SLA de performance para dashboards e relatórios (ex.: query deve responder em menos de 5 segundos)
- O time de negócio consome os dados via SQL ou ferramentas de BI (Power BI, Tableau, Looker)
- A governança de qualidade de dados é crítica — você não pode exibir dados sujos no dashboard do CEO

Evite um DW como destino primário quando:
- Os dados chegam em formato semiestruturado ou não estruturado (logs JSON, imagens, áudio)
- O volume cresce de forma imprevisível e o esquema pode mudar frequentemente
- O custo de transformar tudo antes da ingestão é proibitivo

---

## Seção 2 — Data Lake

### O que é

Um **Data Lake** é um repositório centralizado de dados em formato bruto, armazenado em sistemas de arquivos distribuídos de baixo custo como S3 (AWS), ADLS (Azure) ou GCS (Google Cloud). O princípio central é: ingira agora, transforme depois — ou talvez nunca, se não precisar.

### Características fundamentais

**Dados brutos em formato original:** um Data Lake aceita qualquer coisa — CSV, JSON, Parquet, Avro, imagens, vídeos, logs de servidor, arquivos binários. Nada é transformado na ingestão.

**Schema-on-read:** o esquema só é definido quando alguém vai ler os dados. Isso dá flexibilidade máxima na entrada, mas exige que o leitor saiba interpretar o que está lá.

**Armazenamento barato:** S3, ADLS e GCS cobram centavos por GB/mês. Um DW gerenciado pode custar dezenas de vezes mais pelo mesmo volume de dados frios.

### O risco do "data swamp"

Sem organização e governança, um Data Lake vira um **data swamp** — um pântano de dados onde ninguém sabe o que existe, ninguém confia no que lê e os dados mais antigos são ilegíveis porque o formato mudou e ninguém documentou.

Sinais de um data swamp:
- Arquivos sem nome descritivo (ex.: `export_final_v3_REVISADO2.csv`)
- Sem separação entre dados brutos e processados
- Sem catálogo de dados — ninguém sabe o que cada pasta contém
- Dados duplicados em múltiplos formatos sem versionamento

A solução é estrutura intencional: as **zonas do Data Lake**.

### Zonas típicas

Um Data Lake bem organizado divide os dados em três zonas. Cada zona tem um contrato de qualidade diferente.

```
data-lake/
├── raw/
│   ├── vendas/
│   │   ├── 2024/01/vendas_20240101.json
│   │   ├── 2024/01/vendas_20240102.json
│   │   └── ...
│   ├── clientes/
│   │   └── clientes_export_20240115.csv
│   └── produtos/
│       └── catalogo_produtos_v12.xml
│
├── trusted/
│   ├── vendas/
│   │   └── year=2024/month=01/vendas.parquet
│   ├── clientes/
│   │   └── clientes.parquet
│   └── produtos/
│       └── produtos.parquet
│
└── refined/
    ├── vendas_por_cliente/
    │   └── vendas_por_cliente.parquet
    ├── receita_mensal/
    │   └── receita_mensal.parquet
    └── top_produtos/
        └── top_produtos.parquet
```

**Zona raw/** — dados brutos, nunca modificados

- Armazena exatamente o que chegou da fonte, no formato original
- Nunca sobrescreve, nunca deleta
- É a "verdade imutável" — se algo der errado nas zonas seguintes, você sempre pode voltar aqui
- Nomenclatura inclui data de recebimento para rastreabilidade

**Zona trusted/** — dados limpos e validados

- Dados que passaram por limpeza: nulos tratados, tipos corrigidos, encoding padronizado, duplicatas removidas
- Geralmente convertidos para Parquet para melhor performance
- Organizados por partição de data para facilitar leitura seletiva
- Ainda próximos do dado original — sem joins ou agregações

**Zona refined/** — dados modelados, prontos para consumo

- Resultado das transformações de negócio: joins entre tabelas, métricas calculadas, agregações
- É o que alimenta dashboards, modelos de ML e relatórios
- Equivalente ao que estaria em um DW — mas sem o custo de um sistema especializado
- Atualizado pelo pipeline de transformação (os scripts do Módulo 5, orquestrados pelo pipeline do Módulo 6)

### Conectando ao projeto dos módulos anteriores

Os scripts que você escreveu nos módulos 4 e 5 leem do banco SQLite (`recursos/dados.db`) e produzem arquivos de saída. Em um Data Lake real, esses artefatos teriam este destino:

| Artefato | Zona | Justificativa |
|---|---|---|
| Dump bruto do SQLite em JSON | `raw/` | Dado original sem transformação |
| CSVs de vendas, clientes, produtos lidos do banco | `raw/` | Extração direta da fonte |
| DataFrame pandas limpo (nulos removidos, tipos corrigidos) | `trusted/` | Passou por validação e limpeza |
| Resultado do join vendas + clientes + produtos com métricas | `refined/` | Transformação de negócio aplicada |
| Arquivo de receita por mês | `refined/` | Agregação — dado derivado, pronto para BI |

---

## Seção 3 — Lakehouse

### O problema que resolve

O Data Lake é barato e flexível, mas sem garantias transacionais. Se o pipeline falha no meio de uma escrita, você pode ter arquivos parcialmente escritos. Não há controle de concorrência — dois jobs escrevendo no mesmo diretório podem corromper os dados. E sem versionamento, você não consegue ver como os dados estavam ontem.

O Data Warehouse tem essas garantias, mas é caro e exige transformação prévia.

O **Lakehouse** combina o melhor dos dois mundos: armazena dados no Data Lake (barato, qualquer formato) mas adiciona uma camada de metadados e protocolo transacional que dá ao storage as garantias de um banco de dados.

### Como funciona

O Lakehouse é habilitado por **formatos de tabela abertos** que adicionam uma camada de gerenciamento sobre arquivos Parquet comuns:

**Delta Lake** (criado pela Databricks, agora open source)
- Armazena um transaction log junto com os arquivos Parquet
- Cada escrita é atômica — ou acontece inteira ou não acontece
- Suporta UPDATE, DELETE e MERGE por cima de arquivos em S3/ADLS/GCS
- **Time travel:** `SELECT * FROM tabela VERSION AS OF 5` lê como os dados estavam 5 versões atrás

**Apache Iceberg** (criado pela Netflix, adotado amplamente)
- Gerencia schema evolution — adicionar/remover colunas sem reescrever os arquivos
- Melhor suporte a tabelas com bilhões de arquivos
- Suportado nativamente pelo Snowflake, BigQuery e Spark

**Apache Hudi** (criado pela Uber)
- Foco em upserts eficientes — ideal para casos de uso com muitas atualizações incrementais
- Originalmente projetado para sincronizar bancos transacionais com o data lake em near-real-time

### Plataformas que implementam Lakehouse

| Plataforma | Formato de tabela | Características |
|---|---|---|
| Databricks | Delta Lake | Plataforma unificada Spark + notebook + ML |
| Snowflake com Iceberg | Apache Iceberg | DW gerenciado com acesso a dados externos |
| BigQuery com tabelas abertas | Apache Iceberg | Serverless, integrado ao Google Cloud |
| AWS Lake Formation + Glue | Apache Iceberg / Hudi | Ecossistema AWS gerenciado |

### Quando usar cada arquitetura — resumo

| Critério | Data Warehouse | Data Lake | Lakehouse |
|---|---|---|---|
| Formato dos dados | Estruturado | Qualquer | Qualquer |
| Custo de armazenamento | Alto | Baixo | Baixo |
| Performance de query SQL | Excelente | Variável | Boa |
| Garantias ACID | Sim | Não (nativo) | Sim |
| Dados brutos preservados | Não | Sim | Sim |
| Schema obrigatório na entrada | Sim | Não | Opcional |
| Complexidade operacional | Média | Alta sem governança | Média-alta |

---

## Seção 4 — Processamento Distribuído

### Por que existe

Imagine um arquivo de logs de servidor: 1 TB de dados, representando 10 bilhões de linhas. Uma máquina com 16 GB de RAM não consegue carregar esse arquivo em memória. Mesmo que conseguisse, processar 10 bilhões de linhas em um único processo levaria horas.

A solução é **dividir o trabalho**: em vez de uma máquina fazendo tudo, um cluster de 100 máquinas divide os dados em 100 partes e cada máquina processa a sua parte em paralelo. O tempo total cai de horas para minutos.

Este é o princípio do **processamento distribuído**: particionar os dados, processar cada partição em paralelo em diferentes nós do cluster, e depois agregar os resultados.

### Como funciona (simplificado)

```
Dados originais (1 TB)
         │
         ▼
┌─────────────────┐
│   Particionamento│  — divide os dados em N partes
└─────────────────┘
         │
    ┌────┴────┐
    ▼         ▼         ▼         ...
[Nó 1]    [Nó 2]    [Nó 3]    [Nó N]
parte 1   parte 2   parte 3   parte N
    │         │         │         │
    └────┬────┘         └────┬────┘
         ▼                   ▼
    [Shuffle]          [Shuffle]       — redistribuição dos dados entre nós
         │
         ▼
   [Agregação]       — combina resultados parciais de cada nó
         │
         ▼
   Resultado final
```

O passo de **shuffle** é o mais custoso: quando uma operação como `GROUP BY` precisa que todos os registros de um mesmo grupo estejam no mesmo nó, os dados precisam ser redistribuídos pela rede. Minimizar shuffles é uma das principais otimizações em Spark.

### Apache Spark

O **Apache Spark** é o motor de processamento distribuído open source mais usado na indústria de dados. Criado na UC Berkeley em 2009, ele se tornou o padrão de fato para processamento de grandes volumes.

**O que o Spark resolve:**
- Processa dados que não cabem em uma máquina
- Executa o mesmo código em clusters de dezenas ou centenas de nós
- Suporta batch (processar tudo de uma vez) e streaming (processar em tempo real)
- Tem APIs em Python (PySpark), Scala, Java, R e SQL

**Conceitos fundamentais:**

**DataFrame Spark:** estrutura de dados distribuída, similar ao pandas DataFrame mas particionada entre nós do cluster. As operações são traduzidas em um plano de execução otimizado.

**Transformações lazy:** quando você escreve `df.filter(...)` no Spark, nada é executado imediatamente. O Spark apenas registra a operação no plano de execução. Isso permite que o Spark otimize o plano completo antes de rodar — evitando trabalho desnecessário.

**Actions:** são as operações que de fato acionam a execução — `show()`, `count()`, `write()`, `collect()`. Só quando você chama uma action o Spark executa tudo que estava planejado.

**Driver e Executors:** o processo driver coordena o trabalho e distribui tarefas. Os executors rodam nos nós do cluster e processam as partições de dados.

### Pandas vs PySpark — mesma intenção, escala diferente

A lógica de transformação é a mesma. O que muda é o motor de execução e a escala para a qual cada um foi projetado.

```python
# pandas — funciona bem até ~1-2 GB na memória da máquina local
resultado = (
    df.query("valor_total > 100")
    .merge(df_clientes, on='cliente_id', how='left')
    .groupby('cidade')
    .agg(receita=('valor_total', 'sum'), total_vendas=('venda_id', 'nunique'))
    .sort_values('receita', ascending=False)
    .head(10)
)

# PySpark equivalente — processa os mesmos dados em um cluster de 100 máquinas
from pyspark.sql import functions as F

resultado = (
    df.filter(F.col('valor_total') > 100)
    .join(df_clientes, on='cliente_id', how='left')
    .groupBy('cidade')
    .agg(F.sum('valor_total').alias('receita'), F.countDistinct('venda_id').alias('total_vendas'))
    .orderBy('receita', ascending=False)
    .limit(10)
)
```

**Diferenças visíveis:**

| Elemento | pandas | PySpark |
|---|---|---|
| Filtro | `.query("valor_total > 100")` | `.filter(F.col('valor_total') > 100)` |
| Join | `.merge(..., how='left')` | `.join(..., how='left')` |
| Agrupamento | `.groupby(...)` | `.groupBy(...)` (B maiúsculo) |
| Agregação | `.agg(receita=('col', 'sum'))` | `.agg(F.sum('col').alias('receita'))` |
| Ordenação | `.sort_values('col')` | `.orderBy('col')` |
| Limite | `.head(10)` | `.limit(10)` |

A transição de pandas para PySpark é gradual — o raciocínio é idêntico, a sintaxe muda em detalhes.

### Quando usar cada um

| Situação | Ferramenta indicada |
|---|---|
| Dataset cabe na memória da máquina (< 1–2 GB) | pandas |
| Dataset é grande mas roda OK em modo local | pandas com chunking ou Polars |
| Dataset não cabe em uma máquina (> alguns GB) | PySpark em cluster |
| Processamento recorrente em escala de produção | PySpark ou Spark gerenciado (Databricks, EMR) |
| Exploração rápida, prototipagem | pandas sempre |

---

## Seção 5 — Particionamento

### O que é

**Particionamento** é a prática de dividir um dataset em subdiretórios baseados nos valores de uma ou mais colunas. Em vez de um único arquivo grande, você tem uma árvore de diretórios onde cada pasta representa um subconjunto dos dados.

```
vendas_particionado/
├── ano=2023/
│   ├── mes=01/vendas.parquet
│   ├── mes=02/vendas.parquet
│   └── ...
├── ano=2024/
│   ├── mes=01/vendas.parquet
│   ├── mes=02/vendas.parquet
│   └── ...
```

### Como a leitura se beneficia

Sem particionamento, para ler as vendas de janeiro de 2024, você leria o arquivo inteiro e filtraria depois — mesmo que só precisasse de 1/24 dos dados.

Com particionamento por ano e mês, o motor de leitura (pandas, Spark, Athena) sabe que só precisa abrir `ano=2024/mes=01/`. Os outros 23 diretórios nem são tocados. Isso é chamado de **partition pruning** — podas de partição.

O ganho é proporcional à seletividade do filtro: se você frequentemente filtra por mês, particionar por mês significa ler 1/N dos dados em vez de todos.

### Escrevendo dados particionados com pandas

```python
import pandas as pd
import sqlite3

# Ler vendas do banco
conn = sqlite3.connect('recursos/dados.db')
df = pd.read_sql_query("""
    SELECT
        v.venda_id,
        v.data_venda,
        v.valor_total,
        v.cliente_id,
        v.produto_id
    FROM vendas v
""", conn)
conn.close()

# Extrair ano e mês da coluna de data
df['data_venda'] = pd.to_datetime(df['data_venda'])
df['ano'] = df['data_venda'].dt.year
df['mes'] = df['data_venda'].dt.month

# Escrever particionado
df.to_parquet(
    'trusted/vendas/',
    partition_cols=['ano', 'mes'],
    index=False
)
```

Resultado no disco:
```
trusted/vendas/
├── ano=2023/
│   ├── mes=1/
│   │   └── part-0.parquet
│   └── mes=2/
│       └── part-0.parquet
└── ano=2024/
    ├── mes=1/
    │   └── part-0.parquet
    └── mes=2/
        └── part-0.parquet
```

### Lendo apenas uma partição

```python
# Ler apenas vendas de janeiro de 2024
df_jan = pd.read_parquet('trusted/vendas/', filters=[('ano', '=', 2024), ('mes', '=', 1)])

# Apenas um subdiretório foi lido — os demais foram ignorados
print(f"Registros lidos: {len(df_jan)}")
```

### Escolhendo a coluna de particionamento

Esta é a decisão mais importante. Escolha errada anula o benefício do particionamento.

**Boas colunas para particionar:**
- **Data (ano, mês)** — a mais comum em dados analíticos. Queries quase sempre filtram por período
- **Região ou país** — se análises por região são frequentes
- **Status** — se filtrar por `status = 'pendente'` é um padrão recorrente
- **Tipo de evento** — em logs de sistema onde o tipo é consultado com frequência

**Colunas a evitar:**
- **IDs únicos** (venda_id, cliente_id) — alta cardinalidade cria milhões de diretórios, cada um com apenas um arquivo minúsculo. O overhead de abrir muitos arquivos pequenos é pior que ler um arquivo grande
- **Colunas com muitos valores nulos** — cria uma partição `coluna=None/` que concentra muitos dados sem benefício
- **Colunas que nunca aparecem em filtros** — particionar por elas não ajuda nenhuma query

**Regra prática:** escolha colunas que aparecem frequentemente em cláusulas `WHERE` e que tenham cardinalidade baixa a moderada (entre 10 e alguns milhares de valores distintos).

### Tamanho ideal de arquivo

Além da coluna certa, o tamanho de cada arquivo de partição importa. A convenção para Parquet em ambientes distribuídos é arquivos de **128 MB a 1 GB**. Arquivos muito pequenos (< 1 MB) geram overhead de I/O — é o chamado "small files problem". Arquivos muito grandes perdem o paralelismo.

Em pandas local isso raramente é problema. Em Spark, controla-se com `df.repartition(n)` antes de escrever.
