# Módulo 2 — Modelagem de Dados

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:

- Identificar entidades, atributos e relacionamentos em um domínio de negócio
- Aplicar as formas normais 1FN, 2FN e 3FN para estruturar dados relacionais com integridade
- Saber quando e por que desnormalizar um modelo, balanceando integridade com performance
- Desenhar um modelo dimensional com tabela fato e tabelas dimensão
- Reconhecer as diferenças entre star schema e snowflake schema e suas implicações práticas
- Decidir qual abordagem de modelagem — relacional ou dimensional — usar de acordo com o contexto (OLTP vs OLAP)

## Pré-requisitos

Módulo 1 — SQL Fundamentals (obrigatório). Você precisará escrever e interpretar queries SQL para validar os modelos propostos nos exercícios.

## Duração Estimada

8–10 horas de estudo + exercícios

## Banco de Dados

Continuamos usando o banco SQLite em `recursos/dados.db` com as tabelas `categorias`, `produtos`, `clientes` e `vendas`. Leia o `recursos/schema.md` para uma referência completa do schema.

Para recriar o banco caso necessário:

```bash
python recursos/setup_db.py
```

## Estrutura do Módulo

| Arquivo | Descrição |
|---|---|
| `conteudo.md` | Material de leitura com conceitos, exemplos e diagramas ASCII |
| `exercicios/exercicios.md` | 4 exercícios cobrindo normalização, modelagem relacional e dimensional |
| `exercicios/gabarito.md` | Soluções completas com justificativas (consulte só depois de tentar) |
| `sessao-ao-vivo.md` | Roteiro para o facilitador da sessão ao vivo de 2 horas |
