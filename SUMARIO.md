# Sumário — Trilha de Engenharia de Dados

Índice completo da trilha com links para todos os materiais.

---

## Apresentação do Curso

- [Para Participantes](apresentacao-curso/para-participantes.md) — o que vão aprender, estrutura, carga horária
- [Para Gestores](apresentacao-curso/para-gestores.md) — problema resolvido, ROI, recursos necessários
- [Para Facilitadores](apresentacao-curso/para-facilitadores.md) — como preparar e conduzir cada sessão
- [Deck de Apresentação](apresentacao-curso/apresentacao-curso.pptx) — 14 slides

---

## Recursos Compartilhados

- [Schema do Banco de Dados](recursos/schema.md) — 4 tabelas, 3.370 registros
- [Script de Setup](recursos/setup_db.py) — gera o banco SQLite local
- [Exports CSV](recursos/exports/) — arquivos para exercícios de formato

---

## Módulo 01 — SQL Fundamentals

> *"A pergunta ao dado."*

- [README](modulos/01-sql-fundamentals/README.md) — objetivos e pré-requisitos
- [Conteúdo](modulos/01-sql-fundamentals/conteudo.md)
  - Como conectar ao banco
  - Seção 1 — SELECT e Filtros Básicos
  - Seção 2 — JOINs
  - Seção 3 — Agregações e GROUP BY
  - Seção 4 — CTEs (Common Table Expressions)
  - Seção 5 — Window Functions
  - Seção 6 — Performance Básica
- [Exercícios](modulos/01-sql-fundamentals/exercicios/exercicios.md) — 9 exercícios em 3 níveis
- [Gabarito](modulos/01-sql-fundamentals/exercicios/gabarito.md)
- [Roteiro da Sessão ao Vivo](modulos/01-sql-fundamentals/sessao-ao-vivo.md)
- [Apresentação](modulos/01-sql-fundamentals/sessao-ao-vivo-sql-fundamentals.pptx)

---

## Módulo 02 — Modelagem de Dados

> *"Como pensar relacionamentos entre dados."*

- [README](modulos/02-modelagem-dados/README.md)
- [Conteúdo](modulos/02-modelagem-dados/conteudo.md)
  - Seção 1 — Modelagem Relacional
  - Seção 2 — Normalização
  - Seção 3 — Modelagem Dimensional
  - Seção 4 — Quando Usar Cada Modelagem
- [Exercícios](modulos/02-modelagem-dados/exercicios/exercicios.md)
- [Gabarito](modulos/02-modelagem-dados/exercicios/gabarito.md)
- [Roteiro da Sessão ao Vivo](modulos/02-modelagem-dados/sessao-ao-vivo.md)
- [Apresentação](modulos/02-modelagem-dados/sessao-ao-vivo-modelagem-dados.pptx)

---

## Módulo 03 — Formatos de Dados

> *"O formato certo paga seu próprio custo."*

- [README](modulos/03-formatos-dados/README.md)
- [Conteúdo](modulos/03-formatos-dados/conteudo.md)
  - Seção 1 — Visão Geral dos Formatos
  - Seção 2 — CSV
  - Seção 3 — JSON
  - Seção 4 — Parquet
  - Seção 5 — Delta Lake e Avro (conceitual)
  - Seção 6 — Critério de Escolha
- [Exercícios](modulos/03-formatos-dados/exercicios/exercicios.md)
- [Gabarito](modulos/03-formatos-dados/exercicios/gabarito.md)
- [Roteiro da Sessão ao Vivo](modulos/03-formatos-dados/sessao-ao-vivo.md)
- [Apresentação](modulos/03-formatos-dados/sessao-ao-vivo-formatos-dados.pptx)

---

## Módulo 04 — Python para Dados

> *"Pipeline simples é a base do pipeline em produção."*

- [README](modulos/04-python-dados/README.md)
- [Conteúdo](modulos/04-python-dados/conteudo.md)
  - Seção 1 — Estruturas de Dados Essenciais
  - Seção 2 — Lendo do SQLite com Python
  - Seção 3 — Operações Essenciais com Pandas
  - Seção 4 — Funções Reutilizáveis
  - Seção 5 — Estrutura de um Script Python para Dados
- [Exercícios](modulos/04-python-dados/exercicios/exercicios.md)
- [Gabarito](modulos/04-python-dados/exercicios/gabarito.md)
- [Roteiro da Sessão ao Vivo](modulos/04-python-dados/sessao-ao-vivo.md)
- [Apresentação](modulos/04-python-dados/sessao-ao-vivo-python-dados.pptx)

---

## Módulo 05 — Lógica de ETL/ELT

> *"Pipeline que falha silenciosamente é o pior pipeline."*

- [README](modulos/05-logica-etl-elt/README.md)
- [Conteúdo](modulos/05-logica-etl-elt/conteudo.md)
  - Seção 1 — ETL vs ELT
  - Seção 2 — Estratégias de Extração
  - Seção 3 — Transformações Comuns
  - Seção 4 — Estratégias de Carga
  - Seção 5 — Idempotência
  - Seção 6 — Tratamento de Erros e Logging
- [Exercícios](modulos/05-logica-etl-elt/exercicios/exercicios.md)
- [Gabarito](modulos/05-logica-etl-elt/exercicios/gabarito.md)
- [Roteiro da Sessão ao Vivo](modulos/05-logica-etl-elt/sessao-ao-vivo.md)
- [Apresentação](modulos/05-logica-etl-elt/sessao-ao-vivo-logica-etl-elt.pptx)

---

## Módulo 06 — Engenharia de Pipelines

> *"Pipeline que precisa de alguém apertando botão não é produção."*

- [README](modulos/06-engenharia-pipelines/README.md)
- [Conteúdo](modulos/06-engenharia-pipelines/conteudo.md)
  - Seção 1 — O que é Orquestração
  - Seção 2 — Conceitos Fundamentais
  - Seção 3 — Ferramentas Principais
  - Seção 4 — Modelando Dependências
  - Seção 5 — Git para Código de Dados
- [Exercícios](modulos/06-engenharia-pipelines/exercicios/exercicios.md)
- [Gabarito](modulos/06-engenharia-pipelines/exercicios/gabarito.md)
- [Roteiro da Sessão ao Vivo](modulos/06-engenharia-pipelines/sessao-ao-vivo.md)
- [Apresentação](modulos/06-engenharia-pipelines/sessao-ao-vivo-engenharia-pipelines.pptx)

---

## Módulo 07 — Armazenamento e Processamento

> *"Código funciona com 3.000 linhas. E com 3 bilhões?"*

- [README](modulos/07-armazenamento-processamento/README.md)
- [Conteúdo](modulos/07-armazenamento-processamento/conteudo.md)
  - Seção 1 — Data Warehouse
  - Seção 2 — Data Lake
  - Seção 3 — Lakehouse
  - Seção 4 — Processamento Distribuído
  - Seção 5 — Particionamento
- [Exercícios](modulos/07-armazenamento-processamento/exercicios/exercicios.md)
- [Gabarito](modulos/07-armazenamento-processamento/exercicios/gabarito.md)
- [Roteiro da Sessão ao Vivo](modulos/07-armazenamento-processamento/sessao-ao-vivo.md)
- [Apresentação](modulos/07-armazenamento-processamento/sessao-ao-vivo-armazenamento-processamento.pptx)

---

## Módulo 08 — Qualidade e Observabilidade

> *"Dado errado é pior que dado ausente."*

- [README](modulos/08-qualidade-observabilidade/README.md)
- [Conteúdo](modulos/08-qualidade-observabilidade/conteudo.md)
  - Seção 1 — Dimensões de Qualidade de Dados
  - Seção 2 — Validações em Pipeline
  - Seção 3 — Testes de Pipeline
  - Seção 4 — Logging Estruturado
  - Seção 5 — Métricas de Monitoramento
- [Exercícios](modulos/08-qualidade-observabilidade/exercicios/exercicios.md)
- [Gabarito](modulos/08-qualidade-observabilidade/exercicios/gabarito.md)
- [Roteiro da Sessão ao Vivo](modulos/08-qualidade-observabilidade/sessao-ao-vivo.md)
- [Apresentação](modulos/08-qualidade-observabilidade/sessao-ao-vivo-qualidade-observabilidade.pptx)

---

## Módulo 09 — Troubleshooting

> *"Dado errado às 3h. Onde você começa a olhar?"*

- [README](modulos/09-troubleshooting/README.md)
- [Conteúdo](modulos/09-troubleshooting/conteudo.md)
  - Seção 1 — Metodologia: Os Quatro Passos
  - Seção 2 — Pilar 1: Pipelines Quebrados
  - Seção 3 — Pilar 2: Anomalias em Dados
  - Seção 4 — Pilar 3: Performance SQL
  - Seção 5 — Integrando os Três Pilares
- [Exercícios](modulos/09-troubleshooting/exercicios/exercicios.md)
- [Gabarito](modulos/09-troubleshooting/exercicios/gabarito.md)
- [Roteiro da Sessão ao Vivo](modulos/09-troubleshooting/sessao-ao-vivo.md)
- [Apresentação](modulos/09-troubleshooting/sessao-ao-vivo-troubleshooting.pptx)
