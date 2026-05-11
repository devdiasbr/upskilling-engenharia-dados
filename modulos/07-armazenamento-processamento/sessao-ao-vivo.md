# Módulo 7 — Roteiro da Sessão ao Vivo

**Duração total:** 2 horas
**Formato:** Online (câmera ligada, compartilhamento de tela)
**Materiais necessários (instrutor):** Banco `recursos/dados.db` acessível, gabarito dos exercícios 7.2 e 7.4 abertos em abas separadas, diagrama ASCII pronto para o whiteboard

---

## Abertura — 10 minutos

**O que fazer:**
- Boas-vindas e verificação rápida de presença.
- Perguntar ao grupo: "Quem leu o conteúdo.md antes da sessão? Quem já tentou esboçar o Ex 7.2 no papel?"
- Contextualizar o módulo: "Nos seis módulos anteriores vocês aprenderam a escrever código que move dados. Hoje vamos falar sobre onde esses dados ficam e o que acontece quando o volume cresce além do que uma máquina consegue processar."
- Apresentar a agenda dos 120 minutos.

**Mensagem-chave para abrir:**
> "Um pipeline sem arquitetura é um script com prazo de validade. O código que vocês escreveram no Módulo 5 funciona para 3.000 linhas. A pergunta de hoje é: o que muda quando são 3 bilhões?"

---

## Parte 1 — Diagrama no Whiteboard: DW vs Data Lake vs Lakehouse (20 minutos)

**Objetivo:** Fixar visualmente as três arquiteturas e conectá-las ao pipeline já construído pelo grupo.

**Roteiro:**

1. **Desenhe o diagrama no whiteboard (ou ferramenta de quadro online)** — construa ao vivo com a turma, não mostre pronto.

   Comece com três caixas:
   ```
   ┌────────────────┐   ┌────────────────┐   ┌─────────────────┐
   │  Data Warehouse│   │   Data Lake    │   │   Lakehouse     │
   │                │   │                │   │                 │
   │ schema-on-write│   │ schema-on-read │   │ ACID +          │
   │ dados limpos   │   │ dados brutos   │   │ armazenamento   │
   │ SQL analítico  │   │ formato livre  │   │ barato          │
   │ Snowflake/BQ   │   │ S3/ADLS/GCS    │   │ Delta/Iceberg   │
   └────────────────┘   └────────────────┘   └─────────────────┘
   ```

2. **Conecte ao pipeline do projeto** — pergunte à turma: "O banco SQLite que vocês têm em `recursos/dados.db` seria qual parte dessa arquitetura?" (Resposta esperada: seria a fonte transacional, não faz parte do DW/Lake — é de onde os dados saem.)

3. **Mostre o fluxo completo:**
   ```
   [SQLite - fonte]
         │
         ▼ extração (Módulo 4/5)
   ┌─────────────────────────────────────┐
   │           Data Lake                 │
   │  raw/ ──► trusted/ ──► refined/     │
   └─────────────────────────────────────┘
         │
         ▼ se precisar de BI com SLA
   [Data Warehouse]
   ```

4. **Perguntas para engajar:**
   - "Se o pipeline falhar na metade da transformação, qual zona você olharia primeiro para investigar?" (raw/)
   - "Se o dashboard precisar responder em 2 segundos, você leria de qual zona?" (DW ou refined/ bem particionado)
   - "Se surgir uma lei que exige guardar os dados por 7 anos sem modificação, qual zona garante isso?" (raw/)

5. **Mostre o risco do data swamp** — pergunte: "O que acontece se alguém salvar um arquivo em `refined/` sem seguir a convenção de nomenclatura?" Deixe a turma responder antes de completar.

---

## Parte 2 — Exercício em Grupo: Ex 7.2 + Ex 7.4 (70 minutos)

### Fase A — Ex 7.2: Zonas do Data Lake (30 minutos)

**Objetivo:** Cada pessoa define a estrutura de pastas do Data Lake do projeto antes de ver o gabarito.

**O que pedir (primeiros 10 minutos):**
- "Fechem o gabarito. Abram apenas o enunciado do Ex 7.2."
- "Sem ver o gabarito, desenhem a árvore de diretórios do Data Lake para o pipeline que vocês construíram nos módulos 4 e 5."
- "Foquem na Parte A: qual arquivo vai em raw/, qual vai em trusted/, qual vai em refined/? Usem nomes realistas."

**Discussão em grupo (20 minutos):**

1. "Quem quer mostrar o que desenhou?" — peça 2 ou 3 voluntários.
2. Compare as versões. Pergunte:
   - "Alguém colocou o CSV de clientes direto em trusted/? Por quê isso seria um problema?"
   - "Onde está o resultado do groupby de receita por mês — trusted/ ou refined/? Qual é o critério?"
3. Mostre o gabarito da Parte A e explique as diferenças em relação ao que a turma propôs.
4. Execute a Parte B coletivamente: "Me dá 3 transformações que justificam a promoção de raw → trusted. Quem quer começar?"

**Ponto de atenção:** É comum a turma querer colocar os dados do banco SQLite direto em trusted/ porque "já estão limpos". Discuta: "Limpos pelo sistema que criou, ou limpos pelo engenheiro de dados que verificou? Na dúvida, raw/ é para o que veio da fonte sem você tocar."

---

### Fase B — Ex 7.4: Leitura de PySpark e tradução para pandas (40 minutos)

**Objetivo:** Desenvolver fluência na leitura de código PySpark sem precisar instalar Spark.

**O que fazer:**

1. **Compartilhe o trecho PySpark do Ex 7.4 na tela** (copie do arquivo de exercícios).

2. **Leitura coletiva — Parte A (10 minutos):**
   - "Sem olhar o gabarito: o que esse pipeline faz? Me digam em uma frase de negócio."
   - Colete respostas antes de revelar. Respostas possíveis do grupo: "agrupa vendas por estado", "encontra as melhores categorias"... direcione para a resposta completa.
   - Revele: "Top 3 categorias por receita em cada estado, a cada mês."

3. **Linha a linha — Parte B (10 minutos):**
   - Percorra o código linha por linha com a tela compartilhada.
   - A cada operação, pergunte: "Como vocês escreveriam isso em pandas?"
   - Monte a tabela do Ex 7.4b coletivamente no whiteboard ou num editor de texto.
   - Destaque a linha do `Window.partitionBy` — "Esta é a parte mais diferente. O que ela faz?"
   - Explique: "Em pandas, o equivalente é um groupby seguido de rank. O Spark abstrai isso com Window functions porque o dado está distribuído — o pandas faz tudo local."

4. **Implementação — Parte C (20 minutos):**
   - "Agora abram o banco `recursos/dados.db` e implementem a versão pandas."
   - Deixe a turma codificar por 15 minutos enquanto você circula (ou fica disponível no chat).
   - Nos últimos 5 minutos, mostre a implementação do gabarito ao vivo e execute para mostrar o resultado.
   - Se o banco não tiver tabela de produtos com coluna `categoria`, adapte: "Vamos simular a categoria como 'Categoria A', 'Categoria B' baseado no produto_id par/ímpar — o que importa é a lógica do ranking."

**Pergunta para encerrar essa fase:**
> "Se eu substituir `.filter(F.col('valor_total') > 0)` por `.filter(F.col('valor_total') > 500)`, o resultado muda de que forma? Alguém quer testar?"

---

## Fechamento — 20 minutos

### "E se tivéssemos 10 bilhões de linhas?" (15 minutos)

Esta é a pergunta central do fechamento. Abra espaço para discussão antes de dar as respostas.

**Faça as perguntas em sequência:**

1. **"O que acontece com o código pandas do Ex 7.4c se rodarmos nos 10 bilhões de linhas?"**
   - Deixe 2 ou 3 pessoas responder.
   - Respostas esperadas: "trava", "fica sem memória", "demora muito".
   - Complemente: "Exatamente. pandas carrega tudo em memória. 10 bilhões de linhas com 6 colunas float são ~480 GB de RAM. Uma máquina comum tem 16–32 GB."

2. **"O código PySpark do exercício resolveria esse problema sem nenhuma mudança?"**
   - Resposta: sim, desde que o cluster tenha recursos suficientes. O código é o mesmo — o que muda é a infraestrutura que o executa.
   - "Este é o poder da abstração: você escreve a lógica uma vez e o motor cuida de distribuir."

3. **"Agora pensando no Data Lake: se os dados estiverem particionados por ano e mês, quantos arquivos o Spark precisaria abrir para calcular o top 3 de dezembro de 2024?"**
   - Resposta: apenas os arquivos da partição `ano=2024/mes=12/` — a maioria dos outros seria ignorada pelo partition pruning.
   - "Particionamento + processamento distribuído = a dupla que torna pipelines escaláveis."

4. **"O que mais precisaria mudar na arquitetura para 10 bilhões de linhas?"**
   - Pergunte antes de responder. Respostas possíveis do grupo: "usar Spark em vez de pandas", "usar Delta Lake em vez de Parquet simples", "usar um DW gerenciado para as queries de BI".
   - Complete com: "A lógica de negócio — o que calcular — não muda. O que muda é a infraestrutura de execução e armazenamento."

### Preview do Módulo 8 (5 minutos)

- "No Módulo 8, o último da trilha, vamos falar sobre qualidade de dados — como garantir que o que entra no pipeline está correto antes de transformar."
- "Vocês vão conhecer Great Expectations e dbt tests — ferramentas que automatizam a verificação de contratos de dados."
- "O particionamento que vocês aprenderam hoje vai aparecer lá: testar uma partição específica é muito mais rápido do que testar o dataset inteiro."

### Recap dos 3 pontos do módulo (fechamento)

1. **DW, Data Lake e Lakehouse** resolvem problemas diferentes. A escolha depende de volume, estrutura dos dados, garantias necessárias e custo.
2. **As zonas do Data Lake** (raw, trusted, refined) não são burocracia — são o que permite investigar problemas, reprocessar dados e confiar no que está em produção.
3. **Processamento distribuído existe** porque dados crescem além do que uma máquina suporta. Spark é o motor que torna isso possível sem reescrever a lógica de negócio.

---

## Checklist do instrutor (antes da sessão)

- [ ] Banco `recursos/dados.db` acessível e testado com a query do Ex 7.3
- [ ] Gabarito dos exercícios 7.2 e 7.4 abertos em abas separadas para referência
- [ ] Trecho PySpark do Ex 7.4 copiado em um arquivo de texto para compartilhar na tela
- [ ] Ferramenta de whiteboard online aberta (Miro, FigJam ou whiteboard do Meet/Teams)
- [ ] Python com pandas e pyarrow instalados para executar o Ex 7.3c ao vivo
- [ ] Diagrama ASCII das três arquiteturas pronto para colar no whiteboard
