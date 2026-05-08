# Schema do Banco de Dados — Upskilling Engenharia de Dados

O banco `recursos/dados.db` é gerado pelo script `recursos/setup_db.py` usando Faker (pt_BR) e SQLite.

Execute o script para criar o ambiente local:

```bash
python recursos/setup_db.py
```

---

## Tabelas

### `categorias`

Categorias de produtos disponíveis na loja.

| Coluna        | Tipo    | Descrição                        |
|---------------|---------|----------------------------------|
| `categoria_id`| INTEGER | Chave primária                   |
| `nome`        | TEXT    | Nome da categoria                |

**Registros:** 8  
Valores: Eletronicos, Roupas, Livros, Eletrodomesticos, Esportes, Beleza, Alimentos, Moveis

---

### `produtos`

Catálogo de produtos comercializados.

| Coluna        | Tipo    | Descrição                                          |
|---------------|---------|----------------------------------------------------|
| `produto_id`  | INTEGER | Chave primária                                     |
| `nome`        | TEXT    | Nome do produto (adjetivo + substantivo)           |
| `categoria_id`| INTEGER | Chave estrangeira → `categorias(categoria_id)`     |
| `preco`       | REAL    | Preço unitário em reais (R$)                       |

**Registros:** 60  
Faixas de preço por categoria:
- Eletronicos: R$200 – R$8.000
- Roupas: R$40 – R$500
- Livros: R$25 – R$200
- Eletrodomesticos: R$80 – R$3.500
- Esportes: R$30 – R$2.000
- Beleza: R$15 – R$400
- Alimentos: R$10 – R$300
- Moveis: R$150 – R$5.000

---

### `clientes`

Clientes cadastrados na plataforma.

| Coluna          | Tipo | Descrição                                       |
|-----------------|------|-------------------------------------------------|
| `cliente_id`    | INTEGER | Chave primária                               |
| `nome`          | TEXT    | Nome completo (gerado por Faker pt_BR)       |
| `email`         | TEXT    | Endereço de e-mail                           |
| `cidade`        | TEXT    | Cidade brasileira                            |
| `estado`        | TEXT    | Sigla do estado (UF)                         |
| `data_cadastro` | DATE    | Data de cadastro (ISO 8601: YYYY-MM-DD)      |

**Registros:** 300

---

### `vendas`

Transações de venda realizadas no período 2023–2024.

| Coluna        | Tipo    | Descrição                                      |
|---------------|---------|------------------------------------------------|
| `venda_id`    | INTEGER | Chave primária                                 |
| `cliente_id`  | INTEGER | Chave estrangeira → `clientes(cliente_id)`     |
| `produto_id`  | INTEGER | Chave estrangeira → `produtos(produto_id)`     |
| `quantidade`  | INTEGER | Quantidade comprada (1 a 5)                    |
| `data_venda`  | DATE    | Data da venda (ISO 8601: YYYY-MM-DD)           |
| `valor_total` | REAL    | Total da venda = `quantidade × preco`          |

**Registros:** 3.000  
**Período:** 2023-01-01 a 2024-12-31

---

## Relacionamentos

```
categorias (1) ──< produtos (N)
clientes   (1) ──< vendas   (N)
produtos   (1) ──< vendas   (N)
```

---

## Reprodutibilidade

Os dados são gerados com seeds fixas:
- `random.seed(42)`
- `Faker.seed(42)`

Rodar o script em qualquer máquina produz exatamente o mesmo conjunto de dados.
