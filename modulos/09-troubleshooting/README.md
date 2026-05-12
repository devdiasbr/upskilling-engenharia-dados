# Módulo 9 — Troubleshooting em Engenharia de Dados

## Objetivos de Aprendizagem

Ao concluir este módulo, você será capaz de:
- Aplicar uma metodologia sistemática de diagnóstico (reproduzir → isolar → corrigir → prevenir)
- Diagnosticar falhas em pipelines ETL/ELT a partir de logs e mensagens de erro
- Identificar e classificar anomalias em dados usando as 5 dimensões de qualidade
- Analisar planos de execução SQL e identificar gargalos de performance
- Transformar cada problema encontrado em um teste que previne regressão

## Pré-requisitos

Módulos 1 a 8 da trilha — especialmente:
- Módulo 5 (logging e tratamento de erros)
- Módulo 8 (qualidade de dados e TDD)
- Módulo 1 (SQL e EXPLAIN QUERY PLAN)

## Duração Estimada

8–10 horas de estudo + exercícios

## Banco de Dados

Mesmo banco SQLite dos módulos anteriores: `recursos/dados.db`

```bash
python recursos/setup_db.py
```

## Estrutura do Módulo

| Arquivo | Descrição |
|---|---|
| `conteudo.md` | Metodologia de troubleshooting com os três pilares |
| `exercicios/exercicios.md` | 3 exercícios práticos — pipeline, dados e SQL |
| `exercicios/gabarito.md` | Soluções com explicações (consulte só depois de tentar) |
| `sessao-ao-vivo.md` | Roteiro para a sessão ao vivo de 2 horas |
