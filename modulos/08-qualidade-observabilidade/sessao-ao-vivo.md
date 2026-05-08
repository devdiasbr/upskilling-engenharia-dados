# Módulo 8 — Sessão ao Vivo: Roteiro

**Duração total:** 2 horas
**Tipo:** Sessão de encerramento da trilha
**Material necessário:** exercicios.md aberto, gabarito.md fechado até o momento indicado

---

## Abertura — "Alguém já encontrou dado errado em produção?" (10 min)

**Objetivo:** Conectar o conteúdo do módulo com a experiência real dos participantes antes de qualquer apresentação de conceito.

**Como conduzir:**

Comece com a pergunta diretamente, sem introdução:

> "Antes de começar: alguém aqui já encontrou dado errado em produção? Ou soube de um caso? O que aconteceu?"

Deixe a conversa fluir por 5 a 7 minutos. O que costuma surgir:
- Pipeline que rodou e salvou arquivo vazio sem alertar ninguém
- Dashboard de receita com número errado por duplicatas
- Relatório enviado para a diretoria com dados do dia anterior porque o pipeline atrasou

Após as histórias, conecte com o módulo:

> "Tudo que vocês descreveram tem um nome: problema de qualidade de dados. E hoje vamos aprender a detectar, prevenir e monitorar esses problemas antes que cheguem ao usuário final."

**Cuidado:** não deixe essa abertura passar de 10 minutos. Se ninguém compartilhar histórias, passe para a fase seguinte — o conteúdo do Ex 8.1 vai gerar a conversa naturalmente.

---

## Ex 8.1 — Análise Coletiva de Problemas de Qualidade (30 min)

**Objetivo:** Praticar o vocabulário das cinco dimensões identificando problemas reais em um dataset.

### Parte 1 — Trabalho individual (10 min)

Mostre o dataset do Ex 8.1 na tela (ou peça para cada um abrir o exercicios.md):

```python
df = pd.DataFrame({
    "venda_id":   [101, 102, 103, 103, 104, 105, 106],
    "cliente_id": [10,  20,  30,  30,  None, 50,  60],
    "produto_id": [1,   2,   3,   3,   4,   999, 6],
    "quantidade": [2,   1,   3,   3,   0,   1,   2],
    "data_venda": ["2024-01-10", "2024-01-11", "2024-01-12",
                   "2024-01-12", "2024-01-13", "2024-01-14", "32-13-2024"],
    "valor_total": [100.0, 80.0, 150.0, 150.0, 60.0, 90.0, -40.0],
})
```

> "Sem falar com ninguém ainda: identifiquem cada problema que vocês encontrarem. Anotem a linha, o que está errado, e qual das cinco dimensões está sendo violada. Vocês têm 10 minutos."

### Parte 2 — Comparação coletiva (20 min)

Construa a tabela de respostas coletivamente:

> "Quem quer começar? Qual problema vocês identificaram primeiro?"

Vá anotando as respostas na tela. Quando divergências aparecerem (e vão aparecer), explore:

> "Alguém classificou diferente? Por que você escolheu essa dimensão?"

**Ponto de discussão rico:** o `produto_id = 999` costuma gerar debate.
- Alguns classificam como **Acurácia** (o valor não é real)
- Outros classificam como **Consistência** (viola a integridade referencial com a tabela de produtos)

Ambos estão corretos. O ponto é: dimensões não são categorias mutuamente exclusivas — elas destacam aspectos diferentes do mesmo problema.

**Pergunta para encerrar a discussão:**

> "Dos seis problemas, qual vocês considerariam mais urgente para um pipeline de faturamento? Por quê?"

Não há resposta única. O objetivo é forçar a priorização — habilidade essencial quando não é possível corrigir tudo de uma vez.

---

## TDD na Prática — Testes Antes do Código (40 min)

**Objetivo:** Experimentar o ciclo vermelho-verde do TDD com os testes do Ex 8.3.

### Setup (5 min)

Peça para todos abrirem um editor com o arquivo `exercicios/test_pipeline.py` vazio. Mostre na tela a estrutura mínima:

```python
import pandas as pd
import pytest


def transformar(df):
    pass  # ainda não implementado


def make_df(**kwargs):
    defaults = {
        "venda_id":   [1],
        "cliente_id": [10],
        "produto_id": [100],
        "quantidade": [2],
        "data_venda": ["2024-01-15"],
        "valor_total": [100.0],
    }
    defaults.update(kwargs)
    return pd.DataFrame(defaults)
```

> "A função `transformar` não faz nada ainda. Vamos escrever os testes primeiro."

### Fase vermelha (15 min)

Escreva ao vivo, com a turma sugerindo cada teste:

> "Qual é o primeiro comportamento que queremos garantir?"

Escreva o primeiro teste juntos:

```python
def test_caso_feliz():
    df = make_df()
    resultado = transformar(df)
    assert len(resultado) == 1
    assert "valor_unitario" in resultado.columns
```

Execute: `pytest test_pipeline.py -v`

A tela vai mostrar vermelho. Celebre isso:

> "Perfeito. O teste está falhando porque a função não existe ainda. Isso é exatamente o que queremos — agora sabemos que o teste funciona e detecta o problema certo."

Adicione mais 2 a 3 testes seguindo o mesmo padrão (duplicata, nulo, quantidade zero). Execute após cada um — todos vermelhos.

**Ponto pedagógico central:** o estado "todos vermelhos" não é fracasso. É o ponto de partida. O teste que nunca falhou pode nunca ter detectado nada.

### Fase verde (20 min)

> "Agora vamos implementar. O objetivo é fazer cada teste passar, sem escrever mais código do que o necessário."

Implemente `transformar` incrementalmente:

```python
def transformar(df):
    df = df.copy()
    df = df.drop_duplicates(subset=["venda_id"], keep="first")
    df = df.dropna(subset=["cliente_id", "valor_total", "quantidade"])
    df = df[df["quantidade"] > 0]
    df["data_venda"] = pd.to_datetime(df["data_venda"])
    df["valor_unitario"] = df["valor_total"] / df["quantidade"]
    return df.reset_index(drop=True)
```

Execute os testes novamente. Mostre todos verdes na tela.

> "O que mudou? O código — não os testes. Os testes são o contrato. A implementação é como atendemos ao contrato."

**Pergunta para encerrar:**

> "Se alguém alterar a função `transformar` amanhã e remover a linha de deduplicação, o que acontece?"

Resposta: `test_remove_duplicatas` vai falhar imediatamente. Os testes protegem contra regressões.

---

## Fechamento da Trilha (40 min)

**Objetivo:** Consolidar o aprendizado dos oito módulos, celebrar o percurso e orientar os próximos passos.

### Linha do tempo da trilha (10 min)

Mostre o percurso completo:

> "Vamos recapitular o que vocês aprenderam. No Módulo 1, vocês não sabiam o que era um JOIN. Agora vocês estão escrevendo testes para pipelines com validação de qualidade. O que aconteceu no meio?"

Percorra os módulos com a turma:

| Módulo | O que aprendemos | O que ficou permanente |
|---|---|---|
| 1 — SQL | SELECT, JOIN, agregações | A pergunta "o que eu preciso do dado?" |
| 2 — Modelagem | Normalização, entidades, chaves | Como pensar sobre relacionamentos entre dados |
| 3 — Formatos | CSV, JSON, Parquet, compressão | Por que o formato importa para performance |
| 4 — Python | pandas, leitura de arquivos | O DataFrame como ferramenta de análise |
| 5 — ETL/ELT | Extração, transformação, carga | Idempotência, falha explícita, logging |
| 6 — Pipelines | Orquestração, DAGs, versionamento | A diferença entre script e pipeline |
| 7 — Armazenamento | Data Lake, Warehouse, Lakehouse, Spark | Onde os dados vivem e por quê |
| 8 — Qualidade | Validação, testes, observabilidade | Que dado ruim é pior que dado ausente |

### O que fica (10 min)

> "Vocês aprenderam ferramentas específicas — pandas, SQLite, pytest. Essas ferramentas vão mudar. O que não muda:"

- **Pensar em termos de qualidade de dados** — as cinco dimensões se aplicam a qualquer ferramenta
- **Fail fast** — detectar o problema cedo é mais barato do que descobrir tarde
- **Idempotência** — um pipeline que pode ser reexecutado com segurança é um pipeline de produção
- **Logging com contexto** — você vai agradecer às 3h da manhã quando precisar diagnosticar uma falha

### Próximos passos (15 min)

> "Estes foram os fundamentos. O que vem depois?"

Apresente as ferramentas específicas como extensões do que já foi aprendido:

**Qualidade declarativa**
- **Great Expectations**: você define expectativas em Python — `expect_column_to_not_be_null("cliente_id")` — e a ferramenta gera relatórios automáticos. O fundamento: as validações que vocês escreveram hoje.
- **dbt tests**: testes diretamente nos modelos SQL — `not_null`, `unique`, `accepted_values`. O fundamento: o raciocínio sobre unicidade e completude deste módulo.

**Observabilidade em escala**
- **Monte Carlo**: detecta anomalias automaticamente sem configuração — "o volume caiu 40% hoje, isso é anormal". O fundamento: as métricas de monitoramento da Seção 5.
- **Soda**: validações em YAML integradas a qualquer pipeline. O fundamento: as funções `validar_*` que vocês escreveram.

**Orquestração avançada**
- **Apache Airflow** e **Prefect**: o que vocês viram no Módulo 6, em escala de produção.

> "A diferença entre alguém que usa Great Expectations e alguém que entende Great Expectations é ter construído a validação na mão primeiro. Vocês fizeram isso hoje."

### Encerramento (5 min)

> "Oito módulos atrás, vocês começaram com SQL básico. Hoje vocês escreveram um pipeline com validação, logging estruturado, testes unitários e monitoramento. Isso é engenharia de dados."

Deixe espaço para perguntas e comentários sobre a trilha como um todo.

**Pergunta de encerramento (opcional):**

> "Qual foi o módulo mais difícil para vocês? E qual conceito clicou mais?"

Não há resposta certa. O objetivo é encerrar com reflexão — e com a consciência de que o aprendizado continuou ao longo de oito módulos, não em um único dia.

---

## Notas para o facilitador

**Se o Ex 8.1 gerar muita discussão e o tempo apertar:** Priorize a fase vermelha do TDD — ver os testes falhando pela primeira vez é a experiência mais impactante do módulo. O fechamento da trilha pode ser encurtado se necessário.

**Se a turma for pequena (menos de 5 pessoas):** O Ex 8.1 pode ser feito em pares em vez de individualmente, para gerar mais troca.

**Se alguém perguntar "quando usar pytest vs. assert manual":** Pytest é para qualquer coisa que precisa ser executada de forma repetível e integrada a CI/CD. Assert manual (como no Ex 8.2) é para exploração rápida durante o desenvolvimento. Em produção, pytest.

**Sobre a celebração:** Não subestime o valor simbólico de reconhecer o percurso completo. Oito módulos é um compromisso significativo. O fechamento merece mais do que um "obrigado e até mais".
