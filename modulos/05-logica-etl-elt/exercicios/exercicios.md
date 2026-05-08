# Módulo 5 — Exercícios

---

## Exercício 5.1 — ETL vs ELT: Classificação de Cenários

Para cada cenário abaixo, indique se você usaria **ETL** ou **ELT** e justifique sua escolha em 2 a 4 frases. Considere: onde a transformação acontece, quem tem capacidade para processá-la e quais restrições existem.

---

**Cenário A**

Uma empresa usa **Snowflake** como data warehouse. O time de engenharia quer ingerir logs brutos de acesso de usuários (cliques, navegação, tempo de sessão) para criar relatórios de comportamento de produto. O volume é de ~50 GB por dia e o Snowflake tem créditos de computação disponíveis.

> Qual abordagem você usaria? Por quê?

---

**Cenário B**

Um **sistema legado** hospitalar exporta diariamente um CSV com dados de pacientes — nome, CPF, diagnóstico e medicação. Esses dados precisam ser **anonimizados** (substituir CPF por hash, remover nome) antes de qualquer armazenamento, por exigência da LGPD. O dado original não pode tocar o data warehouse em hipótese alguma.

> Qual abordagem você usaria? Por quê?

---

**Cenário C**

Uma **startup** com 3 pessoas no time de dados usa **BigQuery** como destino. Eles querem criar um pipeline simples de vendas: ler um banco PostgreSQL de produção, calcular receita por categoria e disponibilizar para o time de negócio. Simplicidade e velocidade de entrega são prioridade. O volume é pequeno (~10 mil vendas/mês).

> Qual abordagem você usaria? Por quê?

---

## Exercício 5.2 — Extração Incremental

### Objetivo

Implementar e simular uma extração incremental usando o banco `recursos/dados.db`.

### Parte A — A função de extração

Escreva a função `extrair_incremental(conn, ultima_execucao)` que:

- Recebe uma conexão SQLite aberta e uma string de data no formato `'YYYY-MM-DD'`
- Retorna um DataFrame com vendas cuja `data_venda` seja **posterior** à data informada
- Exibe quantos registros foram encontrados

Teste sua função com as seguintes chamadas:

```python
import sqlite3

caminho_db = "recursos/dados.db"

with sqlite3.connect(caminho_db) as conn:
    # Deve retornar registros de julho/2023 em diante
    df_1 = extrair_incremental(conn, "2023-06-30")
    print(f"Execução 1: {len(df_1)} registros")
    print(f"Período: {df_1['data_venda'].min()} a {df_1['data_venda'].max()}")
```

### Parte B — Simulando duas execuções

Simule um pipeline que:

1. Na **primeira execução**, extrai registros após `2023-09-30` e salva a maior `data_venda` encontrada como ponto de controle
2. Na **segunda execução**, lê o ponto de controle e extrai apenas os registros posteriores

Ao final, mostre:
- Quantos registros foram encontrados em cada execução
- Que as datas das duas execuções não se sobrepõem (sem duplicatas)

### Perguntas para reflexão

- O que acontece se o pipeline falhar após a extração mas antes de salvar o ponto de controle?
- O que acontece se o pipeline falhar após salvar o ponto de controle mas antes de concluir a carga?
- Qual das duas situações é mais problemática para a integridade dos dados?

---

## Exercício 5.3 — Pipeline Idempotente

### Objetivo

Criar um pipeline ETL completo e idempotente que possa ser reexecutado com segurança.

### O que fazer

Crie o arquivo `exercicios/etl_idempotente.py` com um pipeline que:

1. **Extrai** todas as vendas do `recursos/dados.db`
2. **Transforma**:
   - Remove duplicatas por `venda_id`
   - Remove linhas com `quantidade` nula ou zero (não é possível calcular valor_unitario)
   - Remove linhas com `valor_total` nulo
   - Converte `data_venda` para datetime
   - Calcula a coluna `valor_unitario = valor_total / quantidade`
3. **Carrega** o resultado em `saida/vendas_processadas.parquet`

### Requisito de idempotência

Execute o pipeline 3 vezes:

```bash
python exercicios/etl_idempotente.py
python exercicios/etl_idempotente.py
python exercicios/etl_idempotente.py
```

Após cada execução, verifique que o arquivo `saida/vendas_processadas.parquet` tem o mesmo número de linhas e os mesmos dados. A terceira execução deve produzir exatamente o mesmo resultado que a primeira.

**Dica:** Qual estratégia de carga garante isso? Por quê `if_exists="append"` quebraria a idempotência?

### Verificação

Adicione ao final do script uma verificação que lê o arquivo salvo e imprime o número de linhas — deve ser sempre o mesmo número, independente de quantas vezes você executou.

---

## Exercício 5.4 — Tratamento de Erros e Logging

### Objetivo

Evoluir o pipeline do Exercício 5.3 adicionando logging estruturado, tratamento de erros e um resumo de execução.

### O que adicionar ao `etl_idempotente.py`

**1. Configuração de logging**

Configure o `logging` para:
- Formato: `%(asctime)s | %(levelname)s | %(message)s`
- Saída simultânea para terminal (`stdout`) e para `saida/pipeline.log`

**2. Logs de etapa**

Cada função (extrair, transformar, carregar) deve logar:
- Início com os parâmetros relevantes
- Fim com a quantidade de linhas resultantes

**3. Captura de erros sem silenciamento**

Use `try/except` em cada etapa. No bloco `except`:
- Logue o erro com `logger.error()`
- Faça `raise` — não silencia o erro

**4. Resumo final**

Ao final de uma execução bem-sucedida, imprima um resumo:
```
=== RESUMO DA EXECUÇÃO ===
Linhas lidas:          3000
Linhas após limpeza:   2990
Linhas salvas:         2990
Linhas descartadas:    10 (0.3%)
Duração:               0.4s
```

**5. Alerta de qualidade**

Se mais de **5%** das linhas forem descartadas durante a limpeza, registre um `WARNING`:
```
AVISO: 6.2% das linhas foram descartadas — verifique a qualidade dos dados de entrada
```

### Simulando uma falha

Para testar o tratamento de erros, modifique temporariamente o caminho do banco:

```python
# Altere para um caminho inválido e execute
caminho_db = "recursos/dados_inexistente.db"
```

Verifique que:
- O erro aparece no log com contexto claro
- O script termina com código de saída 1 (falha) — use `sys.exit(1)`
- O arquivo de saída **não é sobrescrito** com dados inválidos
