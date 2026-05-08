# Exercícios — Módulo 3: Formatos de Dados

> **Dependências:** `pip install pandas pyarrow`
>
> **Antes de começar:** confirme que os exports existem em `recursos/exports/`. Caso necessário, rode `python recursos/setup_db.py`.

---

## Exercício 3.1 — Conversão de Formatos

**Objetivo:** praticar leitura e escrita nos três formatos principais e perceber as diferenças de tamanho.

**Tarefa:**

Usando Python, leia o arquivo `recursos/exports/vendas.csv` e:

a) Salve os mesmos dados como JSON (orient records — lista de objetos)

b) Salve os mesmos dados como Parquet com compressão snappy

c) Compare o tamanho dos três arquivos em bytes e KB, exibindo uma tabela formatada no terminal

**Requisitos:**
- Crie a pasta `saida/` caso ela não exista (use `os.makedirs(..., exist_ok=True)`)
- Os arquivos de saída devem se chamar `saida/vendas.json` e `saida/vendas.parquet`
- Converta a coluna `data_venda` para o tipo `datetime` antes de salvar como Parquet
- A tabela de comparação deve mostrar os três arquivos: CSV original, JSON gerado e Parquet gerado

**Resultado esperado (valores aproximados):**

```
Formato     Caminho                          Bytes       KB
----------  --------------------------  ----------  ------
CSV         recursos/exports/vendas.csv     97,493    95.2
JSON        saida/vendas.json              ~220,000  ~215.0
Parquet     saida/vendas.parquet            ~18,000   ~17.6
```

**Perguntas para reflexão:**
- Por que o JSON ficou maior que o CSV, mesmo contendo os mesmos dados?
- O que explica o Parquet ser tão menor mesmo contendo schema, tipos e metadados extras?

---

## Exercício 3.2 — Leitura Seletiva com Parquet

**Objetivo:** demonstrar na prática a vantagem do Parquet em leitura analítica.

**Pré-requisito:** ter gerado `saida/vendas.parquet` no Exercício 3.1.

**Tarefa:**

a) Leia o arquivo `saida/vendas.parquet` carregando **apenas** as colunas `data_venda` e `valor_total` (use o parâmetro `columns=` do `pd.read_parquet`)

b) Calcule a receita total por mês, exibindo os resultados em ordem cronológica

**Bônus:** compare o tempo de leitura entre as duas abordagens usando `time.time()` ou o módulo `timeit`:

- Leitura 1: `pd.read_parquet('saida/vendas.parquet', columns=['data_venda', 'valor_total'])`
- Leitura 2: `pd.read_csv('recursos/exports/vendas.csv', usecols=['data_venda', 'valor_total'])`

Repita cada leitura 100 vezes para ter uma medição estável e compare os tempos totais.

**Resultado esperado da receita por mês (valores aproximados, pode variar com o seed):**

```
mes
2023-01    XXXX.XX
2023-02    XXXX.XX
...
2024-12    XXXX.XX
```

**Perguntas para reflexão:**
- Quantas colunas tem o arquivo de vendas? Que fração do arquivo foi lida para calcular a receita?
- O ganho de velocidade do Parquet aumentaria ou diminuiria com uma tabela de 50 colunas? E com 500 milhões de linhas?

---

## Exercício 3.3 — Escolha de Formato por Cenário

**Objetivo:** desenvolver critério para escolha de formato em situações reais.

**Tarefa:**

Para cada cenário abaixo, indique o formato mais adequado e justifique em 2–3 frases. Considere os critérios: legibilidade humana, eficiência de leitura/escrita, schema, compressão, compatibilidade e requisitos operacionais do sistema.

Não há resposta única para todos os cenários — o objetivo é argumentar com clareza.

---

**Cenário A — API REST de pedidos**

Você está desenvolvendo uma API que retorna o histórico de pedidos de um cliente. Cada pedido contém dados do cliente, uma lista de itens com produto e quantidade, e o status atual. A API será consumida por um aplicativo mobile e por um sistema de parceiros externos.

Qual formato você escolheria para a resposta da API? Por quê?

---

**Cenário B — Pipeline de eventos de clickstream**

Um e-commerce registra 10 bilhões de eventos por dia (pageviews, cliques, tempo na página). Os eventos são enviados para um broker de mensagens e processados por um pipeline Spark que calcula métricas de funil e relatórios de cohort. O schema dos eventos pode ganhar novos campos à medida que novas funcionalidades são lançadas.

Qual formato você escolheria para armazenar os eventos no data lake depois do processamento pelo Spark? Qual formato usaria para a fila de mensagens (broker)?

---

**Cenário C — Kafka com schema evolutivo**

Sua equipe publica eventos de atualização de cadastro de clientes em um tópico Kafka. Outros times (CRM, marketing, cobrança) consomem esses eventos. Em 6 meses, o time de produto planeja adicionar o campo `segmento_cliente` aos eventos. Os consumidores precisam continuar funcionando sem redeployment.

Qual formato você escolheria para serializar os eventos Kafka? Por quê?

---

**Cenário D — Arquivo de configuração trocado por e-mail**

Um processo batch precisa de um arquivo de configuração com parâmetros de execução (datas de corte, flags de feature, limiares numéricos). O arquivo é criado por um analista de negócios sem background técnico, enviado por e-mail para o time de engenharia e lido pelo script Python antes de cada execução.

Qual formato você escolheria? Por quê?

---

**Cenário E — Tabela de clientes com histórico de mudanças**

Uma tabela de clientes é atualizada diariamente: endereços mudam, clientes são inativados, novos campos são adicionados. O time jurídico exige que seja possível consultar o estado de qualquer registro em qualquer data dos últimos 2 anos (requisito de auditoria). Ocasionalmente, erros de processamento precisam ser revertidos (rollback para uma versão anterior).

Qual formato/tecnologia você escolheria para armazenar essa tabela? Por quê?
