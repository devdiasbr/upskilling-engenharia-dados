# Módulo 6 — Gabarito

---

## Gabarito — Exercício 6.1

### Diagrama ASCII do DAG

```
extrair_vendas ────┐
                   │
extrair_clientes ──┼──► transformar ──► validar ──► carregar
                   │
extrair_produtos ──┘
```

### Explicação das dependências

**Nível 1 — Extrações em paralelo (sem pré-requisitos):**
- `extrair_vendas`, `extrair_clientes` e `extrair_produtos` iniciam ao mesmo tempo porque não dependem umas das outras. Cada uma lê de uma fonte independente.

**Nível 2 — Fan-in (convergência):**
- `transformar` depende das três extrações. Ela só inicia quando `extrair_vendas`, `extrair_clientes` E `extrair_produtos` concluírem com sucesso. Isso é necessário porque a transformação cruza dados das três fontes — se qualquer uma falhar, o cruzamento seria incompleto.

**Nível 3 — Sequência de garantia de qualidade:**
- `validar` depende de `transformar`. Só faz sentido validar depois que os dados foram transformados.
- `carregar` depende de `validar`. Nunca carregamos dados que não passaram pela validação.

**Por que não colocar validar antes de transformar?**
Porque a validação do Ex 6.1 verifica as regras de negócio sobre os dados já cruzados e calculados. Validar os dados brutos antes da transformação é uma prática diferente (e também recomendada, mas seria uma tarefa separada no início do pipeline).

---

## Gabarito — Exercício 6.2

### dag_vendas.py — Implementação completa com XCom

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sqlite3

# ──────────────────────────────────────────────────────────────
# Funções ETL
# Adaptadas do Módulo 5 para passar dados via XCom entre tarefas
# ──────────────────────────────────────────────────────────────

DB_PATH = "/opt/airflow/recursos/dados.db"  # ajuste o caminho conforme seu ambiente


def extrair_vendas(ti):
    """Extrai todas as vendas do banco SQLite e empurra para o XCom."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_venda, id_cliente, id_produto, quantidade, valor_total, data_venda FROM vendas")
    dados = cursor.fetchall()
    conn.close()
    print(f"Vendas extraídas: {len(dados)} registros")
    ti.xcom_push(key="vendas", value=dados)


def extrair_clientes(ti):
    """Extrai todos os clientes e empurra para o XCom."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente, nome, email, cidade FROM clientes")
    dados = cursor.fetchall()
    conn.close()
    print(f"Clientes extraídos: {len(dados)} registros")
    ti.xcom_push(key="clientes", value=dados)


def extrair_produtos(ti):
    """Extrai todos os produtos e empurra para o XCom."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_produto, nome, categoria, preco_unitario FROM produtos")
    dados = cursor.fetchall()
    conn.close()
    print(f"Produtos extraídos: {len(dados)} registros")
    ti.xcom_push(key="produtos", value=dados)


def transformar(ti):
    """
    Cruza vendas, clientes e produtos para calcular métricas por venda.
    Recebe dados via XCom e empurra o resultado transformado.
    """
    vendas   = ti.xcom_pull(task_ids='extrai_vendas',   key='vendas')
    clientes = ti.xcom_pull(task_ids='extrai_clientes', key='clientes')
    produtos = ti.xcom_pull(task_ids='extrai_produtos', key='produtos')

    # Indexar clientes e produtos por ID para cruzamento eficiente
    idx_clientes = {c[0]: c for c in clientes}
    idx_produtos = {p[0]: p for p in produtos}

    resultado = []
    for venda in vendas:
        id_venda, id_cliente, id_produto, quantidade, valor_total, data_venda = venda
        cliente = idx_clientes.get(id_cliente, (id_cliente, "Desconhecido", "", ""))
        produto = idx_produtos.get(id_produto, (id_produto, "Desconhecido", "", 0))

        resultado.append({
            "id_venda":       id_venda,
            "nome_cliente":   cliente[1],
            "cidade_cliente": cliente[3],
            "nome_produto":   produto[1],
            "categoria":      produto[2],
            "quantidade":     quantidade,
            "valor_total":    valor_total,
            "data_venda":     data_venda,
        })

    print(f"Transformação concluída: {len(resultado)} registros")
    ti.xcom_push(key="transformado", value=resultado)


def validar(ti):
    """
    Verifica regras de negócio sobre os dados transformados.
    Lança ValueError se alguma regra for violada.
    """
    dados = ti.xcom_pull(task_ids='transformar', key='transformado')

    if dados is None or len(dados) == 0:
        raise ValueError("Transformação retornou conjunto de dados vazio")

    erros = []
    for i, registro in enumerate(dados):
        if registro.get("valor_total") is None or registro["valor_total"] < 0:
            erros.append(f"Registro {i}: valor_total inválido ({registro.get('valor_total')})")
        if not registro.get("nome_cliente"):
            erros.append(f"Registro {i}: nome_cliente ausente")
        if not registro.get("data_venda"):
            erros.append(f"Registro {i}: data_venda ausente")

    if erros:
        raise ValueError(f"Validação falhou com {len(erros)} erro(s):\n" + "\n".join(erros[:10]))

    print(f"Validação concluída: {len(dados)} registros aprovados, 0 erros")
    # Passa os dados adiante para a tarefa de carga
    ti.xcom_push(key="validado", value=dados)


def carregar(ti):
    """
    Persiste os dados validados em uma tabela de destino no SQLite.
    Usa INSERT OR REPLACE para garantir idempotência.
    """
    dados = ti.xcom_pull(task_ids='validar', key='validado')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas_processadas (
            id_venda       INTEGER PRIMARY KEY,
            nome_cliente   TEXT,
            cidade_cliente TEXT,
            nome_produto   TEXT,
            categoria      TEXT,
            quantidade     INTEGER,
            valor_total    REAL,
            data_venda     TEXT,
            carregado_em   TEXT
        )
    """)

    from datetime import datetime as dt
    agora = dt.utcnow().isoformat()

    for registro in dados:
        cursor.execute("""
            INSERT OR REPLACE INTO vendas_processadas
            (id_venda, nome_cliente, cidade_cliente, nome_produto, categoria,
             quantidade, valor_total, data_venda, carregado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            registro["id_venda"],
            registro["nome_cliente"],
            registro["cidade_cliente"],
            registro["nome_produto"],
            registro["categoria"],
            registro["quantidade"],
            registro["valor_total"],
            registro["data_venda"],
            agora,
        ))

    conn.commit()
    conn.close()
    print(f"Carga concluída: {len(dados)} registros gravados em vendas_processadas")


# ──────────────────────────────────────────────────────────────
# Definição do DAG
# ──────────────────────────────────────────────────────────────

with DAG(
    dag_id='pipeline_vendas_completo',
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 7 * * *',   # todo dia às 7h
    catchup=False,
    default_args={
        'retries': 2,
        'retry_delay': timedelta(minutes=10),
    },
    tags=['vendas', 'producao'],
) as dag:

    t_extrai_vendas = PythonOperator(
        task_id='extrai_vendas',
        python_callable=extrair_vendas,
    )

    t_extrai_clientes = PythonOperator(
        task_id='extrai_clientes',
        python_callable=extrair_clientes,
    )

    t_extrai_produtos = PythonOperator(
        task_id='extrai_produtos',
        python_callable=extrair_produtos,
    )

    t_transformar = PythonOperator(
        task_id='transformar',
        python_callable=transformar,
    )

    t_validar = PythonOperator(
        task_id='validar',
        python_callable=validar,
    )

    t_carregar = PythonOperator(
        task_id='carregar',
        python_callable=carregar,
    )

    # Dependências: fan-out → fan-in → sequencial
    [t_extrai_vendas, t_extrai_clientes, t_extrai_produtos] >> t_transformar >> t_validar >> t_carregar
```

### Pontos de atenção do gabarito

1. **XCom para passar dados entre tarefas**: cada função recebe `ti` (task instance) como parâmetro e usa `ti.xcom_push` / `ti.xcom_pull`. Isso é necessário porque tarefas em Airflow rodam em processos independentes — não se pode usar variáveis globais.

2. **Idempotência no carregamento**: o uso de `INSERT OR REPLACE` garante que reprocessar o mesmo dia não gera duplicatas. Isso é fundamental para pipelines confiáveis.

3. **`task_id` corresponde ao nome usado em `xcom_pull`**: note que `ti.xcom_pull(task_ids='extrai_vendas', key='vendas')` usa exatamente o `task_id` definido na criação da tarefa.

4. **`tags`**: opcional, mas útil para filtrar DAGs na interface do Airflow quando há muitos pipelines.

---

## Gabarito — Exercício 6.3

### Sequência de comandos comentados

```bash
# Passo 1: Ver o estado atual do repositório
git status
# Saída esperada: lista de arquivos modificados ou "nothing to commit, working tree clean"
# Se retornar "not a git repository", execute: git init

# Passo 2: Criar uma nova branch para isolar o trabalho
git checkout -b feat/adicionar-validacao
# Saída esperada: "Switched to a new branch 'feat/adicionar-validacao'"
# Por que branch? Para não quebrar o código em produção (main) enquanto desenvolvemos.
# A main deve sempre ter código funcionando. O desenvolvimento acontece na branch.

# Passo 3: (editar dag_vendas.py com a função validar melhorada)

# Passo 4: Verificar o que mudou antes de commitar
git diff dag_vendas.py
# Mostra exatamente o que foi adicionado (+) e removido (-) no arquivo.
# Boa prática revisar o diff antes de commitar para não enviar alterações acidentais.

# Passo 5a: Adicionar o arquivo ao staging (área de preparação do commit)
git add dag_vendas.py
# Use "git add ." com cuidado — pode incluir arquivos que não devem ser commitados.
# Prefira adicionar arquivos específicos por nome.

# Passo 5b: Criar o commit com mensagem descritiva
git commit -m "feat: adiciona validacao de registros vazios apos transformacao"
# Saída esperada: "[feat/adicionar-validacao abc1234] feat: adiciona validacao..."
# A mensagem deve explicar O QUE e POR QUE, não apenas o que o código faz tecnicamente.

# Passo 6: Ver o histórico de commits da branch
git log --oneline
# Saída esperada (exemplo):
# abc1234 feat: adiciona validacao de registros vazios apos transformacao
# def5678 feat: cria dag pipeline_vendas_completo
# 9abc012 chore: inicializa estrutura do projeto
```

### Resposta à questão de reflexão

Versionar o código do pipeline no repositório é essencial por três razões. Primeiro, o servidor do Airflow pode falhar, ser reiniciado ou ter sua configuração sobrescrita — sem o repositório, o código se perde sem chance de recuperação. Segundo, o histórico de commits permite entender o que mudou quando um pipeline começa a produzir resultados inesperados: é possível comparar a versão atual com versões anteriores e identificar exatamente o que foi alterado. Terceiro, o repositório serve como ponto único de verdade para a equipe — qualquer engenheiro pode clonar o projeto, entender a lógica do pipeline e rodar localmente, sem depender de acesso ao servidor de orquestração.
