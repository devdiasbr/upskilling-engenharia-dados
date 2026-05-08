# Módulo 6 — Exercícios

---

## Exercício 6.1 — Modelar Dependências (DAG no papel)

**Objetivo:** Praticar a modelagem de um pipeline antes de escrever qualquer código.

### Contexto

Você precisa construir um pipeline de vendas que processa dados de três fontes diferentes. As tarefas disponíveis são:

| Tarefa | Descrição |
|---|---|
| `extrair_vendas` | Lê a tabela de vendas do banco SQLite |
| `extrair_produtos` | Lê a tabela de produtos do banco SQLite |
| `extrair_clientes` | Lê a tabela de clientes do banco SQLite |
| `transformar` | Cruza as três fontes e calcula métricas de vendas por cliente e produto |
| `validar` | Verifica se os dados transformados atendem às regras de negócio (sem nulos, valores válidos, etc.) |
| `carregar` | Persiste o resultado validado em uma tabela de destino |

### Regras de dependência

1. As três extrações (`extrair_vendas`, `extrair_produtos`, `extrair_clientes`) podem rodar **ao mesmo tempo** — elas são independentes entre si.
2. `transformar` só pode iniciar quando **as três extrações** tiverem terminado com sucesso.
3. `validar` só pode iniciar quando `transformar` tiver terminado com sucesso.
4. `carregar` só pode iniciar quando `validar` tiver terminado com sucesso.

### Tarefa

**Desenhe o DAG em formato ASCII** representando as tarefas e suas dependências.

O diagrama deve deixar claro quais tarefas rodam em paralelo e quais são sequenciais. Use setas (`──►`) para indicar dependências.

> Dica: comece identificando quais tarefas não têm pré-requisitos. Essas são as que iniciam o pipeline.

---

## Exercício 6.2 — DAG com Airflow

**Objetivo:** Implementar o DAG modelado no Ex 6.1 usando Apache Airflow.

### Contexto

Use as funções ETL que você desenvolveu no Módulo 5 como `python_callable` das tarefas. Se não tiver as funções do Módulo 5, crie stubs (funções que apenas imprimem uma mensagem e retornam).

### Requisitos

Implemente um arquivo `dag_vendas.py` com o DAG do pipeline de vendas atendendo às seguintes configurações:

1. **`dag_id`**: `pipeline_vendas_completo`
2. **Agendamento**: todos os dias às 7h da manhã
3. **Retentativas**: 2 tentativas em caso de falha
4. **Intervalo entre tentativas**: 10 minutos
5. **`catchup`**: desativado (não reprocessar datas passadas)
6. **Dependências**: exatamente as modeladas no Ex 6.1 — três extrações em paralelo convergindo para transformar → validar → carregar

### Estrutura esperada do arquivo

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Suas funções ETL (ou stubs)
def extrair_vendas():
    ...

def extrair_produtos():
    ...

def extrair_clientes():
    ...

def transformar():
    ...

def validar():
    ...

def carregar():
    ...

# Definição do DAG
with DAG(...) as dag:
    # suas tarefas e dependências aqui
```

> Dica: para definir que `transformar` depende das três extrações simultâneas, use a sintaxe `[lista_de_tarefas] >> tarefa_seguinte`.

---

## Exercício 6.3 — Git na Prática

**Objetivo:** Praticar o fluxo de versionamento de código de pipeline com Git.

### Contexto

Você acabou de escrever a função de validação do Ex 6.2 e quer versionar esse trabalho de forma profissional.

### Passos

Execute a seguinte sequência de comandos no terminal, **dentro do diretório do seu projeto**. Anote o resultado de cada passo.

**Passo 1 — Verificar o estado do repositório:**
```bash
git status
```
O que o comando retorna? O projeto já tem um repositório git? Há arquivos não rastreados?

**Passo 2 — Criar uma nova branch para o seu trabalho:**
```bash
git checkout -b feat/adicionar-validacao
```
Por que criamos uma branch em vez de trabalhar diretamente na `main`?

**Passo 3 — Adicionar a função de validação ao pipeline**

Abra o arquivo do pipeline (ex.: `dag_vendas.py`) e adicione ou melhore a função `validar()`. Por exemplo:

```python
def validar(ti):
    dados = ti.xcom_pull(task_ids='transformar')
    if dados is None or len(dados) == 0:
        raise ValueError("Transformacao retornou conjunto vazio")
    print(f"Validacao concluida: {len(dados)} registros aprovados")
    return dados
```

**Passo 4 — Verificar o que mudou:**
```bash
git diff
```

**Passo 5 — Adicionar o arquivo ao staging e fazer o commit:**
```bash
git add dag_vendas.py
git commit -m "feat: adiciona validacao de registros vazios apos transformacao"
```

**Passo 6 — Verificar o histórico:**
```bash
git log --oneline
```

### Questão de reflexão

Por que é importante versionar o código do pipeline no repositório em vez de manter apenas no servidor do Airflow? Escreva 2 a 3 frases respondendo essa pergunta.
