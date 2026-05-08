# Módulo 4 — Roteiro da Sessão ao Vivo (2h)

---

## Estrutura da sessão

| Bloco | Duração | Atividade |
|---|---|---|
| Abertura e dúvidas | 10 min | Revisão do conteúdo assíncrono |
| Bloco conceitual | 15 min | "A estrutura do Ex 4.3 é um ETL" |
| Exercício em grupo | 75 min | Apresentação e discussão dos pipelines |
| Fechamento | 20 min | Síntese, conexão com Módulo 5, próximos passos |

---

## Bloco 1 — Abertura e dúvidas (10 min)

**Objetivo**: identificar o que ficou menos claro no conteúdo assíncrono antes de avançar.

**Condutor pergunta ao grupo:**

- Alguma dúvida sobre a leitura com `pd.read_sql`?
- Alguém encontrou algum problema ao rodar o script de exemplo?
- O `groupby + agg` ficou claro? Alguma confusão com `reset_index`?

Anote as dúvidas que aparecerem com mais frequência — elas guiam o bloco conceitual.

---

## Bloco 2 — Bloco conceitual: "A estrutura do Ex 4.3 é um ETL" (15 min)

**Objetivo**: conectar o que o aluno já fez com o conceito formal de ETL e preparar o terreno para o Módulo 5.

### Roteiro de fala

Pedir que alguém descreva o que o `pipeline.py` faz em uma frase.

Resposta esperada: "lê do banco, transforma e salva em arquivo".

Escrever no quadro/slide:

```
EXTRAIR  →  TRANSFORMAR  →  CARREGAR
  (banco)      (pandas)       (parquet)
```

Pontuar:

1. **Extrair**: qualquer fonte de dados — banco relacional, API, arquivo CSV, planilha. O que muda é o conector; a estrutura permanece.

2. **Transformar**: aqui vivem as regras de negócio. É onde o analista/engenheiro agrega valor. As funções que vocês escreveram (`receita_por_categoria`, `receita_por_estado`) são transformações.

3. **Carregar**: o destino pode ser um arquivo local (como fizemos), um data warehouse, um bucket na nuvem, ou outra tabela no banco. O que importa é que o resultado seja persistido de forma confiável.

**Perguntar ao grupo:**

- Se o banco fosse uma API REST em vez de SQLite, o que mudaria no código?
  - Resposta esperada: apenas a função `extrair_vendas` — o restante permanece igual. Essa é a força de separar responsabilidades.

- Se precisássemos rodar esse script todo dia às 6h da manhã, o que precisaríamos?
  - Resposta esperada: agendamento, monitoramento, tratamento de erros. Isso é exatamente o Módulo 5.

**Conectar com o Módulo 5:**

> "O que vocês construíram hoje é um pipeline artesanal — funcional, mas manual. No Módulo 5, vamos aprender a orquestrar esse mesmo padrão: agendar, monitorar, tratar falhas e escalar."

---

## Bloco 3 — Exercício em grupo: apresentação dos pipelines (75 min)

**Objetivo**: expor diferentes abordagens para o mesmo problema, identificar variações de qualidade e consolidar aprendizado através da discussão.

### Dinâmica

Dividir o grupo em duplas ou trios. Cada grupo apresenta seu `pipeline.py` por 5–7 minutos, mostrando:

1. Como organizou as funções
2. Como rodou o script e qual foi a saída
3. Uma coisa que acharam difícil ou que teriam feito diferente

### Pontos de discussão para o condutor

Após cada apresentação, levantar pelo menos um dos seguintes pontos:

**Sobre estrutura:**
- Há funções fazendo mais de uma coisa ao mesmo tempo? Como separar?
- O nome das funções comunica bem o que elas fazem?
- Se fosse preciso adicionar um terceiro agregado (por exemplo, receita por produto), o quanto de código seria reescrito?

**Sobre robustez:**
- O script quebra se o banco não existir no caminho informado? Como tratar?
- O diretório `saida/` é criado automaticamente? (Mostrar o `os.makedirs` com `exist_ok=True`)

**Pergunta central do bloco — lançar para todo o grupo:**

> "O que acontece se a coluna `valor_total` vier com valores nulos para algumas vendas?"

Deixar o grupo discutir por 5 minutos antes de mostrar a resposta do gabarito. Pontos esperados na discussão:

- O pandas não quebra — `sum` ignora NaN por padrão
- Mas a contagem (`qtd_vendas`) inclui a linha, enquanto a soma não — inconsistência silenciosa
- A decisão de descartar ou preencher com zero depende da regra de negócio
- Documentar a decisão no código é parte do trabalho do engenheiro

**Comparação de abordagens entre os grupos:**

Ao final das apresentações, perguntar:

- Alguém usou `with sqlite3.connect(...)` (context manager)? Qual a diferença para `conn.close()` explícito?
- Alguém adicionou prints intermediários para acompanhar o progresso? Isso é válido — em produção vira logging.
- Alguém tratou os nulos? Como?

---

## Bloco 4 — Fechamento (20 min)

**Objetivo**: consolidar o aprendizado do módulo e criar expectativa para o próximo.

### Síntese dos conceitos (5 min)

Revisar rapidamente no quadro/slide:

- Estruturas Python para dados: listas, dicionários, comprehensions
- Duas formas de ler SQLite: `sqlite3` puro e `pd.read_sql`
- Operações pandas essenciais: filtro, merge, groupby, tratamento de nulos
- Funções com responsabilidade única e type hints
- Estrutura ETL: extrair → transformar → carregar

### O que o aluno deve ser capaz de fazer agora (3 min)

- Escrever um script Python que lê de um banco SQLite e processa os dados com pandas
- Organizar transformações em funções reutilizáveis
- Salvar resultados em Parquet
- Reconhecer o padrão ETL e saber onde cada responsabilidade vive

### Conexão com o Módulo 5 (5 min)

> "Vocês têm agora um pipeline funcional. Mas ele roda manualmente, não tem tratamento de erros, e se falhar no meio ninguém sabe. O Módulo 5 — Pipelines de Dados — vai resolver exatamente isso: agendamento, monitoramento, idempotência e orquestração."

Mostrar visualmente que o `pipeline.py` do Ex 4.3 vai ser o ponto de partida do Módulo 5 — não é trabalho descartado.

### Tarefa para o próximo módulo (2 min)

Antes da sessão do Módulo 5:

1. Certifique-se de que seu `pipeline.py` roda sem erros do início ao fim
2. Pense: o que precisaria mudar para rodar esse script automaticamente todo dia?
3. Leia a introdução do Módulo 5

### Encerramento (5 min)

Abrir para perguntas finais. Se sobrar tempo, desafio extra:

> "Como você modificaria o pipeline para aceitar o ano e o trimestre como parâmetros de linha de comando — por exemplo: `python pipeline.py --ano 2024 --trimestre 1`?"

Dica para quem quiser explorar: módulo `argparse` da biblioteca padrão do Python.
