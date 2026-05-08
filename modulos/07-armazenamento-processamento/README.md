# Módulo 7 — Armazenamento e Processamento

## Objetivos

Ao final deste módulo, você será capaz de:

1. **Diferenciar Data Warehouse, Data Lake e Lakehouse** — entender o que cada arquitetura resolve, seus compromissos e quando cada uma é a escolha certa.
2. **Descrever as zonas de um Data Lake** (raw, trusted, refined) e justificar por que essa separação existe do ponto de vista de governança e rastreabilidade.
3. **Explicar por que processamento distribuído existe** — o que torna um arquivo de 1 TB impossível de processar em uma única máquina e como clusters resolvem esse problema.
4. **Entender os conceitos fundamentais do Apache Spark** sem escrever código Spark — saber o que são RDDs, DataFrames, transformações lazy e actions, e reconhecer um trecho PySpark.
5. **Tomar decisões de particionamento** — escolher a coluna correta para particionar um dataset, escrever dados particionados com pandas e entender como a leitura se beneficia dessa estrutura.

## Pré-requisitos

- Módulo 1 — Fundamentos de SQL
- Módulo 2 — Modelagem de Dados
- Módulo 3 — Formatos de Dados
- Módulo 4 — Python para Dados
- Módulo 5 — Lógica ETL/ELT
- Módulo 6 — Engenharia de Pipelines

Os alunos devem ter experiência com pandas, leitura de arquivos Parquet/CSV e escrita básica de pipelines Python antes de iniciar este módulo.

## Duração estimada

**6 a 8 horas** (incluindo leitura, exercícios e sessão ao vivo)

| Atividade | Tempo estimado |
|---|---|
| Leitura do conteúdo | 2–3 horas |
| Exercícios práticos | 2–3 horas |
| Sessão ao vivo | 2 horas |

## Estrutura do módulo

```
07-armazenamento-processamento/
├── README.md           ← este arquivo
├── conteudo.md         ← material de leitura com teoria e exemplos
├── sessao-ao-vivo.md   ← roteiro da sessão ao vivo
└── exercicios/
    ├── exercicios.md   ← enunciados dos exercícios
    └── gabarito.md     ← soluções comentadas
```

## Como usar este módulo

1. Leia `conteudo.md` do início ao fim. Este módulo é majoritariamente conceitual — não há instalação de novas ferramentas.
2. Use os diagramas e comparações lado a lado para fixar as diferenças entre as arquiteturas.
3. Tente resolver cada exercício por conta própria antes de consultar o gabarito.
4. O banco SQLite em `recursos/dados.db` é usado nos exercícios práticos de particionamento.
5. Participe da sessão ao vivo com o Ex 7.2 (zonas do Data Lake) já esboçado no papel.

## Por que este módulo existe aqui

Nos módulos anteriores você aprendeu a escrever código que lê, transforma e carrega dados. Agora vamos um nível acima: onde esses dados vivem, em qual estrutura eles são organizados e o que acontece quando o volume cresce além do que uma máquina consegue processar. Estas são as decisões de arquitetura que todo engenheiro de dados precisa saber tomar — ou ao menos saber conversar sobre.
