# Módulo 6 — Engenharia de Pipelines

## Objetivos

Ao final deste módulo, você será capaz de:

1. **Explicar o que é orquestração** e por que scripts executados manualmente não são suficientes em ambientes de produção.
2. **Diferenciar as principais ferramentas** de orquestração: Apache Airflow, Prefect e Databricks Workflows — entendendo quando usar cada uma.
3. **Modelar dependências entre tarefas** de um pipeline usando DAGs (Directed Acyclic Graphs), incluindo padrões sequenciais e paralelos.
4. **Configurar retentativas e alertas básicos** para tornar pipelines resilientes a falhas transientes.
5. **Usar Git com um fluxo básico de branches e commits** para versionar código de pipelines de dados de forma profissional.

## Pré-requisitos

- Módulo 1 — Fundamentos de SQL
- Módulo 2 — Modelagem de Dados
- Módulo 3 — Formatos de Dados
- Módulo 4 — Python para Dados
- Módulo 5 — Lógica ETL/ELT

Os alunos devem ser capazes de escrever scripts Python de extração, transformação e carga antes de iniciar este módulo.

## Duração estimada

**8 a 10 horas** (incluindo leitura, exercícios e sessão ao vivo)

| Atividade | Tempo estimado |
|---|---|
| Leitura do conteúdo | 3–4 horas |
| Exercícios práticos | 3–4 horas |
| Sessão ao vivo | 2 horas |

## Estrutura do módulo

```
06-engenharia-pipelines/
├── README.md           ← este arquivo
├── conteudo.md         ← material de leitura com teoria e exemplos
├── sessao-ao-vivo.md   ← roteiro da sessão ao vivo
└── exercicios/
    ├── exercicios.md   ← enunciados dos exercícios
    └── gabarito.md     ← soluções comentadas
```

## Como usar este módulo

1. Leia `conteudo.md` do início ao fim antes de iniciar os exercícios.
2. Tente resolver cada exercício por conta própria antes de consultar o gabarito.
3. Participe da sessão ao vivo com o Ex 6.1 já resenhado no papel.
4. O banco SQLite em `recursos/dados.db` é o mesmo usado nos módulos anteriores.
