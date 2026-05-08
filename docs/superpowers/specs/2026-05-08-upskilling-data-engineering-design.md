# Design: Programa de Upskilling — Fundamentos de Engenharia de Dados

**Data:** 2026-05-08
**Autor:** Bruno Dias

---

## Contexto

Programa de nivelamento em fundamentos de engenharia de dados para um time composto por profissionais em migração de carreira, júniors e plenos. O objetivo é garantir que todos tenham uma base sólida, sem gaps nos conceitos fundamentais, independente do nível ou papel final.

---

## Público-alvo

- Profissionais em migração de carreira
- Engenheiros de dados júnior
- Engenheiros de dados pleno (com experiência de mercado, mas sem formação específica em dados)

Todos seguem o mesmo conteúdo no próprio ritmo. Plenos tendem a avançar mais rápido pela experiência geral de mercado.

---

## Formato

- **Primário:** self-guided (auto-guiado)
- **Secundário:** sessão ao vivo opcional, 1x/semana, 2 horas
  - Formato da sessão: Q&A sobre o módulo da semana + exercício prático em grupo
  - Roteiro de apresentação criado conforme necessidade

---

## Estrutura da Trilha

Progressão linear e sequencial. A pessoa avança quando conclui o módulo, sem prazo fixo por módulo.

### Módulo 1 — SQL Fundamentals
- Consultas básicas: SELECT, WHERE, GROUP BY, ORDER BY
- JOINs: INNER, LEFT, RIGHT, FULL
- Agregações e funções de grupo
- Subqueries e CTEs
- Window functions: ROW_NUMBER, RANK, LAG, LEAD, SUM/AVG OVER
- Noções de otimização: índices, plano de execução, evitar full scan

### Módulo 2 — Modelagem de Dados
- Modelagem relacional: entidades, relacionamentos, chaves primárias e estrangeiras
- Normalização: 1FN, 2FN, 3FN — quando normalizar e quando não normalizar
- Modelagem dimensional: fato, dimensão, star schema, snowflake schema
- Introdução a Data Vault (conceito)
- Quando usar cada tipo de modelagem

### Módulo 3 — Formatos de Dados
- CSV e JSON: casos de uso, limitações, boas práticas
- Parquet: formato colunar, compressão, por que é padrão em dados
- Avro: serialização, schema evolution
- Delta: versionamento, ACID transactions, time travel
- Critérios de escolha por cenário

### Módulo 4 — Python para Dados
- Estruturas de dados essenciais: listas, dicionários, sets
- Manipulação de arquivos: leitura/escrita CSV, JSON
- Pandas: DataFrames, operações básicas, merge, groupby
- Funções, módulos e boas práticas de código
- Automação de tarefas repetitivas

### Módulo 5 — Lógica de ETL/ELT
- Diferença entre ETL e ELT
- Extração: APIs, bancos de dados, arquivos
- Transformação: limpeza, enriquecimento, padronização
- Carga: estratégias de insert, upsert, full load, incremental
- Idempotência: o que é e por que importa
- Tratamento de erros e reprocessamento

### Módulo 6 — Engenharia de Pipelines
- Conceito de orquestração de fluxos
- Visão geral de ferramentas: Airflow, Prefect, Databricks Workflows
- Controle de dependências entre tarefas
- Controle de erros, retentativas, alertas
- Versionamento de código com Git: commits, branches, pull requests

### Módulo 7 — Armazenamento e Processamento
- Data Warehouse: conceitos, uso, exemplos
- Data Lake: estrutura, zonas (raw, trusted, refined)
- Lakehouse: convergência de DW e Data Lake
- Noções de processamento distribuído: por que existe, como funciona
- Base conceitual para PySpark
- Particionamento e performance de consultas

### Módulo 8 — Qualidade e Observabilidade
- O que é qualidade de dados: completude, consistência, acurácia, timeliness
- Estratégias de validação de dados em pipelines
- Testes de pipeline: unitários e de integração
- Logging: o que logar, níveis de log
- Monitoramento básico: métricas, alertas, SLA de dados

---

## Soft Skills (integradas aos módulos)

Não formam um módulo isolado. São introduzidas no contexto de cada módulo:

- Entender o negócio por trás dos dados → módulos de modelagem e ETL
- Comunicar decisões técnicas para não-técnicos → módulos de pipeline e qualidade
- Documentar o que constrói → ao longo de todos os módulos

---

## O que este programa NÃO cobre (próxima fase)

- Ferramentas específicas (Databricks, Azure, AWS, dbt, etc.)
- PySpark avançado
- Lakeflow Declarative Pipelines
- Arquiteturas avançadas (Medallion, Data Mesh)

---

## Critérios de Sucesso

- Todo o time consegue estruturar um pipeline ETL funcional com Python
- Todo o time entende e aplica os conceitos de modelagem dimensional
- Todo o time sabe escolher o formato de dado adequado para cada cenário
- Nenhum profissional tem gaps silenciosos nos fundamentos listados
