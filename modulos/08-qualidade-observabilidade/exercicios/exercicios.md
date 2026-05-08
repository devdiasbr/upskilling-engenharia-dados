# Módulo 8 — Exercícios

---

## Exercício 8.1 — Identificar Problemas de Qualidade

### Objetivo

Dado um DataFrame com dados problemáticos, identificar qual dimensão de qualidade cada problema viola e como tratá-lo.

### O dataset

```python
import pandas as pd

df = pd.DataFrame({
    "venda_id":   [101, 102, 103, 103, 104, 105, 106],
    "cliente_id": [10,  20,  30,  30,  None, 50,  60],
    "produto_id": [1,   2,   3,   3,   4,   999, 6],
    "quantidade": [2,   1,   3,   3,   0,   1,   2],
    "data_venda": ["2024-01-10", "2024-01-11", "2024-01-12",
                   "2024-01-12", "2024-01-13", "2024-01-14", "32-13-2024"],
    "valor_total": [100.0, 80.0, 150.0, 150.0, 60.0, 90.0, -40.0],
})

# Para referência: IDs válidos de produto no catálogo
produtos_validos = {1, 2, 3, 4, 5, 6, 7, 8}
```

### O que fazer

Para cada problema identificado no DataFrame acima, preencha a tabela abaixo:

| # | Linha(s) afetada(s) | Descrição do problema | Dimensão violada | Como tratar |
|---|---|---|---|---|
| 1 | ? | ? | ? | ? |
| 2 | ? | ? | ? | ? |
| 3 | ? | ? | ? | ? |
| 4 | ? | ? | ? | ? |
| 5 | ? | ? | ? | ? |
| 6 | ? | ? | ? | ? |

**Dica:** existem pelo menos 6 problemas distintos no DataFrame. Cada um viola uma dimensão diferente (ou a mesma dimensão em campos diferentes).

### Perguntas para reflexão

1. Qual dos problemas você considera mais grave para um pipeline de faturamento? Por quê?
2. Para o problema da `data_venda` inválida: o que `pd.to_datetime(df["data_venda"], errors="coerce")` faz? É suficiente como tratamento?
3. O `produto_id = 999` não existe no catálogo. Isso é um problema que pode ser detectado automaticamente em um pipeline? Como?

---

## Exercício 8.2 — Validações em Pipeline

### Objetivo

Escrever uma função de validação completa que encapsula múltiplas verificações de qualidade.

### O que implementar

Crie a função `validar_dataframe(df)` que verifica as seguintes condições — nessa ordem — e levanta `ValidacaoError` com uma mensagem descritiva se qualquer condição falhar:

1. **Schema**: o DataFrame deve conter as colunas `venda_id`, `cliente_id`, `produto_id`, `quantidade`, `data_venda` e `valor_total`
2. **Unicidade**: `venda_id` não deve ter duplicatas
3. **Completude de `cliente_id`**: nenhum valor nulo permitido (tolerância = 0%)
4. **Completude de `produto_id`**: nenhum valor nulo permitido (tolerância = 0%)
5. **Valor total**: `valor_total` deve ser >= 0 em todas as linhas
6. **Quantidade**: `quantidade` deve ser > 0 em todas as linhas

### Estrutura esperada

```python
class ValidacaoError(Exception):
    pass


def validar_dataframe(df: pd.DataFrame) -> None:
    """
    Valida um DataFrame de vendas.

    Levanta ValidacaoError com mensagem descritiva se qualquer
    validação falhar. Não modifica o DataFrame.

    Parâmetros
    ----------
    df : DataFrame com colunas de vendas
    """
    # sua implementação aqui
    ...
```

### Casos de teste (não usar pytest aqui — só assert manual)

Teste sua implementação com os cenários abaixo. Cada `assert` deve passar sem erros:

```python
import pandas as pd

# Caso 1 — DataFrame válido não deve levantar exceção
df_valido = pd.DataFrame({
    "venda_id": [1, 2, 3],
    "cliente_id": [10, 20, 30],
    "produto_id": [100, 200, 300],
    "quantidade": [1, 2, 3],
    "data_venda": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "valor_total": [50.0, 100.0, 75.0],
})
try:
    validar_dataframe(df_valido)
    print("Caso 1 OK — nenhuma exceção levantada")
except ValidacaoError as e:
    print(f"FALHOU: {e}")

# Caso 2 — coluna ausente deve levantar ValidacaoError
df_sem_coluna = df_valido.drop(columns=["valor_total"])
try:
    validar_dataframe(df_sem_coluna)
    print("FALHOU — deveria ter levantado ValidacaoError")
except ValidacaoError as e:
    print(f"Caso 2 OK — {e}")

# Caso 3 — duplicata em venda_id deve levantar ValidacaoError
df_duplicata = df_valido.copy()
df_duplicata = pd.concat([df_duplicata, df_duplicata.iloc[[0]]], ignore_index=True)
try:
    validar_dataframe(df_duplicata)
    print("FALHOU — deveria ter levantado ValidacaoError")
except ValidacaoError as e:
    print(f"Caso 3 OK — {e}")

# Caso 4 — valor_total negativo deve levantar ValidacaoError
df_negativo = df_valido.copy()
df_negativo.loc[0, "valor_total"] = -10.0
try:
    validar_dataframe(df_negativo)
    print("FALHOU — deveria ter levantado ValidacaoError")
except ValidacaoError as e:
    print(f"Caso 4 OK — {e}")
```

### Pergunta para reflexão

A função `validar_dataframe` levanta erro na **primeira** validação que falha. Há situações em que seria melhor **coletar todos os erros** e levantá-los de uma vez? Quando cada abordagem é mais útil?

---

## Exercício 8.3 — Testes Unitários com pytest

### Objetivo

Escrever uma suíte de testes pytest para a função `transformar` do Módulo 5, cobrindo casos felizes e casos de erro.

### Pré-requisito

A função `transformar` que você testará tem este comportamento esperado:
- Remove duplicatas por `venda_id` (mantém a primeira ocorrência)
- Remove linhas onde `cliente_id`, `valor_total` ou `quantidade` são nulos
- Remove linhas onde `quantidade <= 0`
- Converte `data_venda` para datetime
- Calcula `valor_unitario = valor_total / quantidade`

### O que criar

Crie o arquivo `exercicios/test_pipeline.py` com:

**1. A função auxiliar `make_df`**

```python
def make_df(**kwargs) -> pd.DataFrame:
    """
    Cria um DataFrame de uma linha com valores padrão válidos.
    Use kwargs para sobrescrever qualquer campo.

    Exemplo:
        make_df()                       # linha padrão válida
        make_df(quantidade=[0])         # testa quantidade inválida
        make_df(venda_id=[1, 1])        # testa duplicata
    """
    # implemente aqui
    ...
```

**2. Pelo menos cinco testes**, cobrindo:

| Teste | Descrição |
|---|---|
| `test_caso_feliz` | DataFrame válido passa sem erro e `valor_unitario` é calculado corretamente |
| `test_remove_duplicatas` | Duas linhas com mesmo `venda_id` resultam em uma linha |
| `test_descarta_valor_total_nulo` | Linha com `valor_total=None` é descartada |
| `test_descarta_quantidade_zero` | Linha com `quantidade=0` é descartada |
| `test_valor_unitario_correto` | `valor_unitario` = `valor_total / quantidade` para valor preciso |

**3. Um teste de integração** (bônus):

```python
def test_integracao_com_banco_temporario():
    """
    Testa extração + transformação com banco SQLite temporário.
    Verifica que o pipeline completo produz o número correto de linhas.
    """
    # Dica: use tempfile.TemporaryDirectory() para criar um banco temporário
    ...
```

### Como executar

```bash
# Instalar pytest
pip install pytest

# Rodar os testes
pytest exercicios/test_pipeline.py -v
```

**Instrução importante:** rode os testes **antes** de implementar `transformar`. Veja os erros vermelhos. Só então implemente. A experiência de ver o teste falhar primeiro é o ponto do exercício.

### Perguntas para reflexão

1. O teste `test_caso_feliz` verifica que `valor_unitario` está correto. Por que `assert resultado["valor_unitario"].iloc[0] == 50.0` pode ser problemático para valores de ponto flutuante? O que usar no lugar?
2. A função `make_df` reduz a duplicação de código nos testes. O que aconteceria com a manutenibilidade dos testes se a função `transformar` adicionasse uma nova coluna obrigatória?
3. Qual a diferença entre um teste que verifica `len(resultado) == 1` versus um que verifica `resultado["venda_id"].iloc[0] == 1`? Quando cada um é mais útil?

---

## Exercício 8.4 — Pipeline com Qualidade Integrada

### Objetivo

Evoluir o pipeline do Módulo 5 adicionando as três camadas de qualidade que você aprendeu neste módulo: validação de entrada, logging estruturado e alerta de descarte.

### O que implementar

Crie `exercicios/pipeline_qualidade.py` com as seguintes adições ao pipeline original:

**1. Validação antes da transformação**

Antes de qualquer transformação, chame `validar_dataframe(df)`. Se a validação falhar, o pipeline deve:
- Registrar o erro no log com contexto completo
- Terminar com `sys.exit(1)`
- **Não** salvar nenhum arquivo de saída (o destino não deve ser sobrescrito com dados ruins)

**2. Log de métricas em cada etapa**

Cada função deve logar:
- Início com parâmetros relevantes (caminho, tabela, etc.)
- Fim com o volume resultante (número de linhas)

Ao final de uma execução bem-sucedida, imprima um resumo estruturado:

```
=== RESUMO DA EXECUÇÃO ===
Linhas extraídas:      3000
Linhas após validação: 3000  (passou em todas as verificações)
Linhas após limpeza:   2985
Linhas salvas:         2985
Descartadas:           15 (0.5%)
Duração:               0.4s
Status:                SUCESSO
```

**3. Alerta se > 5% das linhas forem descartadas**

Se a diferença entre o número de linhas extraídas e o número de linhas salvas for maior que 5%, registre um `WARNING` no log:

```
AVISO: 8.3% das linhas foram descartadas — verifique a qualidade dos dados de entrada
```

### Estrutura do arquivo

```python
"""
pipeline_qualidade.py
Pipeline ETL com validação, logging estruturado e alerta de qualidade.
Módulo 8 — Qualidade e Observabilidade.
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime

import pandas as pd


# ── Configuração de logging ──────────────────────────────────────────────────
# configure aqui


# ── Erro de validação ────────────────────────────────────────────────────────
class ValidacaoError(Exception):
    pass


# ── Validação ────────────────────────────────────────────────────────────────
def validar_dataframe(df: pd.DataFrame) -> None:
    # reutilize a implementação do Exercício 8.2
    ...


# ── Extração ─────────────────────────────────────────────────────────────────
def extrair(caminho_db: str) -> pd.DataFrame:
    ...


# ── Transformação ────────────────────────────────────────────────────────────
def transformar(df: pd.DataFrame) -> pd.DataFrame:
    ...


# ── Carga ────────────────────────────────────────────────────────────────────
def carregar(df: pd.DataFrame, caminho: str) -> None:
    ...


# ── Pipeline principal ───────────────────────────────────────────────────────
def main():
    ...


if __name__ == "__main__":
    main()
```

### Simulando falhas

Teste cada caminho de erro:

```python
# Teste 1 — banco inexistente
# Modifique: caminho_db = "recursos/nao_existe.db"
# Esperado: log de erro + sys.exit(1)

# Teste 2 — dados inválidos (force uma ValidacaoError)
# Modifique: injete um DataFrame com quantidade=0 antes da validação
# Esperado: log "VALIDACAO | falhou" + sys.exit(1)

# Teste 3 — execução normal
# Use: caminho_db = "recursos/dados.db"
# Esperado: resumo impresso + arquivo saida/vendas_processadas.parquet criado
```

### Critério de avaliação

- [ ] Validação acontece antes de qualquer transformação
- [ ] Pipeline termina com `sys.exit(1)` se a validação falhar
- [ ] Arquivo de saída não é sobrescrito se a validação falhar
- [ ] Cada etapa tem log de início e fim com volume
- [ ] Alerta de WARNING é registrado se descarte > 5%
- [ ] Resumo final é impresso após execução bem-sucedida
