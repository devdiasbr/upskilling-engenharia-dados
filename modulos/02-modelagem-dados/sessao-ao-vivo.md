# Sessão ao Vivo — Módulo 2: Modelagem de Dados

**Duração total:** 2 horas  
**Formato:** interativo, whiteboard + exercício colaborativo  
**Pré-requisito para participantes:** ter lido o `conteudo.md` antes da sessão

---

## Visão geral do tempo

| Bloco | Duração | Descrição |
|---|---|---|
| Abertura | 10 min | Dúvidas rápidas do conteúdo |
| Conceitual | 20 min | Diagrama ao vivo conectando o schema ao conteúdo |
| Exercício em grupo | 70 min | Ex 2.3 colaborativo — modelo dimensional ao vivo |
| Fechamento | 20 min | Revisão do modelo final + preview Módulo 3 |

---

## Bloco 1 — Abertura (10 min)

**Objetivo:** eliminar dúvidas conceituais antes de entrar no exercício.

### Dinâmica sugerida

Abra com uma pergunta de aquecimento (escolha uma):

> "Sem consultar o material: qual a diferença entre chave primária e chave estrangeira? Me dêem um exemplo concreto do `dados.db`."

> "Na prática, quando você desnormalizaria uma tabela? Me dêem um cenário."

### Pontos de atenção comuns (dúvidas que costumam aparecer)

- **"Qual a diferença entre 2FN e 3FN?"** — A 2FN trata de dependência parcial em relação à PK composta. A 3FN trata de dependência entre atributos não-chave. Elas atacam problemas diferentes, mas o efeito prático é o mesmo: separar em tabelas.

- **"A tabela `clientes` do dados.db viola a 3FN por ter cidade e estado juntos?"** — Boa pergunta! Tecnicamente, `estado` depende de `cidade`, o que seria uma dependência transitiva. Em um sistema de produção com alta variabilidade de localização, sim, extrairíamos para uma tabela de cidades. No nosso contexto de aprendizado, mantemos simplificado. Isso é uma decisão de design, não um erro.

- **"Surrogate key: precisa sempre ser criada no DW?"** — É uma boa prática, mas não obrigatório. O benefício principal é desacoplar o DW das PKs do sistema de origem (que podem mudar, ser reutilizadas ou não ser numéricas).

---

## Bloco 2 — Conceitual: Diagrama ao vivo (20 min)

**Objetivo:** visualizar juntos como o schema atual do `dados.db` se encaixa nos conceitos de modelagem.

### Roteiro do facilitador

**1. Abra o whiteboard (físico ou digital) e desenhe o schema atual.**

Comece com as 4 tabelas e seus campos, sem FK ainda:

```
categorias       produtos          clientes           vendas
----------       --------          --------           ------
categoria_id     produto_id        cliente_id         venda_id
nome             nome              nome               cliente_id
                 categoria_id      email              produto_id
                 preco             cidade             quantidade
                                   estado             data_venda
                                   data_cadastro      valor_total
```

**2. Peça para o grupo identificar as chaves primárias de cada tabela.**

Aguarde respostas. Espera-se: `categoria_id`, `produto_id`, `cliente_id`, `venda_id`.

**3. Pergunte: "Onde estão as chaves estrangeiras?"**

Aguarde e confirme: `produtos.categoria_id`, `vendas.cliente_id`, `vendas.produto_id`.

**4. Desenhe as setas de relacionamento e escreva a cardinalidade:**

```
categorias (1) ──────< (N) produtos
clientes   (1) ──────< (N) vendas
produtos   (1) ──────< (N) vendas
```

**5. Pergunta provocativa ao grupo:**

> "A tabela `vendas` é diferente das outras. O que ela representa que `clientes`, `produtos` e `categorias` não representam?"

Resposta esperada: `vendas` representa um **evento** (algo que aconteceu), enquanto as outras representam **entidades** (coisas que existem). Esse é exatamente o conceito de tabela fato.

**6. Transição para o modelo dimensional:**

> "O que precisaríamos adicionar para tornar esse schema adequado para análise de BI?"

Resposta esperada: uma `dim_tempo` — porque `data_venda` como string não permite filtrar por mês, trimestre ou dia da semana.

Esboce no whiteboard a ideia da `dim_tempo` ao lado de `vendas`.

---

## Bloco 3 — Exercício em grupo: Ex 2.3 ao vivo (70 min)

**Objetivo:** cada participante propõe seu modelo dimensional, a turma discute as divergências e chega num consenso colaborativo.

### Estrutura do bloco

#### Fase 1 — Trabalho individual (20 min)

Peça para cada participante, no papel ou na ferramenta de preferência, esboçar:
- `fato_vendas` com campos e FKs
- `dim_cliente`, `dim_produto`, `dim_tempo` com seus campos

Não há resposta certa única — o objetivo é que cada pessoa tome decisões e saiba justificá-las.

#### Fase 2 — Apresentação e discussão (30 min)

Peça 2–3 voluntários para apresentar seu modelo (2–3 min cada). Para cada apresentação, o facilitador guia uma discussão rápida:

**Perguntas de discussão:**

- "Você incluiu `email` em `dim_cliente`? Faz sentido analítico ter email na dimensão?"
  - Reflexão: email é bom para sistemas transacionais (contato), mas raramente é usado para agrupar/filtrar em análises. Pode ser omitido na dimensão.

- "Você desnormalizou `nome_categoria` em `dim_produto` ou manteve uma FK para `dim_categoria`?"
  - Se desnormalizou: star schema — mais simples para BI.
  - Se manteve FK: snowflake — mais correto formalmente, porém mais JOINs.

- "Quais campos você colocou em `dim_tempo`? Tem `eh_fimdesemana`?"
  - Discutir: `eh_fimdesemana` é um campo calculado mas muito útil para análises de e-commerce (padrão de compra difere entre semana e fim de semana).

- "O `preco` em `dim_produto` — ele muda ao longo do tempo. Onde você guarda o preço que era válido no momento da venda?"
  - Esta pergunta abre a discussão do Slowly Changing Dimension (SCD) — guarde para a pergunta provocativa abaixo.

#### Fase 3 — Modelo consensuado (20 min)

Com base na discussão, desenhe coletivamente o modelo final no whiteboard. O facilitador atua como escriba, incorporando as melhores decisões do grupo.

Modelo de referência (adapte conforme a discussão):

```
fato_vendas
- venda_sk (PK)
- cliente_sk (FK)
- produto_sk (FK)
- tempo_sk (FK)
- quantidade
- valor_total

dim_cliente
- cliente_sk (PK)
- cliente_id
- nome
- cidade
- estado

dim_produto
- produto_sk (PK)
- produto_id
- nome
- nome_categoria (desnormalizado)
- preco

dim_tempo
- tempo_sk (PK)
- data
- dia
- mes
- trimestre
- ano
- dia_da_semana
- eh_fimdesemana
```

### Pergunta provocativa — "e o preço ao longo do tempo?"

Após o modelo estar desenhado, lance a pergunta:

> **"E se quiséssemos rastrear a mudança de preço de um produto ao longo do tempo? O preço em `dim_produto` é o preço atual — mas uma venda de janeiro de 2023 pode ter sido com um preço diferente do atual. Como modelaríamos isso?"**

Deixe a discussão fluir por 5–10 minutos. Conceitos que podem emergir:

- **Opção A — Guardar o preço na fato**: colocar `preco_unitario` em `fato_vendas` (o preço no momento da venda). Simples e eficaz para o caso específico de preço.

- **Opção B — Slowly Changing Dimension (SCD) Tipo 2**: criar múltiplos registros em `dim_produto` para o mesmo produto, cada um com datas de vigência (`data_inicio_vigencia`, `data_fim_vigencia`). Quando o preço muda, o registro atual é "fechado" e um novo é criado.

Não é necessário resolver completamente — o objetivo é plantar a semente de que **dimensões mudam ao longo do tempo** e há técnicas específicas para isso. O Módulo 5 (Pipelines de Dados) ou um módulo dedicado de DW pode aprofundar SCDs.

> Validação para encerrar: o grupo consegue responder à query do item (d) do Ex 2.3 com o modelo que desenharam? Execute mentalmente: "usando apenas o schema atual do `dados.db`, como escreveríamos a query de faturamento por mês?"

---

## Bloco 4 — Fechamento (20 min)

**Objetivo:** consolidar o aprendizado e criar antecipação para o Módulo 3.

### Revisão do modelo final (10 min)

Com o diagrama ainda no whiteboard, faça uma revisão rápida cobrindo os 6 objetivos do módulo:

1. **Entidades, atributos e relacionamentos** — apontou no diagrama ao vivo no Bloco 2
2. **Normalização** — vimos 1FN (atomicidade), 2FN (dependência parcial), 3FN (dependência transitiva) no conteúdo e Ex 2.1
3. **Quando desnormalizar** — `dim_produto` com `nome_categoria` é um exemplo proposital de desnormalização
4. **Modelo dimensional** — `fato_vendas` + `dim_cliente` + `dim_produto` + `dim_tempo`
5. **Star vs Snowflake** — discutido no Ex 2.4 e na discussão do Bloco 3
6. **Quando usar cada modelagem** — OLTP para integridade, OLAP para análise

### Preview do Módulo 3 (5 min)

> "Agora que sabemos **como modelar** dados, no Módulo 3 vamos falar sobre **como mover** esses dados — pipelines de ETL e ELT. Vamos pegar o schema do `dados.db` e simular a carga de dados de um sistema transacional para um data warehouse, criando exatamente as dimensões e a tabela fato que desenhamos hoje."

Pontos para despertar curiosidade:
- "O que acontece quando o sistema de origem muda a PK de um cliente? Como nosso pipeline lida com isso?"
- "ETL vs ELT — qual a diferença e quando cada um faz sentido?"
- "Como garantir que a `dim_tempo` está completa para todos os dias do período, mesmo que não haja vendas em alguns dias?"

### Encerramento (5 min)

- Lembrar que o gabarito está em `exercicios/gabarito.md`
- Recomendar: tentar os exercícios 2.1 e 2.4 (que não foram feitos em grupo) antes do próximo módulo
- Pergunta final para levar para casa: "Olhando o schema do `dados.db`, você consegue identificar qual é o grão da tabela `vendas`? E como esse grão impacta o que podemos analisar?"

---

## Materiais necessários para a sessão

- Whiteboard físico ou digital (Miro, FigJam, Excalidraw)
- Acesso ao `recursos/schema.md` para referência
- Banco `dados.db` disponível para consultas ao vivo (opcional, mas útil)
- Slides com o diagrama do star schema (pode usar o diagrama ASCII do `conteudo.md`)

## Dicas para o facilitador

- **Não corrija imediatamente.** Quando alguém apresentar um modelo "errado", pergunte "por que você fez essa escolha?" antes de comentar. Frequentemente a pessoa chega à conclusão sozinha.
- **A pergunta do preço é deliberadamente sem resposta fácil.** Não resolva completamente — o objetivo é criar tensão produtiva que o próximo módulo vai endereçar.
- **Se o grupo for avançado**, introduza o conceito de SCD Tipo 2 brevemente na discussão do Bloco 3.
- **Se o grupo for iniciante**, foque mais tempo no Bloco 2 (diagrama) e reduza a fase de apresentação individual no Bloco 3.
