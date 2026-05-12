# Trilha de Engenharia de Dados — Para Participantes

## O que é esta trilha?

Uma formação prática de fundamentos em engenharia de dados estruturada em 9 módulos sequenciais. O foco é construir a base que você precisa para trabalhar com pipelines, dados e infraestrutura de dados — independente de ferramenta ou cloud.

A trilha foi desenhada para quem já tem alguma experiência em tecnologia e quer entender como dados se movem, se transformam e chegam ao destino certo.

---

## O que você vai aprender

Ao concluir a trilha, você será capaz de:

- Escrever queries SQL para consultar, transformar e analisar dados
- Modelar bancos de dados relacionais com integridade e clareza
- Trabalhar com diferentes formatos de dados (CSV, JSON, Parquet)
- Construir pipelines ETL em Python com pandas e sqlite3
- Aplicar os princípios de idempotência, logging e tratamento de erros
- Orquestrar pipelines com Airflow e versionar com Git
- Entender as arquiteturas de armazenamento (Data Lake, Lakehouse, Spark)
- Garantir qualidade de dados com as 5 dimensões e TDD
- Diagnosticar e corrigir problemas em pipelines e dados com metodologia sistemática

---

## Estrutura da Trilha

| Módulo | Tema | O que você vai fazer |
|--------|------|---------------------|
| 01 | SQL Fundamentals | Consultar, filtrar, agregar, CTEs, window functions |
| 02 | Modelagem de Dados | Entidades, chaves, normalização, integridade |
| 03 | Formatos de Dados | CSV, JSON, Parquet — escolher pelo cenário |
| 04 | Python para Dados | pandas, sqlite3, primeiro pipeline ETL |
| 05 | Lógica de ETL/ELT | Idempotência, logging, falha explícita |
| 06 | Engenharia de Pipelines | Airflow, DAGs, Git para pipelines |
| 07 | Armazenamento e Processamento | Data Lake, Lakehouse, Spark distribuído |
| 08 | Qualidade e Observabilidade | 5 dimensões, validações, TDD com pytest |
| 09 | Troubleshooting | Reproduzir → Isolar → Corrigir → Prevenir |

---

## Como funciona cada módulo

Cada módulo tem quatro componentes:

1. **Conteúdo assíncrono** (`conteudo.md`) — leitura com exemplos comentados. Estude no seu ritmo antes da sessão ao vivo.
2. **Exercícios práticos** (`exercicios/exercicios.md`) — 3 a 9 exercícios em 3 níveis de dificuldade usando o banco de dados da trilha.
3. **Sessão ao vivo** — 2 horas com facilitador. Discussão, demos, exercícios em grupo.
4. **Gabarito** (`exercicios/gabarito.md`) — consulte apenas depois de tentar.

---

## Banco de Dados da Trilha

Todos os exercícios usam o mesmo banco SQLite — uma loja de e-commerce fictícia com 4 tabelas e 3.000 vendas geradas com dados realistas em português.

```bash
python recursos/setup_db.py
```

Tabelas: `clientes`, `produtos`, `categorias`, `vendas`.

---

## Pré-requisitos

- Lógica de programação básica (variáveis, loops, condicionais)
- Familiaridade com terminal/linha de comando
- Python instalado (3.10+) com pip

Não é necessário ter experiência prévia com SQL, pandas ou banco de dados.

---

## Carga Horária Estimada

| Componente | Por módulo | Total (9 módulos) |
|------------|-----------|-------------------|
| Conteúdo assíncrono | 3–5h | ~36h |
| Exercícios | 3–5h | ~36h |
| Sessão ao vivo | 2h | ~18h |
| **Total** | **8–12h** | **~90h** |

---

## Recomendação de Ritmo

Um módulo por semana é o ritmo recomendado. Isso dá tempo de:
- Ler o conteúdo no início da semana
- Tentar os exercícios ao longo da semana
- Participar da sessão ao vivo no final da semana
- Consultar o gabarito e consolidar antes do próximo módulo
