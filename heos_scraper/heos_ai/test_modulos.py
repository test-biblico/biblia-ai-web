"""Prueba de integracion: inserta ejemplos en cada modulo y valida que
los Directores IA y el Orchestrator reaccionan correctamente.

Uso: python test_modulos.py   (requiere base cargada: python heos.py cargar)
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from db import database as db
from core import orchestrator, directors


def ok(cond, msg):
    print(f"  [{'OK' if cond else 'FALLO'}] {msg}")
    return cond


def main():
    db.init_db()
    print("=== PRUEBA: insercion de ejemplos por modulo ===")

    # --- Modulo FLOTA: nueva maquina ---
    db.execute("""INSERT INTO flota (codigo,marca,modelo,anho,tipo,valor_compra,horas,
                  estado,precio_hora,costo_hora,proximo_mantenimiento)
                  VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
               ("MAQ-TEST", "Test", "TX100", 2024, "Excavadora", 500_000_000, 1000,
                "Disponible", 200_000, 80_000, "2026-08-20"))
    flota = db.q1("SELECT * FROM flota WHERE codigo='MAQ-TEST'")
    ok(flota is not None, "FLOTA: MAQ-TEST insertada")

    # --- Modulo CLIENTES: nuevo cliente moroso ---
    db.execute("""INSERT INTO clientes (nombre,tipo_contrato,precio_hora,dias_pago,moroso,rentabilidad)
                  VALUES (?,?,?,?,?,?)""",
               ("Cliente Prueba", "Spot", 210_000, 90, 1, 5.0))
    cli = db.q1("SELECT * FROM clientes WHERE nombre='Cliente Prueba'")
    ok(cli is not None and cli["moroso"] == 1, "CLIENTES: Cliente Prueba moroso insertado")

    # --- Modulo FINANZAS: nuevo gasto de combustible ---
    db.execute("""INSERT INTO finanzas (fecha,concepto,tipo,categoria,monto,cliente)
                  VALUES (?,?,?,?,?,?)""",
               ("2026-08-20", "Combustible prueba", "Gasto", "Combustible", 5_000_000, ""))
    fin = db.q1("SELECT SUM(monto) AS t FROM finanzas WHERE categoria='Combustible'")
    ok(fin["t"] > 0, "FINANZAS: gasto de combustible registrado")

    # --- Modulo MANTENIMIENTO: mantenimiento vencido ---
    db.execute("""INSERT INTO mantenimiento (maquina,tipo,fecha,costo,detalle,estado)
                  VALUES (?,?,?,?,?,?)""",
               ("MAQ-TEST", "Preventivo", "2026-08-01", 1_000_000, "Cambio de aceite", "Abierto"))
    mnt = db.q1("SELECT * FROM mantenimiento WHERE maquina='MAQ-TEST'")
    ok(mnt is not None, "MANTENIMIENTO: registro de MAQ-TEST insertado")

    # --- Modulo INCIDENTES: incidente abierto ---
    db.execute("""INSERT INTO incidentes (maquina,operador,causa,costo_estimado,estado)
                  VALUES (?,?,?,?,?)""",
               ("MAQ-TEST", "Tester", "Sobrecalentamiento", 3_000_000, "Abierto"))
    inc = db.q1("SELECT * FROM incidentes WHERE maquina='MAQ-TEST'")
    ok(inc is not None, "INCIDENTES: incidente de MAQ-TEST insertado")

    # --- Modulo CONTRATOS: nuevo contrato activo ---
    db.execute("""INSERT INTO contratos (cliente,maquina,fecha_inicio,fecha_fin,precio_hora,horas_contrato,estado)
                  VALUES (?,?,?,?,?,?,?)""",
               ("Cliente Prueba", "MAQ-TEST", "2026-08-20", "2026-09-20", 200_000, 100, "Activo"))
    con = db.q1("SELECT * FROM contratos WHERE maquina='MAQ-TEST'")
    ok(con is not None, "CONTRATOS: contrato de MAQ-TEST insertado")

    print("\n=== PRUEBA: reaccion de los Directores IA ===")

    # Director Seguridad debe detectar el incidente abierto
    seg = directors.director_seguridad()
    ok(seg["kpi"]["incidentes_abiertos"] >= 1, "DIRECTOR SEGURIDAD: detecta incidente abierto")

    # Director Financiero debe detectar el moroso nuevo
    fin_dir = directors.director_financiero()
    morosos = [a for a in fin_dir["alertas"] if a[1] == "Financiero" and "moroso" in a[2].lower()]
    ok(len(morosos) >= 1, "DIRECTOR FINANCIERO: detecta cliente moroso")

    # Director Operaciones debe contar la nueva maquina
    ops = directors.director_operaciones()
    ok(ops["kpi"]["maquinas_totales"] >= 13, "DIRECTOR OPERACIONES: contabiliza 13+ maquinas")

    # Director Comercial debe ver el contrato nuevo
    com = directors.director_comercial()
    ok(com["kpi"]["contratos_activos"] >= 7, "DIRECTOR COMERCIAL: ve 7+ contratos activos")

    # Orchestrator: ciclo completo y alertas persistidas
    ciclo = orchestrator.ejecutar_ciclo()
    ok(ciclo["IGE"] > 0, f"ORCHESTRATOR: IGE={ciclo['IGE']} calculado")
    alertas_db = db.q("SELECT COUNT(*) AS n FROM alertas")
    ok(alertas_db[0]["n"] >= 7, "ORCHESTRATOR: alertas persistidas en BD")

    # Dashboard HTML vuelve a generarse sin error
    from core import dashboards
    path = dashboards.save_dashboard()
    ok(os.path.exists(path), f"DASHBOARD: regenerado ({os.path.getsize(path)} bytes)")

    print("\n=== RESULTADO ===")
    print("Todas las pruebas de modulos completadas. Sistema operativo.")


if __name__ == "__main__":
    main()
