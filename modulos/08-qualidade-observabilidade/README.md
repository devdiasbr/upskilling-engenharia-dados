# Módulo 8 — Qualidade e Observabilidade

## Objetivos

Ao concluir este módulo, você será capaz de:

1. **Definir qualidade de dados** usando cinco dimensões concretas e identificar qual dimensão está sendo violada em um problema real.
2. **Escrever validações em pipelines** — funções que verificam schema, completude, unicidade e valores válidos antes de qualquer transformação ou carga.
3. **Estruturar testes unitários e de integração** para funções de pipeline usando pytest — incluindo casos felizes e casos de erro.
4. **Implementar logging estruturado** que permite reproduzir e diagnosticar problemas em produção sem depender de memória ou suposições.
5. **Definir métricas básicas de monitoramento** para qualquer pipeline de dados — tempo de execução, volume, taxa de erros, freshness e taxa de nulos.

## Pré-requisito

Módulos 1 a 7 concluídos. Em especial, o pipeline ETL construído nos Módulos 4 e 5 é o ponto de partida direto dos exercícios práticos deste módulo.

## Duração estimada

**8 a 10 horas** (incluindo leitura, exercícios e sessão ao vivo)

| Atividade | Tempo estimado |
|---|---|
| Leitura do conteúdo | 3–4 horas |
| Exercícios práticos | 3–4 horas |
| Sessão ao vivo | 2 horas |

## Banco de dados

Todos os exemplos e exercícios utilizam o banco SQLite em `recursos/dados.db`, com as tabelas `vendas`, `clientes`, `produtos` e `categorias` — as mesmas usadas nos módulos anteriores.

## Estrutura do módulo

```
08-qualidade-observabilidade/
├── README.md           ← este arquivo
├── conteudo.md         ← material teórico em 5 seções
├── sessao-ao-vivo.md   ← roteiro da sessão ao vivo de encerramento
└── exercicios/
    ├── exercicios.md   ← quatro exercícios progressivos
    └── gabarito.md     ← soluções completas e comentadas
```

## Como usar este módulo

1. Leia `conteudo.md` do início ao fim antes de iniciar os exercícios.
2. No Exercício 8.3, escreva os testes **antes** de implementar as funções — mesmo que eles falhem primeiro. A experiência de ver o teste vermelho antes de vê-lo verde é o ponto central do exercício.
3. Tente resolver cada exercício por conta própria antes de consultar o gabarito.
4. Participe da sessão ao vivo com o Ex 8.1 já resolvido individualmente.

## Nota de encerramento da trilha

Este é o **último módulo dos fundamentos** da trilha de Engenharia de Dados.

Ao longo dos oito módulos você percorreu o caminho completo: do SQL básico até pipelines testados, observáveis e prontos para produção. Os próximos passos naturais são ferramentas e práticas específicas do mercado — **Great Expectations** e **dbt tests** para qualidade declarativa, **Apache Airflow** e **Prefect** para orquestração avançada, **Monte Carlo** e **Soda** para observabilidade de dados em escala.

Os conceitos que você aprendeu aqui são a base para tudo isso. As ferramentas mudam; o raciocínio fica.
