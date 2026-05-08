# Roteiro da Sessão ao Vivo — Módulo 3: Formatos de Dados

**Duração total:** 2 horas
**Formato:** facilitador + participantes com Python e as dependências instaladas
**Pré-requisito para os participantes:** ter lido o `conteudo.md`, instalado `pandas` e `pyarrow`, e tentado os exercícios antes da sessão

---

## Abertura — 10 min

**Objetivo:** garantir que todo o grupo tem o ambiente funcionando e criar uma expectativa comum sobre o que será discutido.

**Roteiro:**

1. Boas-vindas e objetivo da sessão (2 min):
   > "Hoje não vamos debater sintaxe. Vamos debater decisões. Qual formato escolher, por quê, e o que acontece quando você escolhe errado."

2. Verificação de ambiente — pedir que todos rodem o snippet abaixo e confirmem que nenhum erro ocorre (3 min):

   ```python
   import pandas as pd
   import pyarrow
   df = pd.read_csv('recursos/exports/vendas.csv')
   print(f"pandas {pd.__version__}, pyarrow {pyarrow.__version__}")
   print(f"Vendas carregadas: {len(df)} linhas, {len(df.columns)} colunas")
   ```

   Resultado esperado: `Vendas carregadas: 3000 linhas, 6 colunas`

   Caso alguém não tenha as dependências:
   ```bash
   pip install pandas pyarrow
   ```

3. Sondagem rápida (levantar a mão ou chat): "Quem já usou Parquet antes de hoje?" (1 min)
   - Útil para calibrar o ritmo da demo

4. Agenda da sessão (2 min):
   - 20 min de demo ao vivo comparando formatos com os dados reais
   - 70 min de exercício em grupo (Ex 3.3 — escolha de formato)
   - 20 min de fechamento e bônus opcional

---

## Demo ao Vivo — Comparando Formatos na Prática — 20 min

**Objetivo:** tornar concreto e visual o que o conteúdo descreveu em texto. Ver os números reais tem mais impacto que qualquer explicação.

**Preparação:** ter o terminal aberto na raiz do projeto com Python disponível.

### Parte 1 — Geração e comparação de tamanhos (10 min)

Execute ao vivo, comentando cada linha enquanto digita:

```python
import os
import pandas as pd

os.makedirs('saida', exist_ok=True)

# Ler o CSV
df = pd.read_csv('recursos/exports/vendas.csv')
df['data_venda'] = pd.to_datetime(df['data_venda'])

# Gerar os outros formatos
df.to_json('saida/vendas.json', orient='records', indent=2, force_ascii=False)
df.to_parquet('saida/vendas.parquet', compression='snappy', index=False)

# Comparar tamanhos
arquivos = [
    ('CSV',     'recursos/exports/vendas.csv'),
    ('JSON',    'saida/vendas.json'),
    ('Parquet', 'saida/vendas.parquet'),
]

print(f"{'Formato':<10}  {'Bytes':>12}  {'KB':>8}")
print("-" * 35)
for nome, caminho in arquivos:
    tam = os.path.getsize(caminho)
    print(f"{nome:<10}  {tam:>12,}  {tam/1024:>8.1f}")
```

**Perguntas para o grupo após ver os números:**
- "O JSON ficou maior que o CSV. Alguém esperava isso?"
- "O Parquet ficou 5–6x menor. O que o motor do Parquet fez que o CSV não faz?"
- Dar 2 minutos para o grupo tentar responder antes de explicar.

### Parte 2 — Leitura seletiva de colunas (10 min)

```python
import time
import pandas as pd

N = 100

# Parquet — leitura seletiva
t0 = time.time()
for _ in range(N):
    pd.read_parquet('saida/vendas.parquet', columns=['data_venda', 'valor_total'])
t_parquet = time.time() - t0

# CSV — mesmo subset de colunas (mas lê a linha toda internamente)
t0 = time.time()
for _ in range(N):
    pd.read_csv('recursos/exports/vendas.csv', usecols=['data_venda', 'valor_total'])
t_csv = time.time() - t0

print(f"Parquet: {t_parquet:.3f}s total  |  {t_parquet/N*1000:.2f}ms por leitura")
print(f"CSV:     {t_csv:.3f}s total  |  {t_csv/N*1000:.2f}ms por leitura")
print(f"Speedup: {t_csv/t_parquet:.1f}x")
```

**Contexto a passar ao grupo:**

> "Com 3.000 linhas a diferença absoluta parece pequena — alguns milissegundos. Mas imaginem essa mesma operação em uma tabela com 500 milhões de linhas e 50 colunas. Parquet leria apenas 2/50 das colunas. O CSV leria tudo. A diferença passa a ser de minutos vs horas."

Abrir um arquivo Parquet no explorador de arquivos e comparar com o CSV para mostrar visualmente que o binário não é legível. Reforçar: "o preço da eficiência é a legibilidade humana — mas em dados de produção, ninguém abre o arquivo na mão."

---

## Exercício em Grupo — Ex 3.3 — 70 min

**Objetivo:** desenvolver critério de decisão através de debate, não de memorização. Ênfase explícita: **não há sempre uma resposta única** — o que importa é a qualidade da argumentação.

### Etapa 1 — Trabalho individual silencioso (15 min)

Pedir que cada participante leia os 5 cenários e anote suas respostas individualmente antes de qualquer discussão. Isso garante que todos tenham uma posição própria, sem ser influenciados pelo primeiro a falar.

> "Escreva suas respostas agora. Em 15 minutos, vamos discutir. Se você não sabe um cenário, tudo bem — escreva sua melhor hipótese e por quê você chegou a ela."

### Etapa 2 — Coleta de respostas (10 min)

Para cada cenário, perguntar ao grupo: "Quem escolheu X? Quem escolheu Y?"

Anotar as divergências em lousa/slide colaborativo. Os cenários com mais divergência são os mais ricos para discussão.

**Divergências esperadas e como conduzir:**

- **Cenário A:** JSON é consenso, mas alguns podem propor CSV. Perguntar: "Como você representaria a lista de itens do pedido em CSV?"
- **Cenário B:** A divisão broker vs data lake costuma gerar confusão. Reforçar que o cenário tem **dois** sistemas com necessidades diferentes.
- **Cenário C:** Alguns podem dizer JSON, especialmente quem nunca usou Schema Registry. Perguntar: "Quando o campo `segmento_cliente` for adicionado, como o time de cobrança vai saber que precisa atualizar o consumidor?"
- **Cenário D:** Este é o mais ambíguo — CSV, JSON e YAML são todos defensáveis. O ponto não é qual é certo, mas **o analista de negócios consegue editar sem ajuda?**
- **Cenário E:** Delta Lake não é óbvio para quem não o conhece. Aceitar SCD Tipo 2 em Parquet como resposta válida, mas perguntar: "O que acontece se você processar um lote errado e precisar reverter 3 dias de dados?"

### Etapa 3 — Discussão dos cenários mais divergentes (30 min)

Focar tempo nas divergências identificadas na Etapa 2. Para cada divergência:

1. Pedir que quem escolheu cada opção explique o raciocínio (2 min)
2. Perguntar ao grupo: "Há algum cenário onde a outra escolha também seria válida?" (3 min)
3. Facilitador sintetiza os critérios que determinam a escolha (2 min)

**Pontos que o facilitador deve garantir que aparecem:**

- A decisão de formato é sempre um trade-off — não existe melhor absoluto
- Legibilidade humana vs eficiência de máquina é o eixo central
- Schema evolution é frequentemente subestimado por quem nunca sofreu uma quebra de contrato em produção
- Delta Lake não é "Parquet melhor" — é uma camada de confiabilidade que tem custo operacional (precisa de cluster Spark ou Delta-rs)

### Etapa 4 — Fechamento do exercício (15 min)

Apresentar o gabarito do Ex 3.3 para os cenários com mais divergência, focando não na resposta certa, mas nos **critérios de decisão** que levam a ela.

Perguntar ao grupo:
- "Algum cenário mudou sua opinião? Por quê?"
- "Em qual dos 5 cenários você ainda não tem certeza da resposta?"

---

## Fechamento — 20 min

### Resumo do módulo (10 min)

Retomar os objetivos de aprendizagem do `README.md` e checar cada um:

| Objetivo | Coberto por |
|---|---|
| Diferenças entre CSV, JSON, Parquet, Avro, Delta | Seção 1 (tabela comparativa) + demo ao vivo |
| Escolher formato por cenário | Seção 6 + Ex 3.3 |
| Ler/escrever formatos com Python | Seções 2, 3, 4 + Ex 3.1 |
| Por que Parquet e Delta são padrão moderno | Seção 4 e 5 + demo de leitura seletiva |

Perguntar ao grupo:
- "Qual formato vocês mais usam hoje no trabalho?"
- "Qual formato vocês deveriam estar usando e não estão?"
- "Qual conceito ainda gera dúvida?"

### Bônus — Delta Lake ao vivo (se sobrar tempo, ~10 min)

Se o grupo tiver `deltalake` instalado (`pip install deltalake`), mostrar ao vivo:

```python
import pandas as pd
from deltalake.writer import write_deltalake
from deltalake import DeltaTable
import os

os.makedirs('saida/delta_vendas', exist_ok=True)

df = pd.read_csv('recursos/exports/vendas.csv')
df['data_venda'] = pd.to_datetime(df['data_venda'])

# Versão inicial
write_deltalake('saida/delta_vendas', df, mode='overwrite')

# Simular uma atualização (append de novos dados)
df_novo = df.head(10).copy()
df_novo['valor_total'] = df_novo['valor_total'] * 1.1  # reajuste de 10%
write_deltalake('saida/delta_vendas', df_novo, mode='append')

# Inspecionar o transaction log
dt = DeltaTable('saida/delta_vendas')
print("Versão atual:", dt.version())
print("Histórico:")
print(dt.history())

# Time travel: consultar a versão anterior
dt_v0 = DeltaTable('saida/delta_vendas', version=0)
df_v0 = dt_v0.to_pandas()
print(f"\nVersão 0: {len(df_v0)} linhas")
```

**Mensagem a passar:**

> "Vocês acabaram de ver time travel em data engineering. A tabela tem agora duas versões no mesmo diretório — sem mágica, apenas um log de transações sobre arquivos Parquet normais. Em produção, isso é o que permite fazer rollback de um ETL errado que corrompeu 3 dias de dados."

Se não houver tempo para a demo, explicar o conceito verbalmente e mostrar a estrutura de pastas de uma tabela Delta de exemplo.

### Preview do Módulo 4 (5 min)

O próximo módulo cobre **Pipelines de Dados com Python** (ETL/ELT):
- Orquestração com Airflow ou Prefect
- Transformações com pandas e dbt
- Estratégias de ingestão incremental
- Tratamento de erros e idempotência

**Recomendação antes do Módulo 4:** revise o Exercício 3.1 e tente adicionar um quarto formato — CSV comprimido com GZIP (`df.to_csv('saida/vendas.csv.gz', compression='gzip', index=False)`) — e compare o tamanho com o Parquet. Reflita: se CSV comprimido fica quase do mesmo tamanho que Parquet, por que ainda preferimos Parquet?

### Encerramento (5 min)

- Compartilhar link do material (conteudo.md, exercicios.md, gabarito.md)
- Data da próxima sessão
- Canal de dúvidas assíncronas (Slack/Teams)
