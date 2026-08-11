"""Carga inicial de datos mínima recomendada (FASE 4 del manual 040).

Empresa: Constructora XYZ. Flota, clientes, personal, finanzas de ejemplo
para que HEOS pueda construir su línea base y producir el primer diagnóstico.
"""
from db.database import reset_db, execute, insert_many


def seed():
    reset_db()

    # ---------------- EMPRESA ----------------
    execute(
        """INSERT INTO empresa (id, nombre, giro, moneda, objetivo_texto, organizacion_json)
           VALUES (1, ?, ?, ?, ?, ?)""",
        (
            "Constructora XYZ",
            "Alquiler de maquinaria pesada",
            "Gs.",
            "Maximizar rentabilidad de la flota con decisiones basadas en datos.",
            '{"directores": ["Operaciones","Financiero","Mantenimiento","Comercial",'
            '"Compras","Inventario","RRHH","Seguridad","BI"]}',
        ),
    )

    # ---------------- FLOTA (expediente inteligente por máquina) ----------------
    # (codigo, marca, modelo, anho, tipo, capacidad, valor_compra, horas, odometro,
    #  sucursal, ubicacion_gps, cliente_asignado, proyecto, operador, estado,
    #  precio_hora, costo_hora, ultimo_mantenimiento, proximo_mantenimiento, km_desde_sucursal)
    flota = [
        ("MAQ-001", "Caterpillar", "CAT 320", 2022, "Excavadora", "20 t", 850_000_000, 3200, 41000, "Asuncion", "-25.30,-57.63", "Constructora ABC", "Ruta 2", "Carlos R.", "Trabajando", 250_000, 95_000, "2026-05-10", "2026-11-10", 18),
        ("MAQ-002", "Komatsu", "PC200", 2021, "Excavadora", "20 t", 800_000_000, 4100, 38000, "Asuncion", "-25.28,-57.60", "", "", "", "Disponible", 245_000, 92_000, "2026-06-01", "2026-12-01", 5),
        ("MAQ-003", "Caterpillar", "320D", 2019, "Excavadora", "20 t", 720_000_000, 6800, 61000, "Asuncion", "-25.29,-57.58", "Minera Sur", "Mina", "Luis P.", "Trabajando", 240_000, 110_000, "2026-04-20", "2026-10-20", 40),
        ("MAQ-004", "John Deere", "350D", 2020, "Retroexcavadora", "3.5 t", 480_000_000, 2900, 22000, "Asuncion", "-25.31,-57.62", "", "", "", "Disponible", 180_000, 70_000, "2026-07-05", "2027-01-05", 8),
        ("MAQ-005", "Caterpillar", "JCB-05", 2018, "Retroexcavadora", "3.5 t", 430_000_000, 7200, 25000, "Asuncion", "-25.27,-57.64", "Constructora ABC", "Ruta 2", "Pedro G.", "Trabajando", 175_000, 85_000, "2026-03-15", "2026-09-15", 22),
        ("MAQ-006", "Volvo", "EC210", 2021, "Excavadora", "21 t", 820_000_000, 3500, 33000, "San Lorenzo", "-25.34,-57.51", "Viales SA", "Autopista", "Miguel S.", "Trabajando", 255_000, 98_000, "2026-06-20", "2026-12-20", 30),
        ("MAQ-007", "Komatsu", "D65", 2019, "Bulldozer", "20 t", 900_000_000, 5400, 30000, "Asuncion", "-25.32,-57.59", "", "", "", "Disponible", 300_000, 120_000, "2026-05-25", "2026-11-25", 12),
        ("MAQ-008", "Caterpillar", "CAT 320", 2022, "Excavadora", "20 t", 850_000_000, 2100, 19000, "Asuncion", "-25.30,-57.63", "Constructora ABC", "Ruta 2", "Carlos R.", "Trabajando", 250_000, 95_000, "2026-07-10", "2027-01-10", 18),
        ("MAQ-009", "Hyundai", "R210", 2020, "Excavadora", "21 t", 760_000_000, 4600, 35000, "San Lorenzo", "-25.35,-57.50", "Viales SA", "Autopista", "Juan M.", "Trabajando", 235_000, 90_000, "2026-04-30", "2026-10-30", 30),
        ("MAQ-010", "Caterpillar", "MAQ-018", 2017, "Excavadora", "22 t", 700_000_000, 8000, 70000, "Asuncion", "-25.26,-57.61", "", "", "", "Trabajando", 130_000, 100_000, "2026-02-10", "2026-08-10", 15),
        ("MAQ-018", "Caterpillar", "MAQ-054", 2017, "Bulldozer", "20 t", 700_000_000, 8100, 71000, "Asuncion", "-25.33,-57.57", "", "", "", "Disponible", 290_000, 125_000, "2026-02-15", "2026-08-15", 14),
        ("MAQ-044", "Komatsu", "PC300", 2018, "Excavadora", "30 t", 950_000_000, 7700, 65000, "Asuncion", "-25.25,-57.65", "", "", "", "Disponible", 280_000, 115_000, "2026-01-20", "2026-07-20", 25),
    ]
    insert_many(
        "flota",
        ["codigo", "marca", "modelo", "anho", "tipo", "capacidad", "valor_compra", "horas",
         "odometro", "sucursal", "ubicacion_gps", "cliente_asignado", "proyecto", "operador",
         "estado", "precio_hora", "costo_hora", "ultimo_mantenimiento", "proximo_mantenimiento",
         "km_desde_sucursal"],
        flota,
    )

    # ---------------- CLIENTES ----------------
    # (nombre, tipo_contrato, precio_hora, dias_pago, moroso, rentabilidad)
    clientes = [
        ("Constructora ABC", "Mensual", 250_000, 30, 0, 22.0),
        ("Minera Sur", "Por obra", 260_000, 45, 0, 25.0),
        ("Viales SA", "Mensual", 255_000, 30, 0, 20.0),
        ("Inmobiliaria Centro", "Spot", 230_000, 60, 1, 12.0),   # moroso
        ("Obras Publicas", "Por obra", 240_000, 30, 0, 18.0),
    ]
    insert_many(
        "clientes",
        ["nombre", "tipo_contrato", "precio_hora", "dias_pago", "moroso", "rentabilidad"],
        clientes,
    )

    # ---------------- PERSONAL ----------------
    # (nombre, rol, certificado, disponible, productividad, sucursal)
    personal = [
        ("Carlos R.", "Operador", 1, 0, 95, "Asuncion"),
        ("Luis P.", "Operador", 1, 0, 92, "Asuncion"),
        ("Pedro G.", "Operador", 1, 0, 88, "Asuncion"),
        ("Miguel S.", "Operador", 1, 0, 90, "San Lorenzo"),
        ("Juan M.", "Operador", 1, 0, 93, "San Lorenzo"),
        ("Tec. Ramon", "Tecnico", 1, 1, 96, "Asuncion"),
        ("Tec. Baez", "Tecnico", 1, 1, 91, "Asuncion"),
        ("Ana L.", "Administrativo", 1, 1, 98, "Asuncion"),
    ]
    insert_many(
        "personal",
        ["nombre", "rol", "certificado", "disponible", "productividad", "sucursal"],
        personal,
    )

    # ---------------- FINANZAS (mes actual: agosto 2026) ----------------
    # (fecha, concepto, tipo, categoria, monto, cliente)
    finanzas = [
        ("2026-08-01", "Alquiler MAQ-001", "Ingreso", "Alquiler", 60_000_000, "Constructora ABC"),
        ("2026-08-01", "Alquiler MAQ-003", "Ingreso", "Alquiler", 55_000_000, "Minera Sur"),
        ("2026-08-01", "Alquiler MAQ-006", "Ingreso", "Alquiler", 58_000_000, "Viales SA"),
        ("2026-08-05", "Combustible flota", "Gasto", "Combustible", 28_000_000, ""),
        ("2026-08-05", "Salarios operadores", "Gasto", "Salarios", 45_000_000, ""),
        ("2026-08-08", "Repuestos taller", "Gasto", "Repuestos", 12_000_000, ""),
        ("2026-08-08", "Seguro flota", "Gasto", "Seguros", 9_000_000, ""),
        ("2026-08-10", "Alquiler MAQ-005", "Ingreso", "Alquiler", 40_000_000, "Constructora ABC"),
        ("2026-08-10", "Financiacion equipo", "Gasto", "Financiacion", 18_000_000, ""),
        ("2026-08-12", "Alquiler MAQ-009", "Ingreso", "Alquiler", 52_000_000, "Viales SA"),
        ("2026-08-15", "Combustible flota", "Gasto", "Combustible", 30_000_000, ""),
        ("2026-08-15", "Cobranza atrasada Inmobiliaria", "Gasto", "Morosidad", 0, "Inmobiliaria Centro"),
    ]
    insert_many(
        "finanzas",
        ["fecha", "concepto", "tipo", "categoria", "monto", "cliente"],
        finanzas,
    )

    # ---------------- CONTRATOS ACTIVOS ----------------
    # (cliente, maquina, fecha_inicio, fecha_fin, precio_hora, horas_contrato, estado)
    contratos = [
        ("Constructora ABC", "MAQ-001", "2026-08-01", "2026-09-30", 250_000, 350, "Activo"),
        ("Constructora ABC", "MAQ-005", "2026-08-01", "2026-09-15", 175_000, 200, "Activo"),
        ("Constructora ABC", "MAQ-008", "2026-08-05", "2026-09-30", 250_000, 300, "Activo"),
        ("Minera Sur", "MAQ-003", "2026-07-15", "2026-10-15", 260_000, 600, "Activo"),
        ("Viales SA", "MAQ-006", "2026-08-01", "2026-09-30", 255_000, 400, "Activo"),
        ("Viales SA", "MAQ-009", "2026-08-10", "2026-09-30", 235_000, 320, "Activo"),
    ]
    insert_many(
        "contratos",
        ["cliente", "maquina", "fecha_inicio", "fecha_fin", "precio_hora", "horas_contrato", "estado"],
        contratos,
    )

    print("HEOS_DATABASE cargada: Constructora XYZ.")
    print(f"  Flota: {len(flota)} | Clientes: {len(clientes)} | Personal: {len(personal)} | Finanzas: {len(finanzas)}")


if __name__ == "__main__":
    seed()
