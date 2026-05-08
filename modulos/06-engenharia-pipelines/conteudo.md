# Módulo 6 — Engenharia de Pipelines: Conteúdo

---

## Seção 1 — O que é Orquestração

### O problema do script manual

Você terminou o Módulo 5 com um script Python funcional que extrai dados de vendas, transforma e carrega no banco. Ele roda perfeitamente quando você digita `python pipeline_vendas.py` no terminal. Então qual é o problema?

O problema aparece quando esse script precisa rodar **todos os dias às 6h da manhã**, sem que ninguém precise acordar para isso. E quando ele falha às 3h, você precisa ser avisado. E quando a tabela de clientes ainda não terminou de carregar quando o pipeline de vendas começa a rodar, você precisa garantir que ele espere. E quando um parceiro fornece um arquivo CSV com formato errado, você precisa reprocessar apenas aquele passo — não o pipeline inteiro.

Scripts manuais não resolvem esses problemas. Cron jobs simples resolvem o agendamento, mas não as dependências nem as retentativas. É para isso que existe a **orquestração**.

### O que a orquestração resolve

| Problema | Solução via orquestração |
|---|---|
| Executar no horário certo, todo dia | Agendamento com cron ou trigger |
| Garantir a ordem correta das tarefas | Modelagem de dependências (DAG) |
| Reprocessar apenas uma etapa que falhou | Retentativas e reruns granulares |
| Saber o que falhou e por quê | Logs centralizados e notificações |
| Rodar etapas independentes ao mesmo tempo | Execução paralela de tarefas |

### A analogia do maestro

Pense em um pipeline de dados como uma orquestra. Você tem violinos, trompetes, percussão — cada seção independente, com seu próprio ritmo. A música só soa bem quando cada instrumento toca **no momento certo e na ordem certa**.

O orquestrador é o maestro: ele não toca nenhum instrumento, mas decide quando cada um entra. Se um violinista erra, o maestro sabe exatamente quem foi e pode pedir para repetir aquele trecho — sem reiniciar a sinfonia desde o começo.

---

## Seção 2 — Conceitos Fundamentais

### DAG — Directed Acyclic Graph

Um **DAG** (Grafo Dirigido Acíclico) é a estrutura que representa um pipeline. Cada nó é uma tarefa, cada aresta é uma dependência.

- **Dirigido**: a dependência tem sentido. A → B significa "B só começa depois que A terminar".
- **Acíclico**: não há ciclos. B não pode depender de A se A já depende de B (isso causaria deadlock).

Exemplo visual de um DAG simples:

```
extrair_vendas
      |
      v
  transformar
      |
      v
   carregar
```

Exemplo com paralelismo (fan-out/fan-in):

```
extrair_vendas ──┐
                 v
extrair_clientes ─► transformar ──► validar ──► carregar
                 ^
extrair_produtos ─┘
```

As três extrações rodam ao mesmo tempo (paralelismo). `transformar` só começa quando as três terminam.

### Tarefas (Tasks)

Uma **tarefa** é a unidade mínima de trabalho em um pipeline. Boas tarefas têm:

- **Responsabilidade única**: uma tarefa extrai, outra transforma, outra carrega. Nunca tudo junto.
- **Idempotência**: rodar a mesma tarefa duas vezes com os mesmos parâmetros produz o mesmo resultado — sem duplicatas, sem erros.
- **Atomicidade**: ou a tarefa termina completamente, ou falha — sem estados intermediários sujos.

### Agendamento

Orquestradores usam **cron syntax** para definir quando um pipeline deve rodar:

```
 ┌───── minuto (0–59)
 │ ┌───── hora (0–23)
 │ │ ┌───── dia do mês (1–31)
 │ │ │ ┌───── mês (1–12)
 │ │ │ │ ┌───── dia da semana (0–6, domingo=0)
 │ │ │ │ │
 * * * * *
```

Exemplos práticos:

| Expressão | Significado |
|---|---|
| `0 6 * * *` | Todo dia às 6h00 |
| `0 7 * * 1` | Toda segunda-feira às 7h00 |
| `0 */4 * * *` | A cada 4 horas |
| `30 23 * * 5` | Toda sexta-feira às 23h30 |
| `@daily` | Equivalente a `0 0 * * *` |
| `@hourly` | Equivalente a `0 * * * *` |

### Run (execução)

Uma **run** é uma instância do DAG executando. O mesmo DAG pode ter múltiplas runs em histórico — cada dia cria uma nova run. Cada run tem um `execution_date` que identifica o período de dados que está sendo processado.

---

## Seção 3 — Ferramentas Principais

### Tabela comparativa

| Ferramenta | Onde roda | Ponto forte | Complexidade de setup |
|---|---|---|---|
| **Apache Airflow** | Self-hosted ou cloud (MWAA, Cloud Composer) | Ecossistema maduro, milhares de operadores, comunidade enorme | Alta — requer infraestrutura própria |
| **Prefect** | Cloud gerenciada ou self-hosted | API Python moderna, observabilidade nativa, curva de aprendizado menor | Média — mais fácil de começar |
| **Databricks Workflows** | Databricks (cloud) | Integração nativa com Spark, Delta Lake e notebooks | Baixa (se já usa Databricks) — limitada ao ecossistema |

Para este módulo, usaremos **Apache Airflow** por ser o padrão da indústria e a ferramenta mais cobrada em processos seletivos de Engenharia de Dados.

### Apache Airflow — Conceitos básicos

#### Estrutura de um DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

with DAG(
    dag_id='pipeline_vendas',          # identificador único do DAG
    start_date=datetime(2024, 1, 1),   # a partir de quando o DAG pode rodar
    schedule_interval='0 7 * * *',     # todo dia às 7h
    catchup=False,                     # não reprocessar datas passadas
    default_args={
        'retries': 2,                          # tentar 2 vezes em caso de falha
        'retry_delay': timedelta(minutes=10),  # esperar 10min entre tentativas
    }
) as dag:

    t_extrair = PythonOperator(
        task_id='extrair',
        python_callable=extrair        # função Python a executar
    )

    t_transformar = PythonOperator(
        task_id='transformar',
        python_callable=transformar
    )

    t_carregar = PythonOperator(
        task_id='carregar',
        python_callable=carregar
    )

    # Definição das dependências: extrair → transformar → carregar
    t_extrair >> t_transformar >> t_carregar
```

#### Elementos-chave explicados

**`dag_id`**: nome único do DAG no sistema. Use snake_case descritivo.

**`start_date`**: data de início. O Airflow só agenda runs a partir desta data. Importante: não é "quando foi criado", é "a partir de quando faz sentido processar dados".

**`catchup=False`**: sem esse parâmetro, o Airflow tentaria reprocessar todas as runs desde `start_date`. Com `catchup=False`, ele só roda a próxima execução futura.

**`default_args`**: dicionário de configurações que se aplicam a todas as tarefas do DAG. Retries e retry_delay são os mais usados.

**`PythonOperator`**: executa uma função Python. O `python_callable` aponta para a função que será chamada. Existem operadores para BashOperator, EmailOperator, SparkOperator, e muitos outros.

**Operador `>>`**: define dependência. `t_extrair >> t_transformar` significa "t_transformar depende de t_extrair".

---

## Seção 4 — Modelando Dependências

### Sequencial vs Paralelo

**Sequencial** — cada tarefa espera a anterior:

```python
t_a >> t_b >> t_c >> t_d
```

```
A ──► B ──► C ──► D
```

Use quando cada etapa depende do resultado da anterior.

**Paralelo** — tarefas independentes rodam ao mesmo tempo:

```python
t_a >> [t_b, t_c, t_d] >> t_e
```

```
     ┌──► B ──┐
A ───┼──► C ──┼──► E
     └──► D ──┘
```

Use quando as tarefas não têm dependência entre si e os recursos permitem.

### Padrão Fan-out / Fan-in

O padrão mais comum em pipelines de dados reais: múltiplas fontes extraídas em paralelo (fan-out), convergindo em uma única transformação (fan-in).

**Exemplo com 3 fontes de dados:**

```python
t_extrai_vendas    = PythonOperator(task_id='extrai_vendas',    python_callable=extrair_vendas)
t_extrai_clientes  = PythonOperator(task_id='extrai_clientes',  python_callable=extrair_clientes)
t_extrai_produtos  = PythonOperator(task_id='extrai_produtos',  python_callable=extrair_produtos)
t_transformar      = PythonOperator(task_id='transformar',      python_callable=transformar)
t_validar          = PythonOperator(task_id='validar',          python_callable=validar)
t_carregar         = PythonOperator(task_id='carregar',         python_callable=carregar)

# Fan-out: as 3 extrações em paralelo
# Fan-in: transformar só começa quando as 3 terminam
[t_extrai_vendas, t_extrai_clientes, t_extrai_produtos] >> t_transformar >> t_validar >> t_carregar
```

Diagrama resultante:

```
extrai_vendas ────┐
                  v
extrai_clientes ──► transformar ──► validar ──► carregar
                  ^
extrai_produtos ──┘
```

### Boas práticas de modelagem

- **Granularidade adequada**: tarefas muito grandes são difíceis de monitorar e reprocessar. Tarefas muito pequenas geram overhead de orquestração.
- **Falha isolada**: se uma extração falha, as outras continuam. Só o fan-in é bloqueado.
- **Nomes descritivos**: `task_id='extrai_vendas_diario'` é melhor que `task_id='task_1'`.
- **Evite estado compartilhado via arquivos temporários**: use XCom (mecanismo nativo do Airflow) para passar dados pequenos entre tarefas.

---

## Seção 5 — Git para Código de Dados

### Por que código de pipeline deve viver no repositório

Pipelines de dados são **código de produção**. Um DAG mal versionado é tão perigoso quanto um bug em uma API de pagamento. Guardar o código apenas na máquina local ou no servidor de orquestração é um risco real:

- Se o servidor cair, o código some.
- Se você sair da empresa, ninguém sabe o que o pipeline faz.
- Se algo quebrar, não há histórico para entender o que mudou.

Git resolve todos esses problemas.

### Fluxo básico de trabalho

```
main (branch principal — código em produção)
  │
  ├── feat/adicionar-validacao   ← você trabalha aqui
  │     commits, testes, ajustes
  │
  └── Pull Request → revisão → merge → main
```

### Comandos essenciais com exemplos reais

**Inicializar repositório (apenas uma vez por projeto):**
```bash
git init
git remote add origin https://github.com/seu-usuario/pipelines-dados.git
```

**Ver o estado atual:**
```bash
git status
```

**Criar e mudar para uma nova branch:**
```bash
git checkout -b feat/adicionar-validacao
# ou com git moderno:
git switch -c feat/adicionar-validacao
```

**Adicionar arquivos modificados ao staging:**
```bash
git add modulos/06-engenharia-pipelines/dag_vendas.py
# ou adicionar todos os arquivos modificados (use com cuidado):
git add .
```

**Criar um commit:**
```bash
git commit -m "feat: adiciona validacao de schema antes do carregamento"
```

**Enviar para o repositório remoto:**
```bash
git push origin feat/adicionar-validacao
```

**Ver histórico de commits:**
```bash
git log --oneline
```

### Mensagens de commit descritivas

Use o padrão **Conventional Commits**:

| Prefixo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade ou nova tarefa no pipeline |
| `fix:` | Correção de bug |
| `refactor:` | Reestruturação de código sem mudança de comportamento |
| `chore:` | Tarefas de manutenção (atualizar dependências, etc.) |
| `docs:` | Alterações apenas em documentação |

Exemplos reais:

```
feat: adiciona extração paralela de clientes e produtos
fix: corrige fuso horário no schedule_interval do DAG de vendas
refactor: extrai função de validacao para modulo separado
chore: atualiza versao do apache-airflow para 2.8.0
```

Mensagens ruins (evite):

```
update
fix bug
changes
wip
```

### O arquivo `.gitignore` para projetos de dados

Sempre crie um `.gitignore` para evitar versionar arquivos sensíveis ou desnecessários:

```
# Credenciais e configurações locais
.env
credentials.json
airflow.cfg

# Cache e artefatos Python
__pycache__/
*.pyc
.venv/

# Dados (versione apenas amostras pequenas)
*.csv
*.parquet
dados/raw/
dados/processed/

# Logs locais
logs/
*.log
```
