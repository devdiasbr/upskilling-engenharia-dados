# Dataset — Loja de E-commerce

Dataset fictício reutilizado em todos os módulos da trilha.

## Tabelas

### clientes
| coluna         | tipo    | descrição                        |
|----------------|---------|----------------------------------|
| cliente_id     | INTEGER | identificador único              |
| nome           | VARCHAR | nome completo                    |
| email          | VARCHAR | email de contato                 |
| cidade         | VARCHAR | cidade de residência             |
| data_cadastro  | DATE    | data de cadastro na plataforma   |

### produtos
| coluna         | tipo    | descrição                        |
|----------------|---------|----------------------------------|
| produto_id     | INTEGER | identificador único              |
| nome           | VARCHAR | nome do produto                  |
| categoria      | VARCHAR | categoria (Eletrônicos, Roupas…) |
| preco          | DECIMAL | preço unitário                   |

### vendas
| coluna         | tipo    | descrição                        |
|----------------|---------|----------------------------------|
| venda_id       | INTEGER | identificador único              |
| cliente_id     | INTEGER | FK → clientes                    |
| produto_id     | INTEGER | FK → produtos                    |
| quantidade     | INTEGER | unidades vendidas                |
| data_venda     | DATE    | data da transação                |
| valor_total    | DECIMAL | quantidade × preço               |
