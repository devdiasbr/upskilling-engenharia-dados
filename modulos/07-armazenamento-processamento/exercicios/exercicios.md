# Módulo 7 — Exercícios

---

## Exercício 7.1 — DW vs Data Lake vs Lakehouse

**Objetivo:** Aplicar os critérios de escolha de arquitetura a situações concretas.

### Contexto

Para cada cenário abaixo, escolha a arquitetura mais adequada entre **Data Warehouse**, **Data Lake** e **Lakehouse**. Justifique sua escolha em 2 a 4 frases, mencionando pelo menos um critério determinante.

### Cenários

**a) Logs brutos de servidor**

Uma empresa de e-commerce gera ~500 GB/dia de logs de acesso no formato JSON (eventos de clique, navegação, erros de aplicação). A maioria desses logs nunca será analisada, mas é necessário armazená-los por 2 anos para fins de auditoria e eventual investigação de incidentes. Análises acontecem raramente e de forma exploratória.

Qual arquitetura você escolhe? Por quê?

---

**b) Relatórios de vendas com SLA estrito**

Um varejista precisa que o dashboard de vendas diárias esteja disponível para a diretoria toda manhã às 8h. As queries precisam responder em menos de 5 segundos. Os dados vêm de três sistemas transacionais (ERP, CRM e plataforma de e-commerce), todos com esquema estável e bem documentado. O time de BI usa Power BI conectado diretamente à fonte analítica.

Qual arquitetura você escolhe? Por quê?

---

**c) Plataforma unificada de dados brutos, transformados, BI e ML**

Uma fintech quer construir uma plataforma de dados que: (1) preserve os dados brutos das transações para rastreabilidade regulatória, (2) sirva transformações limpas para o time de BI, (3) sirva os mesmos dados para modelos de machine learning em Python, e (4) garanta que operações de UPDATE e DELETE sejam transacionalmente seguras (ex.: ao aplicar uma correção de dados por determinação judicial). O time de engenharia quer usar SQL e Python no mesmo ambiente.

Qual arquitetura você escolhe? Por quê?

---

## Exercício 7.2 — Zonas do Data Lake

**Objetivo:** Projetar a estrutura de pastas de um Data Lake real baseado no pipeline que você construiu nos módulos 4 e 5.

### Contexto

Você construiu um pipeline que:
1. Lê vendas, clientes e produtos do banco SQLite `recursos/dados.db`
2. Limpa os dados (remove nulos, corrige tipos, padroniza strings)
3. Faz join entre as três tabelas
4. Calcula métricas: receita por cliente, receita por produto, receita mensal
5. Salva os resultados em arquivos CSV ou Parquet

Agora imagine que esse pipeline roda em produção em um ambiente de nuvem. Os dados não vêm mais de um SQLite — vêm de APIs e bancos de dados reais.

### Tarefas

**Parte A — Desenhar a estrutura de pastas**

Desenhe a estrutura de diretórios do Data Lake que acomodaria este pipeline. Use o formato de árvore abaixo como ponto de partida:

```
data-lake/
├── raw/
│   └── (complete aqui)
├── trusted/
│   └── (complete aqui)
└── refined/
    └── (complete aqui)
```

Inclua pelo menos 3 arquivos em cada zona. Use nomenclatura realista com datas nos nomes onde fizer sentido.

**Parte B — Justificar a classificação**

Para cada zona, responda:

1. **raw/**: Por que os dados brutos devem nunca ser modificados ou deletados, mesmo depois de processados para trusted/?
2. **trusted/**: Que diferença existe entre um arquivo em `raw/vendas/` e um arquivo em `trusted/vendas/`? Liste pelo menos 3 transformações que justificam a promoção de raw para trusted.
3. **refined/**: O que diferencia um arquivo em `trusted/` de um em `refined/`? Por que essa separação existe?

**Parte C — Rastreabilidade**

Se um analista encontrar um valor suspeito no relatório de receita mensal (em `refined/`), como as zonas do Data Lake ajudam a investigar de onde veio esse valor? Descreva o caminho de investigação em 3 a 5 passos.

---

## Exercício 7.3 — Particionamento na Prática

**Objetivo:** Escrever e ler dados particionados com pandas usando o banco de dados do projeto.

### Pré-requisito

O banco `recursos/dados.db` deve estar acessível. Importe as bibliotecas necessárias:

```python
import pandas as pd
import sqlite3
import os
```

### Parte A — Escrever dados particionados

Escreva um script Python que:

1. Conecte ao banco `recursos/dados.db` e leia a tabela de vendas com a query:
   ```sql
   SELECT venda_id, data_venda, valor_total, cliente_id, produto_id
   FROM vendas
   ```
2. Converta a coluna `data_venda` para o tipo datetime do pandas
3. Crie as colunas `ano` e `mes` a partir de `data_venda`
4. Salve o DataFrame em formato Parquet, particionado por `ano` e `mes`, no diretório `output/trusted/vendas/`
5. Liste os arquivos criados para verificar a estrutura de partições

### Parte B — Ler com filtro de partição

Escreva um script que leia apenas as vendas de um mês específico (escolha qualquer mês que exista nos dados) usando o parâmetro `filters` do `pd.read_parquet`. Imprima:
- Quantos registros foram lidos
- O intervalo de datas do resultado
- A soma total de `valor_total` para esse mês

### Parte C — Análise de escolha de partição

Responda por escrito (sem código) as seguintes questões:

1. Por que particionar os dados por `venda_id` seria uma má escolha para este dataset? O que aconteceria na prática com a estrutura de diretórios?
2. Se uma análise frequente neste dataset for "todas as vendas acima de R$ 500 em qualquer período", particionar por `valor_total` seria uma boa escolha? Justifique.
3. Suponha que o dataset crescesse para 10 anos de dados (120 meses). Compare o custo de leitura de "vendas de janeiro de 2024" com e sem particionamento — em termos de proporção de dados que precisam ser lidos.

---

## Exercício 7.4 — Leitura de PySpark

**Objetivo:** Desenvolver fluência na leitura de código PySpark e tradução para pandas.

### Contexto

Você recebeu o seguinte trecho de código PySpark de um colega que trabalha em Databricks. Você precisa entender o que ele faz e replicar a lógica no ambiente pandas que você já conhece.

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("analise_vendas").getOrCreate()

df_vendas = spark.read.parquet("trusted/vendas/")
df_clientes = spark.read.parquet("trusted/clientes/")
df_produtos = spark.read.parquet("trusted/produtos/")

resultado = (
    df_vendas
    .filter(F.col('valor_total') > 0)
    .join(df_clientes.select('cliente_id', 'nome', 'cidade', 'estado'), on='cliente_id', how='left')
    .join(df_produtos.select('produto_id', 'nome_produto', 'categoria'), on='produto_id', how='left')
    .withColumn('mes_venda', F.date_trunc('month', F.col('data_venda')))
    .groupBy('estado', 'categoria', 'mes_venda')
    .agg(
        F.sum('valor_total').alias('receita_total'),
        F.count('venda_id').alias('qtd_vendas'),
        F.avg('valor_total').alias('ticket_medio')
    )
    .withColumn(
        'rank_categoria',
        F.rank().over(Window.partitionBy('estado', 'mes_venda').orderBy(F.desc('receita_total')))
    )
    .filter(F.col('rank_categoria') <= 3)
    .orderBy('mes_venda', 'estado', 'rank_categoria')
)

resultado.write.mode('overwrite').parquet("refined/top_categorias_por_estado/")
```

### Tarefas

**Parte A — Explicar o que o código faz**

Em linguagem de negócio (não técnica), descreva o que este pipeline produz. Quem seria o consumidor desse resultado (analista de vendas, time de marketing, diretoria)? O que ele pode fazer com esse dado?

**Parte B — Identificar as etapas**

Liste cada etapa do pipeline na sequência, descrevendo em uma linha o que acontece e qual função pandas/SQL equivalente você usaria. Formato sugerido:

| Etapa | O que faz | Equivalente pandas |
|---|---|---|
| `.filter(...)` | ... | ... |
| `.join(df_clientes...)` | ... | ... |
| ... | ... | ... |

**Parte C — Reescrever em pandas**

Reescreva o mesmo pipeline usando pandas. Você pode simular as tabelas de entrada lendo do banco `recursos/dados.db`. O resultado final deve ter as mesmas colunas: `estado`, `categoria`, `mes_venda`, `receita_total`, `qtd_vendas`, `ticket_medio`, `rank_categoria`.

> Dica para o ranking: pandas tem `.rank(method='min')` aplicável após um groupby, ou você pode usar `.groupby(...).apply(...)` para calcular o rank dentro de cada grupo de estado + mês.

**Parte D — Reflexão sobre escala**

Suponha que este dataset tivesse 5 bilhões de linhas em vez de 3.000. Liste dois problemas concretos que surgiriam ao rodar o código pandas do item C, e explique por que o código PySpark original não teria esses problemas.
