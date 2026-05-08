# Módulo 5 — Lógica de ETL/ELT

## Objetivos

Ao concluir este módulo, você será capaz de:

- Explicar a diferença entre ETL e ELT e decidir qual abordagem usar em cada contexto
- Identificar e implementar estratégias de extração: full load e incremental
- Aplicar transformações de limpeza, padronização e enriquecimento de dados com pandas
- Implementar estratégias de carga: full replace, append e upsert
- Escrever pipelines idempotentes que podem ser reexecutados com segurança
- Tratar erros de forma estruturada e registrar logs úteis para monitoramento e reprocessamento

## Pré-requisito

Módulos 1, 2, 3 e 4 concluídos. Em especial, o script ETL básico escrito no Módulo 4 é o ponto de partida direto deste módulo.

## Duração estimada

10 a 12 horas (conteúdo + exercícios + sessão ao vivo)

## Banco de dados

Todos os exemplos e exercícios utilizam o banco SQLite localizado em `recursos/dados.db`, com as seguintes tabelas:

- `categorias` — categorias de produtos
- `produtos` — cadastro de produtos com categoria e preço
- `clientes` — cadastro de clientes com cidade e estado
- `vendas` — transações de venda com data, cliente, produto e valor

## Estrutura do módulo

| Arquivo | Descrição |
|---|---|
| `conteudo.md` | Material teórico com exemplos práticos em 6 seções |
| `exercicios/exercicios.md` | Quatro exercícios progressivos |
| `exercicios/gabarito.md` | Soluções completas com código funcional |
| `sessao-ao-vivo.md` | Roteiro da sessão ao vivo de 2 horas |

## Conexão com o Módulo 4

No Módulo 4 você escreveu um script que extrai dados do `dados.db`, aplica transformações com pandas e salva o resultado em Parquet. Você já fez ETL — agora você tem o vocabulário e as ferramentas para fazê-lo de forma robusta, segura e repetível.

## Próximo módulo

Módulo 6 — Orquestração de Pipelines: os pipelines que você estruturar neste módulo serão a base para agendamento, monitoramento e reprocessamento automatizado.
