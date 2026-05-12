# Gabarito — Módulo 3: Formatos de Dados

> Consulte este gabarito apenas depois de tentar os exercícios. O objetivo não é copiar o código, mas comparar a sua abordagem e entender as diferenças.

---

## Exercício 3.1 — Conversão de Formatos

```python
import os
import pandas as pd

# Criar pasta de saída se não existir
os.makedirs('saida', exist_ok=True)

# --- Ler o CSV original ---
df = pd.read_csv('recursos/exports/vendas.csv')

# Converter data_venda para datetime antes de salvar como Parquet
# Parquet armazena datas com tipo nativo (DATE/TIMESTAMP), o que melhora a
# compressão e evita problemas de parsing ao ler de volta
df['data_venda'] = pd.to_datetime(df['data_venda'])

# --- a) Salvar como JSON ---
df.to_json('saida/vendas.json', orient='records', indent=2, force_ascii=False)

# --- b) Salvar como Parquet com compressão Snappy ---
df.to_parquet('saida/vendas.parquet', compression='snappy', index=False)

# --- c) Comparar tamanhos ---
arquivos = [
    ('CSV',     'recursos/exports/vendas.csv'),
    ('JSON',    'saida/vendas.json'),
    ('Parquet', 'saida/vendas.parquet'),
]

print(f"{'Formato':<10}  {'Caminho':<35}  {'Bytes':>12}  {'KB':>8}")
print(f"{'-'*10}  {'-'*35}  {'-'*12}  {'-'*8}")

for nome, caminho in arquivos:
    if os.path.exists(caminho):
        tamanho = os.path.getsize(caminho)
        print(f"{nome:<10}  {caminho:<35}  {tamanho:>12,}  {tamanho / 1024:>8.1f}")
    else:
        print(f"{nome:<10}  {caminho:<35}  {'(não encontrado)':>21}")
```

**Resultado esperado:**

```
Formato     Caminho                              Bytes       KB
----------  -----------------------------------  ----------  ------
CSV         recursos/exports/vendas.csv          97,493       95.2
JSON        saida/vendas.json                   ~220,000     ~215.0
Parquet     saida/vendas.parquet                 ~18,000      ~17.6
```

**Por que JSON ficou maior que CSV?**

Em CSV, cada campo aparece uma vez na linha de cabeçalho. Em JSON, o nome de cada chave se repete em todos os registros. Com 3.000 vendas e, digamos, 6 campos, isso significa que `"venda_id"`, `"cliente_id"`, `"produto_id"`, etc. aparecem 3.000 vezes cada — muito overhead de metadados para os mesmos dados.

**Por que Parquet é tão menor?**

Dois motivos combinados:
1. **Codificação colunar**: valores iguais ou próximos ficam contíguos, tornando os algoritmos de compressão muito mais eficientes. Por exemplo, a coluna `quantidade` provavelmente só tem valores entre 1 e 5 — armazenada em coluna com run-length encoding, isso comprime quase perfeitamente.
2. **Compressão Snappy**: depois da codificação colunar, o Snappy aplica compressão lossless que reduz ainda mais o tamanho, especialmente em strings repetitivas e inteiros de baixa cardinalidade.

---

## Exercício 3.2 — Leitura Seletiva com Parquet

### Parte principal — receita por mês

```python
import pandas as pd

# Ler APENAS as colunas necessárias — as demais colunas nem são lidas do disco
df = pd.read_parquet(
    'saida/vendas.parquet',
    columns=['data_venda', 'valor_total']
)

# Criar coluna de período mensal (ex: "2024-01")
df['mes'] = df['data_venda'].dt.to_period('M')

# Agregar receita por mês
receita_por_mes = (
    df.groupby('mes')['valor_total']
    .sum()
    .sort_index()
    .rename('receita_total')
)

print(receita_por_mes.to_string())
print(f"\nTotal geral: R$ {receita_por_mes.sum():,.2f}")
```

### Bônus — comparação de tempo

```python
import time
import pandas as pd

N = 100  # número de repetições

# --- Parquet (leitura seletiva) ---
inicio = time.time()
for _ in range(N):
    pd.read_parquet('saida/vendas.parquet', columns=['data_venda', 'valor_total'])
tempo_parquet = time.time() - inicio

# --- CSV (leitura seletiva com usecols) ---
inicio = time.time()
for _ in range(N):
    pd.read_csv('recursos/exports/vendas.csv', usecols=['data_venda', 'valor_total'])
tempo_csv = time.time() - inicio

print(f"Parquet ({N}x): {tempo_parquet:.3f}s  |  média: {tempo_parquet/N*1000:.2f}ms por leitura")
print(f"CSV    ({N}x): {tempo_csv:.3f}s  |  média: {tempo_csv/N*1000:.2f}ms por leitura")
print(f"Parquet é {tempo_csv/tempo_parquet:.1f}x mais rápido nesta leitura")
```

**Interpretação esperada:**

Com apenas 3.000 linhas, a diferença absoluta será pequena (dezenas de milissegundos). A diferença relativa, porém, já é visível: Parquet costuma ser 2–5x mais rápido mesmo em arquivos pequenos, porque:
- O arquivo é menor (menos leitura de disco/IO)
- Os tipos já estão definidos (sem parsing de strings para inferir tipos)
- A leitura seletiva de colunas é nativa (CSV com `usecols` ainda lê a linha inteira para descartar os campos)

O ganho escala dramaticamente com o volume. Em uma tabela de 10 GB com 50 colunas, ler 2 colunas em Parquet pode ser 20–50x mais rápido que CSV.

**Resposta sobre fração lida:**

O arquivo de vendas tem 6 colunas (`venda_id`, `cliente_id`, `produto_id`, `quantidade`, `valor_total`, `data_venda`). Ao ler apenas `data_venda` e `valor_total`, lemos aproximadamente 2/6 = 33% dos dados — e na prática menos, porque `valor_total` comprime melhor que strings.

---

## Exercício 3.3 — Escolha de Formato por Cenário

### Cenário A — API REST de pedidos

**Formato: JSON**

JSON é o formato padrão para APIs HTTP por razões de interoperabilidade universal: qualquer linguagem de programação tem um parser JSON nativo ou em biblioteca padrão, e os dados hierárquicos (pedido com lista de itens) se representam naturalmente como objetos aninhados. CSV não suporta estruturas aninhadas, e Parquet/Avro são binários que exigem bibliotecas específicas no cliente — inviável para um app mobile ou parceiro externo.

Note que "padrão" não significa "ideal em todos os casos": para APIs de alto throughput interno onde os consumidores são todos controlados pelo mesmo time, formatos binários como Protocol Buffers ou MessagePack podem ser mais eficientes.

### Cenário B — Pipeline de clickstream

**Data lake após processamento Spark: Parquet**
**Fila de mensagens (broker): Avro**

Os dois estágios têm necessidades diferentes. Na fila de mensagens, os eventos chegam registro a registro e precisam de schema evolution (novos campos de produto não devem quebrar consumidores de marketing). Avro é otimizado exatamente para isso.

Após o processamento pelo Spark, os dados são armazenados para consultas analíticas (funil, cohort, retenção). Aqui Parquet domina: queries de analytics leem poucas colunas de bilhões de eventos, e Parquet reduz o volume lido em 80–95% em relação a CSV ou JSON. A compressão também reduz drasticamente o custo de armazenamento em cloud.

### Cenário C — Kafka com schema evolutivo

**Formato: Avro com Confluent Schema Registry**

Avro foi criado precisamente para este cenário: schema embutido, suporte nativo a schema evolution com compatibilidade backward/forward, e integração de primeira classe com o ecossistema Kafka (Confluent Schema Registry gerencia as versões de schema centralmente). Quando o campo `segmento_cliente` for adicionado com um valor default, consumidores que ainda estão na versão antiga continuarão funcionando sem nenhuma mudança — o campo simplesmente não existe para eles.

JSON seria uma alternativa aceitável para volumes menores, mas sem controle de schema via registry, a probabilidade de um consumidor quebrar por uma mudança de campo aumenta muito em equipes distribuídas.

### Cenário D — Arquivo de configuração trocado por e-mail

**Formato: JSON ou CSV (dependendo da estrutura)**

O critério dominante aqui é a legibilidade e editabilidade humana: o arquivo será criado por um analista sem background técnico em um editor de texto ou planilha. CSV é ideal se a configuração for uma tabela simples (ex: lista de parâmetros com nome e valor). JSON é melhor se houver agrupamentos lógicos ou parâmetros opcionais.

Ambos podem ser abertos e editados sem instalar nenhuma ferramenta. Parquet, Avro e Delta Lake exigem bibliotecas e conhecimento técnico para edição — completamente inadequados para este cenário. YAML seria outra opção válida e é muito usado para configurações por ser mais legível que JSON (sem chaves obrigatórias em strings simples).

### Cenário E — Tabela de clientes com histórico e rollback

**Formato/tecnologia: Delta Lake**

Este é o caso de uso central do Delta Lake. Os requisitos — consulta a versões anteriores (time travel) e rollback — são impossíveis com arquivos Parquet simples, que são imutáveis por natureza. Delta Lake resolve isso mantendo um transaction log que registra cada versão da tabela. `SELECT * FROM clientes VERSION AS OF 365` retorna o estado da tabela há 365 versões atrás, e `RESTORE TABLE clientes TO VERSION AS OF 42` faz o rollback.

Além disso, updates e deletes diários (mudanças de endereço, inativações) são operações MERGE/UPDATE eficientes no Delta, enquanto em Parquet puro você precisaria reescrever os arquivos completos ou manter uma lógica de SCD manual complexa.

Se o ambiente não suportar Delta Lake (ex: sem Spark ou Databricks), a alternativa mais próxima seria implementar SCD Tipo 2 manualmente em Parquet com colunas `data_inicio`, `data_fim` e `ativo` — funcional, mas com muito mais código de manutenção.
