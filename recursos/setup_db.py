"""
setup_db.py
Gera dados realistas com Faker (pt_BR), cria o banco SQLite e exporta CSVs.
Execute: python recursos/setup_db.py
"""

import csv
import os
import random
import sqlite3
from pathlib import Path

from faker import Faker

# ---------------------------------------------------------------------------
# Configuracao de seed para reproducibilidade
# ---------------------------------------------------------------------------
random.seed(42)
Faker.seed(42)
fake = Faker("pt_BR")

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "dados.db"
EXPORTS_DIR = BASE_DIR / "exports"

# ---------------------------------------------------------------------------
# Dados de referencia por categoria
# ---------------------------------------------------------------------------
CATEGORIAS = [
    (1, "Eletronicos"),
    (2, "Roupas"),
    (3, "Livros"),
    (4, "Eletrodomesticos"),
    (5, "Esportes"),
    (6, "Beleza"),
    (7, "Alimentos"),
    (8, "Moveis"),
]

PRODUTO_TEMPLATES = {
    1: {  # Eletronicos
        "adjetivos": ["Smart", "Ultra", "Pro", "Slim", "Turbo"],
        "substantivos": ["Smartphone", "Notebook", "Tablet", "Fone de Ouvido", "Monitor",
                         "Teclado Mecanico", "Mouse Gamer", "Webcam", "SSD Externo", "Smartwatch"],
        "preco_min": 200.0,
        "preco_max": 8000.0,
    },
    2: {  # Roupas
        "adjetivos": ["Elegante", "Casual", "Slim", "Confortavel", "Moderno"],
        "substantivos": ["Camiseta", "Calca Jeans", "Vestido", "Jaqueta", "Tenis",
                         "Blusa", "Shorts", "Moletom", "Saia", "Camisa Social"],
        "preco_min": 40.0,
        "preco_max": 500.0,
    },
    3: {  # Livros
        "adjetivos": ["Essencial", "Completo", "Pratico", "Avancado", "Definitivo"],
        "substantivos": ["Guia de Python", "Manual de SQL", "Introducao a IA",
                         "Fundamentos de Redes", "Atlas Geografico", "Dicionario Tecnico",
                         "Romance Historico", "Conto de Suspense", "Poesia Brasileira", "Biografia"],
        "preco_min": 25.0,
        "preco_max": 200.0,
    },
    4: {  # Eletrodomesticos
        "adjetivos": ["Turbo", "Digital", "Silencioso", "Compacto", "Automatico"],
        "substantivos": ["Liquidificador", "Cafeteira", "Aspirador", "Fritadeira Air Fryer",
                         "Micro-ondas", "Geladeira", "Maquina de Lavar", "Secador de Cabelo",
                         "Ferro de Passar", "Batedeira"],
        "preco_min": 80.0,
        "preco_max": 3500.0,
    },
    5: {  # Esportes
        "adjetivos": ["Pro", "Esportivo", "Resistente", "Leve", "Ergonomico"],
        "substantivos": ["Bicicleta", "Haltere", "Tapete de Yoga", "Corda de Pular",
                         "Luva de Boxe", "Garrafa Termica", "Mochila Esportiva",
                         "Capacete", "Joelheira", "Bola de Futebol"],
        "preco_min": 30.0,
        "preco_max": 2000.0,
    },
    6: {  # Beleza
        "adjetivos": ["Natural", "Organico", "Hidratante", "Revitalizante", "Premium"],
        "substantivos": ["Shampoo", "Condicionador", "Creme Facial", "Perfume",
                         "Batom", "Base Facial", "Mascara de Cilios", "Esfoliante",
                         "Oleo Corporal", "Protetor Solar"],
        "preco_min": 15.0,
        "preco_max": 400.0,
    },
    7: {  # Alimentos
        "adjetivos": ["Integral", "Organico", "Artesanal", "Premium", "Natural"],
        "substantivos": ["Cafe Torrado", "Granola", "Azeite Extra Virgem", "Mel Puro",
                         "Barra de Proteina", "Pasta de Amendoim", "Cha Verde",
                         "Amendoim Torrado", "Quinoa", "Whey Protein"],
        "preco_min": 10.0,
        "preco_max": 300.0,
    },
    8: {  # Moveis
        "adjetivos": ["Moderno", "Classico", "Compacto", "Ergonomico", "Sustentavel"],
        "substantivos": ["Escrivaninha", "Cadeira de Escritorio", "Estante", "Mesa de Jantar",
                         "Sofa 2 Lugares", "Rack para TV", "Guarda-Roupa", "Poltrona",
                         "Mesa de Centro", "Painel Decorativo"],
        "preco_min": 150.0,
        "preco_max": 5000.0,
    },
}


# ---------------------------------------------------------------------------
# Geradores
# ---------------------------------------------------------------------------

def gerar_categorias():
    return CATEGORIAS


def gerar_produtos(n=60):
    produtos = []
    produto_id = 1
    # Distribui os 60 produtos de forma mais uniforme entre as 8 categorias
    # 60 / 8 = 7 com sobra de 4, entao 4 categorias ficam com 8 e 4 com 7
    counts = [8, 8, 8, 8, 7, 7, 7, 7]
    random.shuffle(counts)

    for idx, (cat_id, _) in enumerate(CATEGORIAS):
        tmpl = PRODUTO_TEMPLATES[cat_id]
        usados = set()
        qtd = counts[idx]
        for _ in range(qtd):
            # Gera nome unico dentro da categoria
            tentativas = 0
            while True:
                adj = random.choice(tmpl["adjetivos"])
                sub = random.choice(tmpl["substantivos"])
                nome = f"{adj} {sub}"
                if nome not in usados or tentativas > 50:
                    usados.add(nome)
                    break
                tentativas += 1
            preco = round(random.uniform(tmpl["preco_min"], tmpl["preco_max"]), 2)
            produtos.append((produto_id, nome, cat_id, preco))
            produto_id += 1

    return produtos


def gerar_clientes(n=300):
    clientes = []
    for i in range(1, n + 1):
        nome = fake.name()
        email = fake.email()
        cidade = fake.city()
        estado = fake.state_abbr()
        data_cadastro = fake.date_between(start_date="-3y", end_date="today").isoformat()
        clientes.append((i, nome, email, cidade, estado, data_cadastro))
    return clientes


def gerar_vendas(clientes, produtos, n=3000):
    from datetime import date
    vendas = []
    data_inicio = date(2023, 1, 1)
    data_fim = date(2024, 12, 31)

    ids_clientes = [c[0] for c in clientes]
    # produtos: (produto_id, nome, categoria_id, preco)
    for i in range(1, n + 1):
        cliente_id = random.choice(ids_clientes)
        produto = random.choice(produtos)
        produto_id = produto[0]
        preco = produto[3]
        quantidade = random.randint(1, 5)
        valor_total = round(quantidade * preco, 2)
        data_venda = fake.date_between(start_date=data_inicio, end_date=data_fim).isoformat()
        vendas.append((i, cliente_id, produto_id, quantidade, data_venda, valor_total))
    return vendas


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------

def criar_banco(db_path: Path):
    # Remove banco anterior se existir
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE categorias (
            categoria_id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL
        );

        CREATE TABLE produtos (
            produto_id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria_id INTEGER NOT NULL REFERENCES categorias(categoria_id),
            preco REAL NOT NULL
        );

        CREATE TABLE clientes (
            cliente_id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            data_cadastro DATE NOT NULL
        );

        CREATE TABLE vendas (
            venda_id INTEGER PRIMARY KEY,
            cliente_id INTEGER NOT NULL REFERENCES clientes(cliente_id),
            produto_id INTEGER NOT NULL REFERENCES produtos(produto_id),
            quantidade INTEGER NOT NULL,
            data_venda DATE NOT NULL,
            valor_total REAL NOT NULL
        );
    """)

    return conn


def inserir_dados(conn, categorias, produtos, clientes, vendas):
    cur = conn.cursor()
    cur.executemany("INSERT INTO categorias VALUES (?, ?)", categorias)
    cur.executemany("INSERT INTO produtos VALUES (?, ?, ?, ?)", produtos)
    cur.executemany("INSERT INTO clientes VALUES (?, ?, ?, ?, ?, ?)", clientes)
    cur.executemany("INSERT INTO vendas VALUES (?, ?, ?, ?, ?, ?)", vendas)
    conn.commit()


# ---------------------------------------------------------------------------
# Exportacao CSV
# ---------------------------------------------------------------------------

TABELAS = {
    "categorias": ["categoria_id", "nome"],
    "produtos": ["produto_id", "nome", "categoria_id", "preco"],
    "clientes": ["cliente_id", "nome", "email", "cidade", "estado", "data_cadastro"],
    "vendas": ["venda_id", "cliente_id", "produto_id", "quantidade", "data_venda", "valor_total"],
}


def exportar_csvs(conn, exports_dir: Path):
    exports_dir.mkdir(parents=True, exist_ok=True)
    cur = conn.cursor()
    for tabela, colunas in TABELAS.items():
        cur.execute(f"SELECT * FROM {tabela}")
        rows = cur.fetchall()
        csv_path = exports_dir / f"{tabela}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(colunas)
            writer.writerows(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    categorias = gerar_categorias()
    produtos = gerar_produtos(60)
    clientes = gerar_clientes(300)
    vendas = gerar_vendas(clientes, produtos, 3000)

    conn = criar_banco(DB_PATH)
    inserir_dados(conn, categorias, produtos, clientes, vendas)

    exportar_csvs(conn, EXPORTS_DIR)
    conn.close()

    # Resumo
    print(f"Banco criado: {DB_PATH.relative_to(Path.cwd()) if DB_PATH.is_relative_to(Path.cwd()) else DB_PATH}")
    print(f"  categorias: {len(categorias)} registros")
    print(f"  produtos:   {len(produtos)} registros")
    print(f"  clientes:   {len(clientes)} registros")
    print(f"  vendas:     {len(vendas)} registros")
    print(f"Exports salvos em {EXPORTS_DIR.relative_to(Path.cwd()) if EXPORTS_DIR.is_relative_to(Path.cwd()) else EXPORTS_DIR}/")


if __name__ == "__main__":
    main()
