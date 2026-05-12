# Módulo 7 — Gabarito

---

## Exercício 7.1 — DW vs Data Lake vs Lakehouse

### Cenário a) — Logs brutos de servidor

**Resposta: Data Lake**

Logs JSON em ~500 GB/dia são semiestruturados e de volume imprevisível. A maioria nunca será analisada — não faz sentido o custo e trabalho de transformá-los antes da ingestão. O Data Lake aceita o dado bruto, armazena barato (S3/GCS) e preserva para eventual consulta. O critério determinante é: **schema-on-read** — só quando alguém precisar investigar um incidente é que o dado será processado, não antes. Ingerir 500 GB/dia em um DW exigiria pipeline de limpeza contínuo e custos de armazenamento muito superiores.

### Cenário b) — Relatórios de vendas com SLA estrito

**Resposta: Data Warehouse**

O critério determinante é o **SLA de 5 segundos** com dados de esquema estável. O DW é otimizado exatamente para esse caso: queries SQL analíticas sobre dados modelados, com compressão colunar e índices que garantem performance previsível. O Power BI conectado diretamente ao DW é o padrão da indústria. Como os dados têm esquema bem definido e são transformados antes de chegar, o schema-on-write não é um problema — é uma vantagem que garante qualidade. Um Data Lake bruto não daria as garantias de performance necessárias.

### Cenário c) — Plataforma unificada com ACID e ML

**Resposta: Lakehouse (com Delta Lake ou Apache Iceberg)**

Nenhuma das outras arquiteturas atende todos os requisitos simultaneamente. O Data Lake preserva os brutos mas não tem ACID para UPDATE/DELETE. O DW tem ACID mas não preserva os brutos nem serve bem para ML em Python. O Lakehouse (ex.: Databricks com Delta Lake) combina: armazenamento barato com dados brutos preservados, garantias ACID para operações de correção, acesso via SQL para BI e via Python para ML, tudo sobre o mesmo dado. O time travel do Delta Lake atende o requisito de rastreabilidade regulatória.

---

## Exercício 7.2 — Zonas do Data Lake

### Parte A — Estrutura de pastas

```
data-lake/
├── raw/
│   ├── vendas/
│   │   ├── 2024/01/vendas_20240101.json
│   │   ├── 2024/01/vendas_20240102.json
│   │   └── 2024/02/vendas_20240201.json
│   ├── clientes/
│   │   ├── clientes_export_20240115.csv
│   │   └── clientes_export_20240201.csv
│   └── produtos/
│       ├── catalogo_produtos_20240101.csv
│       └── catalogo_produtos_20240201.csv
│
├── trusted/
│   ├── vendas/
│   │   ├── ano=2024/mes=1/vendas.parquet
│   │   └── ano=2024/mes=2/vendas.parquet
│   ├── clientes/
│   │   └── clientes.parquet
│   └── produtos/
│       └── produtos.parquet
│
└── refined/
    ├── receita_por_cliente/
    │   └── receita_por_cliente.parquet
    ├── receita_mensal/
    │   └── receita_mensal.parquet
    └── top_produtos_por_categoria/
        └── top_produtos.parquet
```

### Parte B — Justificativa por zona

**raw/ — por que nunca modificar:**
Os dados brutos são a única evidência do que chegou da fonte. Se uma transformação introduzir um bug (ex.: arredondar valores, truncar datas), você precisa ser capaz de reprocessar a partir do dado original. Sem o raw, o erro é irrecuperável. Além disso, regras de negócio mudam — o que você não precisava ontem pode ser valioso amanhã. A imutabilidade do raw é uma garantia de auditabilidade: você pode sempre responder "o que a fonte enviou?" independente do que aconteceu nas camadas seguintes.

**trusted/ — transformações de raw para trusted:**
1. Conversão de tipos: `data_venda` de string para datetime, `valor_total` de string para float
2. Remoção de duplicatas: vendas com o mesmo `venda_id` registradas mais de uma vez
3. Tratamento de nulos: clientes sem `cidade` preenchida recebem valor padrão "Não informado"
4. Normalização de strings: "são paulo", "São Paulo", "SAO PAULO" padronizados para "São Paulo"
5. Conversão de formato: JSON ou CSV convertidos para Parquet para melhor performance

**refined/ — trusted vs refined:**
Em trusted, os dados estão limpos mas ainda espelham as tabelas originais — uma linha por venda, uma linha por cliente. Em refined, dados de múltiplas tabelas foram combinados e transformações de negócio foram aplicadas: joins, agrupamentos, métricas calculadas. Um arquivo em `refined/receita_mensal/` não existe em nenhuma tabela da fonte — foi criado pelo pipeline. A separação existe para que seja possível recomputar o refined a partir do trusted sem precisar voltar à fonte original, e para que o custo de transformação não recaia sobre quem apenas quer consumir o dado pronto.

### Parte C — Rastreabilidade

1. O analista encontra o valor suspeito em `refined/receita_mensal/receita_mensal.parquet` e identifica o mês e o cliente ou produto envolvido.
2. Vai até `trusted/vendas/ano=XXXX/mes=YY/vendas.parquet` e filtra as vendas daquele mês para verificar se o valor já estava presente e correto após a limpeza.
3. Se o valor está errado no trusted, vai até `raw/vendas/XXXX/YY/` e abre o arquivo bruto original para ver o que a fonte enviou.
4. Compara o valor em raw com o valor em trusted — se diferem, há um bug na transformação raw → trusted.
5. Se raw e trusted são iguais, o dado bruto chegou errado da fonte — o problema é upstream (sistema de origem), não no pipeline.

---

## Exercício 7.3 — Particionamento na Prática

### Parte A — Escrever dados particionados

```python
import pandas as pd
import sqlite3
import os

# Conectar ao banco e ler vendas
conn = sqlite3.connect('recursos/dados.db')
df = pd.read_sql_query("""
    SELECT venda_id, data_venda, valor_total, cliente_id, produto_id
    FROM vendas
""", conn)
conn.close()

# Converter data e extrair partições
df['data_venda'] = pd.to_datetime(df['data_venda'])
df['ano'] = df['data_venda'].dt.year
df['mes'] = df['data_venda'].dt.month

print(f"Total de registros: {len(df)}")
print(f"Intervalo de datas: {df['data_venda'].min()} a {df['data_venda'].max()}")
print(f"Anos presentes: {sorted(df['ano'].unique())}")

# Criar diretório de saída
os.makedirs('output/trusted/vendas', exist_ok=True)

# Salvar particionado
df.to_parquet(
    'output/trusted/vendas/',
    partition_cols=['ano', 'mes'],
    index=False
)

print("\nEstrutura criada:")
for root, dirs, files in os.walk('output/trusted/vendas/'):
    level = root.replace('output/trusted/vendas/', '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        print(f'{subindent}{file}')
```

### Parte B — Ler com filtro de partição

```python
import pandas as pd

# Ajuste o ano e mês conforme os dados existentes no seu banco
ANO = 2024
MES = 1

df_mes = pd.read_parquet(
    'output/trusted/vendas/',
    filters=[('ano', '=', ANO), ('mes', '=', MES)]
)

print(f"Registros lidos para {MES:02d}/{ANO}: {len(df_mes)}")
print(f"Intervalo de datas: {df_mes['data_venda'].min()} a {df_mes['data_venda'].max()}")
print(f"Receita total do mês: R$ {df_mes['valor_total'].sum():,.2f}")
```

### Parte C — Análise de escolha de partição

**1. Por que `venda_id` é má escolha:**
`venda_id` é um identificador único — cada venda tem um ID diferente. Particionar por ele criaria um diretório separado para cada venda. Se o dataset tem 100.000 vendas, você teria 100.000 diretórios, cada um com um arquivo minúsculo (provavelmente alguns KB). O overhead de listar e abrir milhares de arquivos pequenos é muito maior do que ler um único arquivo grande. Além disso, nenhuma query do mundo real filtra por `venda_id` específico de forma a beneficiar da partição — quem quer uma venda específica usa um índice ou filtra diretamente no dado. Alta cardinalidade + sem uso em filtros amplos = péssima escolha de partição.

**2. Particionar por `valor_total`:**
Não é uma boa escolha. `valor_total` é uma coluna contínua (float) — na prática tem alta cardinalidade e queries raramente filtram por "exatamente R$ 152,30". O filtro descrito ("acima de R$ 500") é um range, não uma igualdade. Particionamento funciona bem com filtros de igualdade (`ano = 2024`) — para ranges em colunas contínuas, não há benefício real porque os dados estão distribuídos em muitas partições e o motor ainda precisa verificar muitos diretórios. Além disso, qualquer arredondamento na criação das partições introduziria inconsistências.

**3. Proporção de dados lidos — 10 anos (120 meses):**
- **Sem particionamento:** para ler um único mês, você lê 100% dos dados (todos os 120 meses) e filtra depois. Se o dataset total tem 10 GB, você lê 10 GB para obter ~83 MB de resultado.
- **Com particionamento por ano e mês:** para ler janeiro de 2024, você abre apenas `ano=2024/mes=1/`. Lê aproximadamente 1/120 dos dados — cerca de 0,8% do total. Se o dataset tem 10 GB, você lê ~83 MB diretamente, sem desperdício.
- Ganho: 120x menos dados lidos.

---

## Exercício 7.4 — Leitura de PySpark

### Parte A — Explicação em linguagem de negócio

O pipeline produz um relatório mensal das **3 categorias de produtos com maior receita em cada estado**. Para cada combinação de estado + mês, ele identifica quais categorias geraram mais vendas e calcula receita total, quantidade de vendas e ticket médio. O consumidor natural é o **time de vendas ou marketing regionais**: eles usariam esse dado para entender quais categorias dominam em cada estado mês a mês, identificar sazonalidade regional e direcionar campanhas ou estoques. A diretoria usaria para comparar performance por região ao longo do tempo.

### Parte B — Etapas do pipeline

| Etapa | O que faz | Equivalente pandas |
|---|---|---|
| `.filter(F.col('valor_total') > 0)` | Remove registros com valor zero ou negativo | `.query("valor_total > 0")` |
| `.join(df_clientes..., on='cliente_id', how='left')` | Adiciona nome, cidade e estado de cada cliente | `.merge(df_clientes[...], on='cliente_id', how='left')` |
| `.join(df_produtos..., on='produto_id', how='left')` | Adiciona nome e categoria de cada produto | `.merge(df_produtos[...], on='produto_id', how='left')` |
| `.withColumn('mes_venda', F.date_trunc('month', ...))` | Trunca a data para o primeiro dia do mês (agrupa por mês) | `df['mes_venda'] = df['data_venda'].dt.to_period('M')` |
| `.groupBy('estado', 'categoria', 'mes_venda')` | Agrupa por estado, categoria e mês | `.groupby(['estado', 'categoria', 'mes_venda'])` |
| `.agg(F.sum(...), F.count(...), F.avg(...))` | Calcula receita, quantidade e ticket médio | `.agg(receita_total=..., qtd_vendas=..., ticket_medio=...)` |
| `.withColumn('rank_categoria', F.rank().over(Window...))` | Atribui ranking de receita por estado+mês | `.groupby([...]).rank(method='min', ascending=False)` |
| `.filter(F.col('rank_categoria') <= 3)` | Mantém apenas as top 3 categorias | `.query("rank_categoria <= 3")` |
| `.orderBy('mes_venda', 'estado', 'rank_categoria')` | Ordena o resultado final | `.sort_values([...])` |
| `.write.mode('overwrite').parquet(...)` | Salva o resultado em Parquet, sobrescrevendo | `.to_parquet(...)` |

### Parte C — Reescrita em pandas

```python
import pandas as pd
import sqlite3

# Ler dados do banco SQLite
conn = sqlite3.connect('recursos/dados.db')

df_vendas = pd.read_sql_query("""
    SELECT venda_id, data_venda, valor_total, cliente_id, produto_id
    FROM vendas
""", conn)

df_clientes = pd.read_sql_query("""
    SELECT cliente_id, nome, cidade, estado
    FROM clientes
""", conn)

df_produtos = pd.read_sql_query("""
    SELECT produto_id, nome_produto, categoria
    FROM produtos
""", conn)

conn.close()

# Converter tipos
df_vendas['data_venda'] = pd.to_datetime(df_vendas['data_venda'])

# Filtrar registros com valor positivo
df_vendas = df_vendas.query("valor_total > 0")

# Joins
df = (
    df_vendas
    .merge(df_clientes[['cliente_id', 'nome', 'cidade', 'estado']], on='cliente_id', how='left')
    .merge(df_produtos[['produto_id', 'nome_produto', 'categoria']], on='produto_id', how='left')
)

# Criar coluna de mês (primeiro dia do mês para agrupar)
df['mes_venda'] = df['data_venda'].dt.to_period('M').dt.to_timestamp()

# Agregar por estado, categoria e mês
agregado = (
    df.groupby(['estado', 'categoria', 'mes_venda'])
    .agg(
        receita_total=('valor_total', 'sum'),
        qtd_vendas=('venda_id', 'count'),
        ticket_medio=('valor_total', 'mean')
    )
    .reset_index()
)

# Calcular ranking dentro de cada estado+mês por receita (descendente)
agregado['rank_categoria'] = (
    agregado
    .groupby(['estado', 'mes_venda'])['receita_total']
    .rank(method='min', ascending=False)
    .astype(int)
)

# Filtrar top 3 por estado+mês
resultado = (
    agregado
    .query("rank_categoria <= 3")
    .sort_values(['mes_venda', 'estado', 'rank_categoria'])
    .reset_index(drop=True)
)

print(resultado.head(15).to_string(index=False))
print(f"\nTotal de linhas: {len(resultado)}")

# Salvar resultado
import os
os.makedirs('output/refined/top_categorias_por_estado', exist_ok=True)
resultado.to_parquet('output/refined/top_categorias_por_estado/top_categorias.parquet', index=False)
```

### Parte D — Reflexão sobre escala

**Problema 1 — Memória insuficiente:**
Com 5 bilhões de linhas, o DataFrame pandas não cabe na memória de uma máquina convencional. Uma linha com 6 colunas numéricas ocupa ~200 bytes — 5 bilhões de linhas seriam ~1 TB de RAM. O processo Python simplesmente travaria com `MemoryError` ou seria encerrado pelo sistema operacional antes de terminar. O PySpark divide os dados entre os executors do cluster — cada nó processa apenas sua partição, que pode caber confortavelmente na memória local.

**Problema 2 — Tempo de processamento impraticável:**
Pandas processa os dados sequencialmente em um único core (operações groupby/merge não usam múltiplos núcleos de forma eficaz). Com 5 bilhões de linhas, o join e o groupby levariam horas ou dias. O PySpark distribui o trabalho entre dezenas de nós do cluster, processando partições em paralelo. O mesmo job que levaria 8 horas em pandas local pode rodar em 10 minutos com um cluster de 20 nós. Além disso, o Spark usa execução lazy e otimiza o plano antes de rodar — ele sabe que pode fazer o filtro antes do join, reduzindo drasticamente os dados trafegados na rede entre nós.
