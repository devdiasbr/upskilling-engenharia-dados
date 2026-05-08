# Módulo 3 — Formatos de Dados

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:

- Explicar as diferenças entre CSV, JSON, Parquet, Avro e Delta Lake e quando usar cada um
- Escolher o formato adequado para um dado cenário: troca de dados, analytics, streaming ou lakehouse
- Ler e escrever cada formato com Python usando as bibliotecas padrão e pandas
- Entender por que Parquet e Delta Lake são o padrão moderno em pipelines de dados
- Quantificar o impacto de compressão e leitura seletiva de colunas na prática

## Pré-requisitos

Módulos 1 e 2 (obrigatórios). Você precisará saber escrever queries SQL e entender o modelo de dados do banco de referência para os exercícios práticos.

## Duração Estimada

5–7 horas de estudo + exercícios

## Banco de Dados e Arquivos de Referência

Continuamos usando o banco SQLite em `recursos/dados.db` e os exports CSV em `recursos/exports/`. Leia o `recursos/schema.md` para uma referência completa do schema.

Para recriar o banco e os CSVs caso necessário:

```bash
python recursos/setup_db.py
```

Os arquivos disponíveis em `recursos/exports/` são:

| Arquivo | Tamanho aproximado |
|---|---|
| `categorias.csv` | ~120 bytes |
| `produtos.csv` | ~2 KB |
| `clientes.csv` | ~21 KB |
| `vendas.csv` | ~95 KB |

## Estrutura do Módulo

| Arquivo | Descrição |
|---|---|
| `conteudo.md` | Material de leitura com tabela comparativa, exemplos de código e critérios de escolha |
| `exercicios/exercicios.md` | 3 exercícios: conversão de formatos, leitura seletiva e escolha de formato por cenário |
| `exercicios/gabarito.md` | Soluções completas com código Python funcional e justificativas |
| `sessao-ao-vivo.md` | Roteiro para o facilitador da sessão ao vivo de 2 horas |

## Dependências Python

Este módulo requer bibliotecas adicionais além da biblioteca padrão:

```bash
pip install pandas pyarrow
```
