# Exercícios — Módulo 2: Modelagem de Dados

> Tente resolver cada exercício antes de consultar o `gabarito.md`. O valor está no raciocínio, não na resposta certa.

---

## Exercício 2.1 — Identificando e corrigindo violações de normalização

### Cenário

Uma analista de dados recebeu a seguinte tabela de um sistema legado de pedidos:

```
pedidos_legado
+----------+------------------+--------------------------------+----------+-----------+
| pedido_id| cliente          | produtos_comprados             | qtd_total| total_r$  |
+----------+------------------+--------------------------------+----------+-----------+
|   1001   | Ana Lima / SP    | Notebook Pro, Mouse USB        |    2     | 3600.00   |
|   1002   | Carlos Braga / RJ| Livro de Python                |    1     |   89.00   |
|   1003   | Ana Lima / SP    | Camiseta Básica, Tênis Run     |    2     |  309.90   |
|   1004   | Marcos Pinto / MG| Notebook Pro                  |    1     | 3500.00   |
+----------+------------------+--------------------------------+----------+-----------+
```

### Tarefas

**(a)** Liste todas as violações de normalização que você identifica nessa tabela. Para cada violação, indique qual forma normal é violada e por quê.

**(b)** Proponha uma estrutura normalizada (mínimo 3FN) que resolva todos os problemas apontados. Descreva as tabelas em texto ou ASCII, indicando PKs e FKs.

**(c)** Com a estrutura normalizada, escreva a query SQL que reproduz a visão original da tabela `pedidos_legado` (ou seja, um resultado parecido com a tabela acima, com JOIN entre as tabelas criadas).

---

## Exercício 2.2 — Modelagem relacional: sistema de biblioteca

### Cenário

Uma biblioteca municipal quer digitalizar seu acervo. Os requisitos levantados com a bibliotecária são:

- A biblioteca possui livros. Cada livro tem título, ano de publicação e ISBN.
- Cada livro pode ter um ou mais autores. Um autor pode ter escrito vários livros.
- Os membros da biblioteca são cadastrados com nome, e-mail e data de filiação.
- Um membro pode pegar emprestado vários livros ao longo do tempo, mas cada empréstimo registra um único livro por vez.
- Cada empréstimo tem data de retirada e data de devolução prevista. A devolução real pode ser diferente (ou ausente, se o livro ainda não foi devolvido).

### Tarefas

**(a)** Identifique todas as entidades do sistema e seus atributos principais.

**(b)** Identifique todos os relacionamentos entre as entidades e classifique a cardinalidade de cada um (1:1, 1:N ou N:M).

**(c)** Desenhe o modelo em texto/ASCII, mostrando as tabelas com seus campos, PKs e FKs. Atenção especial para o relacionamento N:M entre livros e autores — ele requer uma tabela associativa.

---

## Exercício 2.3 — Transformando o schema relacional em modelo dimensional

### Cenário

Você trabalha como engenheiro de dados em uma empresa de e-commerce. O banco transacional (`dados.db`) tem as tabelas `categorias`, `produtos`, `clientes` e `vendas`. A equipe de BI quer criar um data warehouse para responder perguntas como:

- "Qual mês de 2024 teve o maior faturamento?"
- "Quais categorias vendem mais aos finais de semana?"
- "Qual estado tem o maior ticket médio por venda?"
- "Quais produtos do segmento Eletronicos têm melhor performance por trimestre?"

O schema atual não responde essas perguntas de forma eficiente — precisamos de um modelo dimensional.

### Tarefas

**(a)** Defina o **grão** da tabela fato: o que representa uma única linha em `fato_vendas`?

**(b)** Proponha um **modelo dimensional** com:
- `fato_vendas` com todas as métricas e FKs
- `dim_cliente` com atributos relevantes para análise
- `dim_produto` com `nome_categoria` desnormalizado (star schema)
- `dim_tempo` com os atributos analíticos necessários para responder às perguntas acima

Para cada tabela, liste os campos e indique PKs e FKs.

**(c)** Desenhe o diagrama do star schema em ASCII com as 4 tabelas.

**(d)** Escreva a query SQL que, usando o schema atual do `dados.db`, responde: *"Qual o faturamento total por mês e ano, ordenado do mais recente ao mais antigo?"*

> Dica: use `strftime('%Y', data_venda)` e `strftime('%m', data_venda)` para extrair ano e mês no SQLite.

---

## Exercício 2.4 — Star Schema vs Snowflake Schema

### Cenário

Você está modelando o data warehouse de uma rede varejista com lojas em todo o Brasil. A dimensão de localização precisa capturar:

- Nome da loja
- Endereço da loja
- Cidade (500 cidades distintas)
- Estado (27 estados)
- Região (5 regiões: Norte, Nordeste, Centro-Oeste, Sudeste, Sul)

Cada loja fica em uma cidade, cada cidade fica em um estado, cada estado fica em uma região.

### Tarefas

**(a)** Modele a dimensão de localização no estilo **star schema** — uma única tabela `dim_loja` desnormalizada. Liste todos os campos.

**(b)** Modele a dimensão de localização no estilo **snowflake schema** — normalize a hierarquia cidade > estado > região em tabelas separadas. Desenhe em ASCII e liste os campos de cada tabela.

**(c)** Considerando que:
- A equipe de BI usa Power BI e faz consultas diárias do tipo `GROUP BY cidade, estado, regiao`
- Os dados de localização mudam raramente (uma loja pode mudar de endereço, mas cidades e estados não mudam)
- O volume de lojas é de 1.200 registros

**Qual abordagem você recomenda? Justifique em 3–5 frases, considerando performance, manutenção e complexidade de queries.**
