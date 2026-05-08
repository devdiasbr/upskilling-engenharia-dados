# Módulo 4 — Python para Dados

## Objetivos

Ao concluir este módulo, você será capaz de:

- Manipular dados com pandas lendo diretamente de um banco SQLite
- Escrever funções reutilizáveis de transformação com responsabilidade única
- Ler e escrever dados nos formatos CSV, JSON e Parquet
- Estruturar um script Python organizado seguindo o padrão extrair/transformar/carregar
- Automatizar tarefas repetitivas de processamento de dados

## Pré-requisito

Módulos 1, 2 e 3 concluídos. Familiaridade com SQL (JOINs, GROUP BY, filtros) e noções básicas de Python.

## Duração estimada

10 a 15 horas (conteúdo + exercícios + sessão ao vivo)

## Banco de dados

Todos os exemplos e exercícios utilizam o banco SQLite localizado em `recursos/dados.db`, com as seguintes tabelas:

- `categorias` — categorias de produtos
- `produtos` — cadastro de produtos com categoria e preço
- `clientes` — cadastro de clientes com cidade e estado
- `vendas` — transações de venda com data, cliente, produto e valor

## Estrutura do módulo

| Arquivo | Descrição |
|---|---|
| `conteudo.md` | Material teórico com exemplos práticos |
| `exercicios/exercicios.md` | Três exercícios progressivos |
| `exercicios/gabarito.md` | Soluções completas comentadas |
| `sessao-ao-vivo.md` | Roteiro da sessão ao vivo de 2 horas |

## Próximo módulo

Módulo 5 — Pipelines de Dados: o script ETL que você escreverá neste módulo é a base direta do próximo módulo.
