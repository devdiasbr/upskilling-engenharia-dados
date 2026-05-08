# Módulo 6 — Roteiro da Sessão ao Vivo

**Duração total:** 2 horas  
**Formato:** Online (câmera ligada, compartilhamento de tela)  
**Materiais necessários (instrutor):** Airflow rodando localmente ou em ambiente demo, `dag_vendas.py` do gabarito, diagrama ASCII do Ex 6.1

---

## Abertura — 10 minutos

**O que fazer:**
- Boas-vindas e verificação rápida de presença.
- Perguntar ao grupo: "Quem já tentou rodar o Ex 6.1 antes da sessão? Quem tem o diagrama no papel?"
- Contextualizar o módulo: "Nos Módulos 4 e 5 vocês aprenderam a escrever o script. Hoje vamos aprender a colocar esse script para funcionar sozinho, todo dia, sem ninguém precisar apertar um botão."
- Apresentar a agenda dos 120 minutos.

**Mensagem-chave para abrir:**
> "Um pipeline que só roda quando alguém lembra de executar manualmente não é um pipeline de produção — é um lembrete de tarefa. Orquestração é o que transforma código em infraestrutura confiável."

---

## Parte 1 — Demo: A interface do Airflow (15 minutos)

**Objetivo:** Materializar visualmente os conceitos de DAG, tarefa e run antes de escrever código.

**Roteiro:**

1. **Abra o Airflow no navegador** (localhost:8080 ou URL do ambiente demo) e compartilhe a tela.

2. **Mostre a lista de DAGs** — explique que cada linha é um pipeline:
   - "Este é o `pipeline_vendas_completo` que vocês vão construir hoje."
   - Aponte o campo de schedule (`0 7 * * *`) e o status da última run.

3. **Clique no DAG e mostre a aba Graph View:**
   - Aponte cada nó: "este é `extrai_vendas`, este é `transformar`."
   - Aponte as setas: "esta seta significa que `transformar` só começa quando `extrai_vendas`, `extrai_clientes` e `extrai_produtos` terminam."
   - Mostre o paralelismo visualmente: "repare que essas três tarefas ficam no mesmo nível — elas rodam ao mesmo tempo."

4. **Clique em uma run passada** e mostre o log de uma tarefa:
   - "Isso é o que aparece quando você clica em `extrai_vendas` e vai em Logs."
   - Aponte o timestamp, o output do print e o status de sucesso.

5. **Mostre o que acontece quando uma tarefa falha:**
   - Se possível, mostre um log de falha com stack trace.
   - "O Airflow sabe exatamente qual tarefa falhou e tenta de novo automaticamente, porque configuramos `retries: 2`."

**Pergunta para o grupo antes de seguir:**
> "Alguém tem dúvida sobre algum elemento da interface antes de ir para o exercício?"

---

## Parte 2 — Exercício em Grupo: Ex 6.1 e Ex 6.2 ao vivo (75 minutos)

### Fase A — Cada um desenha o DAG no papel (10 minutos)

**O que pedir:**
- "Fechem o conteúdo.md por 10 minutos. Abram os exercicios.md apenas no enunciado do Ex 6.1."
- "Desenhem o DAG no papel (ou em um editor de texto em branco) seguindo as regras de dependência."
- Enquanto espera, circule pelas câmeras / peça que ativem câmera para mostrar o papel.

**Ao fim dos 10 minutos:**
- "Quem quer mostrar o que desenhou?"
- Peça para 2 ou 3 voluntários compartilhar a tela ou descrever o diagrama.
- Aponte diferenças e semelhanças entre as versões.

**Mostre o gabarito do Ex 6.1:**
```
extrair_vendas ────┐
                   │
extrair_clientes ──┼──► transformar ──► validar ──► carregar
                   │
extrair_produtos ──┘
```
- Explique por que as extrações são paralelas.
- Explique por que `transformar` precisa esperar as três.

### Fase B — Implementar juntos o DAG em Airflow (45 minutos)

**O que fazer:**
1. Abra um arquivo `dag_vendas.py` em branco no editor (VS Code ou similar) com a tela compartilhada.
2. **Construa o DAG ao vivo com a turma**, não mostre o gabarito diretamente. Pergunte a cada passo:
   - "Qual deve ser o `dag_id`?"
   - "Qual é a expressão cron para 7h todo dia?"
   - "Quantas retentativas configuramos?"
   - "Como escrevemos a dependência de `transformar` em relação às três extrações?"

3. À medida que constroem, **abra o Airflow e faça o upload/reload do DAG** para mostrar o grafo aparecendo em tempo real.

4. **Discussão sobre XCom** (10 minutos dentro desta fase):
   - "Como as tarefas passam dados umas para as outras? Elas rodam em processos diferentes."
   - Mostre o `ti.xcom_push` e `ti.xcom_pull` no código.
   - Mostre o XCom na interface do Airflow (aba XCom em uma run).

5. **Trigger manual de um run** — clique em "Trigger DAG" na interface e acompanhe ao vivo:
   - Mostre as tarefas mudando de cor (azul = rodando, verde = sucesso, vermelho = falha).
   - Se alguma falhar, mostre como ver o log e o que o erro diz.

### Fase C — Ex 6.3 Git (20 minutos)

**O que fazer:**
1. Compartilhe o terminal e mostre a sequência de comandos do Ex 6.3 ao vivo.
2. Execute cada passo explicando o que está acontecendo:
   ```bash
   git status
   git checkout -b feat/adicionar-validacao
   # (editar o arquivo)
   git diff dag_vendas.py
   git add dag_vendas.py
   git commit -m "feat: adiciona validacao de registros vazios apos transformacao"
   git log --oneline
   ```
3. Peça para a turma executar os mesmos comandos no próprio terminal enquanto você faz ao vivo.
4. Mostre o que acontece se alguém esquecer o `git add` antes do `git commit`.

---

## Fechamento (20 minutos)

### Por que código de pipeline deve viver no repositório (10 minutos)

Abra uma discussão rápida com o grupo:

**Pergunte:** "O que acontece se o servidor do Airflow cair e o código do pipeline não estiver no repositório?"

- Colete 2 ou 3 respostas.
- Complemente: "Perdemos o pipeline. Ninguém sabe o que ele fazia. Não tem histórico de mudanças."

**Pergunte:** "Por que é importante saber qual versão do pipeline estava rodando quando uma anomalia aparece nos dados?"

- Resposta esperada: "Para comparar com a versão anterior e ver o que mudou."

**Mensagem de fechamento:**
> "Código de pipeline é código de produção. O mesmo rigor que você aplica a uma API, aplique ao seu DAG. Branch, commit, PR, revisão — esse fluxo protege o time e os dados."

### Preview do Módulo 7 (5 minutos)

- "No Módulo 7 vamos falar sobre qualidade de dados — como garantir que o que chega no pipeline já está correto antes de transformar."
- "Vamos conhecer ferramentas como Great Expectations e dbt tests."
- "O que vocês aprenderam hoje sobre validação dentro do pipeline vai ser a base para o que veremos lá."

### Encerramento (5 minutos)

- Recap dos 3 pontos principais do módulo:
  1. Orquestração automatiza, ordena e monitora pipelines.
  2. DAGs modelam dependências — paralelismo e sequência têm momentos certos.
  3. Git é obrigatório para código de produção, incluindo pipelines.
- Informar prazo para entrega dos exercícios.
- Abrir espaço para perguntas finais.

---

## Checklist do instrutor (antes da sessão)

- [ ] Airflow rodando no ambiente demo com o DAG de exemplo carregado
- [ ] `dag_vendas.py` com código completo salvo localmente (para referência)
- [ ] Terminal aberto no diretório do projeto com git inicializado
- [ ] `recursos/dados.db` acessível pelo Airflow (ou stub functions prontas)
- [ ] Diagrama ASCII do Ex 6.1 impresso ou em arquivo de texto para projetar
