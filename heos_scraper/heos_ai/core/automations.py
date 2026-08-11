"""FASE 7 — Automatizaciones y Notificaciones (manual 040 §7 y Doc 007 §9).

El motor de reglas lee las alertas activas y los datos de la flota y dispara
acciones automáticas según los permisos definidos en los documentos:
  - Baja utilización (>10 días sin asignación) -> alerta + sugerir traslado + notificar Comercial
  - Mantenimiento vencido -> notificar taller
  - Cliente moroso -> notificar cobranza (Financiero)
  - Máquina 'Disponible' sin contrato -> oportunidad de ingreso (Comercial)
"""
from db.database import q, q1, execute
import datetime as _dt


def _asegurar_tabla():
    execute("""CREATE TABLE IF NOT EXISTS notificaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT DEFAULT (datetime('now')),
        area TEXT,
        mensaje TEXT,
        canal TEXT DEFAULT 'Consola',
        estado TEXT DEFAULT 'Enviada'
    )""")


def _notificar(area, mensaje, canal="Consola"):
    execute("INSERT INTO notificaciones (area, mensaje, canal) VALUES (?,?,?)",
            (area, mensaje, canal))


def ejecutar_automatizaciones():
    """Dispara las automatizaciones según reglas y devuelve el log de acciones."""
    _asegurar_tabla()
    acciones = []

    # --- Regla: máquinas Disponibles sin contrato (oportunidad de ingreso) ---
    libres = q("""SELECT f.codigo, f.modelo, f.sucursal
                  FROM flota f
                  WHERE f.estado='Disponible'
                    AND NOT EXISTS (SELECT 1 FROM contratos c
                                    WHERE c.maquina=f.codigo AND c.estado='Activo')""")
    for m in libres:
        msg = (f"Oportunidad: {m['codigo']} ({m['modelo']}) disponible en {m['sucursal']} "
               f"sin contrato. Contactar clientes inactivos / promoción 8%.")
        _notificar("Comercial", msg)
        acciones.append(("Comercial", msg))

    # --- Regla: mantenimiento vencido/próximo -> notificar taller ---
    hoy = _dt.date.today()
    for m in q("SELECT codigo, proximo_mantenimiento FROM flota"):
        pm = m["proximo_mantenimiento"]
        if not pm:
            continue
        try:
            dias = (hoy - _dt.date.fromisoformat(pm)).days
        except ValueError:
            continue
        if dias >= 0:
            msg = f"Mantenimiento de {m['codigo']} VENCIDO ({dias} días). Programar taller ya."
            _notificar("Mantenimiento", msg)
            acciones.append(("Mantenimiento", msg))

    # --- Regla: cliente moroso -> cobranza ---
    for c in q("SELECT nombre, dias_pago FROM clientes WHERE moroso=1"):
        msg = f"Cliente {c['nombre']} moroso (plazo {c['dias_pago']} días). Activar cobranza."
        _notificar("Financiero", msg)
        acciones.append(("Financiero", msg))

    return acciones


def listar_notificaciones(limit=20):
    return q(f"SELECT * FROM notificaciones ORDER BY id DESC LIMIT {limit}")
