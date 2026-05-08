# Módulo 1 — SQL Fundamentals

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Escrever queries para consultar e filtrar dados com SELECT, WHERE, ORDER BY
- Combinar dados de múltiplas tabelas com diferentes tipos de JOIN
- Agregar e sumarizar dados com GROUP BY e funções de agregação
- Usar CTEs para organizar queries complexas
- Usar window functions para cálculos sobre partições de dados
- Identificar e evitar problemas básicos de performance em queries

## Pré-requisitos

Nenhum. Este é o módulo inicial da trilha.

## Duração Estimada

8–12 horas de estudo + exercícios

## Banco de Dados

Usaremos o banco SQLite em `recursos/dados.db`, gerado pelo script `recursos/setup_db.py`.

Para criar o banco antes de começar:

```bash
python recursos/setup_db.py
```

O script usa Faker (pt_BR) com seeds fixas (`random.seed(42)` e `Faker.seed(42)`), garantindo que todos os participantes tenham exatamente os mesmos dados.

Leia o `recursos/schema.md` para entender as 4 tabelas: `categorias`, `produtos`, `clientes` e `vendas`.

## Estrutura do Módulo

| Arquivo | Descrição |
|---|---|
| `conteudo.md` | Material de leitura com exemplos comentados para todas as seções |
| `exercicios/exercicios.md` | 9 exercícios em 3 níveis de dificuldade |
| `exercicios/gabarito.md` | Soluções com explicações (consulte só depois de tentar) |
| `sessao-ao-vivo.md` | Roteiro para o facilitador da sessão ao vivo de 2 horas |
