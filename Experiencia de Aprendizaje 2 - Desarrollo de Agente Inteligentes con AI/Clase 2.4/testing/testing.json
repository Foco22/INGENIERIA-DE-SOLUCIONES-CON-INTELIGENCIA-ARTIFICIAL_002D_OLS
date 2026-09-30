
import sqlite3
import os
import random
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

random.seed(42)

CLIENTES = [
    (1, "Ana García",   "ana@mail.com",    "Santiago"),
    (2, "Luis Pérez",   "luis@mail.com",   "Valparaíso"),
    (3, "María López",  "maria@mail.com",  "Santiago"),
    (4, "Carlos Ruiz",  "carlos@mail.com", "Concepción"),
    (5, "Sofía Torres", "sofia@mail.com",  "Santiago"),
]

PRODUCTOS = [
    (1, "Laptop Pro",          "Electrónica", 899990),
    (2, "Mouse Inalámbrico",   "Electrónica",  19990),
    (3, "Teclado Mecánico",    "Electrónica",  49990),
    (4, 'Monitor 27"',         "Electrónica", 299990),
    (5, "Silla Ergonómica",    "Muebles",     189990),
    (6, "Escritorio",          "Muebles",     149990),
]

ESTADOS = ["entregado", "entregado", "entregado", "pendiente", "cancelado"]


def generar_pedidos():
    pedidos = []
    detalles = []
    pedido_id = 1
    detalle_id = 1

    start = date(2025, 1, 1)
    end = date(2025, 12, 31)

    current = start
    while current <= end:
        # Entre 2 y 5 pedidos por semana
        n_pedidos = random.randint(2, 5)
        for _ in range(n_pedidos):
            cliente_id = random.choice(CLIENTES)[0]
            estado = random.choice(ESTADOS)
            dia = current + timedelta(days=random.randint(0, 6))
            if dia > end:
                dia = end
            pedidos.append((pedido_id, cliente_id, dia.isoformat(), estado))

            # Entre 1 y 4 productos por pedido
            productos_pedido = random.sample(PRODUCTOS, random.randint(1, 4))
            for prod in productos_pedido:
                cantidad = random.randint(1, 3)
                detalles.append((detalle_id, pedido_id, prod[0], cantidad, prod[3]))
                detalle_id += 1

            pedido_id += 1

        current += timedelta(weeks=1)

    return pedidos, detalles


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS detalle_pedidos;
        DROP TABLE IF EXISTS pedidos;
        DROP TABLE IF EXISTS productos;
        DROP TABLE IF EXISTS clientes;

        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            email TEXT,
            ciudad TEXT
        );

        CREATE TABLE productos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            categoria TEXT,
            precio REAL NOT NULL
        );

        CREATE TABLE pedidos (
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER REFERENCES clientes(id),
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL
        );

        CREATE TABLE detalle_pedidos (
            id INTEGER PRIMARY KEY,
            pedido_id INTEGER REFERENCES pedidos(id),
            producto_id INTEGER REFERENCES productos(id),
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL
        );
    """)

    cur.executemany("INSERT INTO clientes VALUES (?,?,?,?)", CLIENTES)
    cur.executemany("INSERT INTO productos VALUES (?,?,?,?)", PRODUCTOS)

    pedidos, detalles = generar_pedidos()
    cur.executemany("INSERT INTO pedidos VALUES (?,?,?,?)", pedidos)
    cur.executemany("INSERT INTO detalle_pedidos VALUES (?,?,?,?,?)", detalles)

    conn.commit()

    print(f"Base de datos creada en: {DB_PATH}")
    print(f"  Pedidos:          {len(pedidos)}")
    print(f"  Detalle pedidos:  {len(detalles)}")

    conn.close()


if __name__ == "__main__":
    seed()
