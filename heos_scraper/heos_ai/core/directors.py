"""Directores IA — FASE 3 del manual 040 y Documentos 004/120, 007/120, etc.

Cada Director implementa SU lógica de cálculo concreta (KPIs, salud de área,
alertas y recomendaciones). No son prompts: son funciones Python que operan
sobre HEOS_DATABASE y devuelven un dict estructurado.
"""
from db.database import q, q1
import datetime as _dt


def _gs(n):
    """Formatea guaraníes de forma compacta para los informes."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "Gs. 0"
    return f"Gs. {n:,.0f}".replace(",", ".")


# ============================================================
# DIRECTOR OPERACIONES IA  (HEOS-OPS-01, Documento 007)
# ============================================================
def director_operaciones():
    flota = q("SELECT * FROM flota")
    total = len(flota)
    estados = {}
    for m in flota:
        estados[m["estado"]] = estados.get(m["estado"], 0) + 1
    disponibles = estados.get("Disponible", 0)
    trabajando = estados.get("Trabajando", 0)
    mantto = estados.get("En mantenimiento preventivo", 0) + estados.get("En mantenimiento correctivo", 0)
    detenidas = estados.get("Fuera de servicio", 0)

    # Utilización = máquinas trabajando / total (KPI Documento 007)
    utilizacion = round(100 * trabajando / total, 1) if total else 0

    alertas = []
    recomendaciones = []
    # Máquina detenida > 24h (fuera de servicio)
    if detenidas:
        alertas.append(("Alto", "Operaciones",
                         f"{detenidas} máquina(s) fuera de servicio",
                         "Afecta disponibilidad de la flota", 0))
    # Baja utilización (<70% requiere acción, Doc 007)
    if utilizacion < 70:
        alertas.append(("Medio", "Operaciones",
                         f"Utilización de flota baja: {utilizacion}%",
                         "Menos del 70% requiere acción", 0))
        recomendaciones.append({
            "problema": "Utilización de flota bajo el objetivo (70%)",
            "causa": "Máquinas disponibles sin asignación o contratos cortos",
            "impacto_gs": 0,
            "riesgo": "Medio",
            "accion": "Reubicar máquinas disponibles a sucursales con mayor demanda y promocionar alquiler",
            "responsable": "Director Comercial IA",
            "beneficio": "Subir utilización al objetivo",
            "confianza": 85,
        })
    return {
        "nombre": "Director Operaciones IA",
        "codigo": "HEOS-OPS-01",
        "kpi": {
            "maquinas_totales": total,
            "disponibles": disponibles,
            "trabajando": trabajando,
            "en_mantenimiento": mantto,
            "fuera_servicio": detenidas,
            "utilizacion_pct": utilizacion,
            "meta_utilizacion": 90,
        },
        "estados": estados,
        "alertas": alertas,
        "recomendaciones": recomendaciones,
    }


# ============================================================
# DIRECTOR FINANCIERO IA  (HEOS-FIN-01)
# ============================================================
def director_financiero():
    rows = q("SELECT tipo, categoria, SUM(monto) AS total FROM finanzas GROUP BY tipo, categoria")
    ingresos = sum(r["total"] for r in rows if r["tipo"] == "Ingreso")
    gastos = sum(r["total"] for r in rows if r["tipo"] == "Gasto")
    por_cat = {}
    for r in rows:
        por_cat.setdefault(r["categoria"], {})[r["tipo"]] = r["total"]
    rentabilidad = round(100 * (ingresos - gastos) / ingresos, 1) if ingresos else 0

    # Caja aproximada = ingresos - gastos (línea base simplificada)
    caja = ingresos - gastos

    alertas = []
    recomendaciones = []
    # Morosidad
    morosos = q("SELECT nombre, dias_pago FROM clientes WHERE moroso=1")
    if morosos:
        alertas.append(("Alto", "Financiero",
                         f"{len(morosos)} cliente(s) moroso(s)",
                         "Cobranza retrasada afecta liquidez", 0))
        recomendaciones.append({
            "problema": "Cliente moroso retrasa pago",
            "causa": "Plazos de pago largos y cobranza pasiva",
            "impacto_gs": 0,
            "riesgo": "Alto",
            "accion": "Activar cobranza automática y renegociar plazos a 30 días",
            "responsable": "Director Financiero IA",
            "beneficio": "Mejorar flujo de caja",
            "confianza": 90,
        })
    return {
        "nombre": "Director Financiero IA",
        "codigo": "HEOS-FIN-01",
        "kpi": {
            "ingresos": ingresos,
            "gastos": gastos,
            "rentabilidad_pct": rentabilidad,
            "caja_aprox": caja,
            "por_categoria": por_cat,
        },
        "alertas": alertas,
        "recomendaciones": recomendaciones,
    }


# ============================================================
# DIRECTOR MANTENIMIENTO IA  (HEOS-MNT-01)
# ============================================================
def director_mantenimiento():
    hoy = _dt.date.today()
    flota = q("SELECT codigo, proximo_mantenimiento, estado FROM flota")
    proximos = []
    for m in flota:
        pm = m["proximo_mantenimiento"]
        if pm:
            try:
                d = _dt.date.fromisoformat(pm)
                dias = (d - hoy).days
            except ValueError:
                dias = 999
            if dias <= 30:
                proximos.append((m["codigo"], pm, dias))
    proximos.sort(key=lambda x: x[2])

    alertas = []
    recomendaciones = []
    for codigo, pm, dias in proximos:
        nivel = "Critico" if dias <= 7 else ("Alto" if dias <= 15 else "Medio")
        alertas.append((nivel, "Mantenimiento",
                         f"{codigo} con mantenimiento vencido/próximo ({dias} días)",
                         f"Próximo: {pm}", 0))
        if dias <= 15:
            recomendaciones.append({
                "problema": f"{codigo} cerca de mantenimiento obligatorio",
                "causa": "Calendario de preventivo no ejecutado a tiempo",
                "impacto_gs": 0,
                "riesgo": nivel,
                "accion": f"Programar mantenimiento preventivo de {codigo} antes de {pm}",
                "responsable": "Director Mantenimiento IA",
                "beneficio": "Evitar falla correctiva costosa",
                "confianza": 92,
            })
    return {
        "nombre": "Director Mantenimiento IA",
        "codigo": "HEOS-MNT-01",
        "kpi": {
            "equipos_proximos_servicio": len(proximos),
            "detalle_proximos": [{"maquina": c, "fecha": p, "dias": d} for c, p, d in proximos],
        },
        "alertas": alertas,
        "recomendaciones": recomendaciones,
    }


# ============================================================
# DIRECTOR COMERCIAL IA  (HEOS-COM-01)
# ============================================================
def director_comercial():
    clientes = q("SELECT * FROM clientes")
    contratos = q("SELECT * FROM contratos WHERE estado='Activo'")
    # Ingreso proyectado de contratos activos
    ingreso_proy = sum(c["precio_hora"] * c["horas_contrato"] for c in contratos)
    top = sorted(clientes, key=lambda c: (c["rentabilidad"] or 0), reverse=True)

    alertas = []
    recomendaciones = []
    maquinas_libres = q("SELECT COUNT(*) AS n FROM flota WHERE estado='Disponible'")["n"] if q("SELECT COUNT(*) AS n FROM flota WHERE estado='Disponible'") else 0
    if maquinas_libres > 0:
        alertas.append(("Medio", "Comercial",
                         f"{maquinas_libres} máquina(s) disponible(s) sin contrato",
                         "Oportunidad de ingreso no capturada", 0))
        recomendaciones.append({
            "problema": f"{maquinas_libres} máquinas disponibles sin asignar",
            "causa": "Demanda no cubierta o precio fuera de mercado",
            "impacto_gs": maquinas_libres * 15_000_000,
            "riesgo": "Medio",
            "accion": "Lanzar promoción del 8% por 2 semanas y contactar clientes inactivos",
            "responsable": "Director Comercial IA",
            "beneficio": "Recuperar ingresos por flota ociosa",
            "confianza": 80,
        })
    return {
        "nombre": "Director Comercial IA",
        "codigo": "HEOS-COM-01",
        "kpi": {
            "clientes": len(clientes),
            "contratos_activos": len(contratos),
            "ingreso_proyectado_contratos": ingreso_proy,
            "cliente_top": top[0]["nombre"] if top else "",
            "rentabilidad_top": top[0]["rentabilidad"] if top else 0,
            "maquinas_disponibles": maquinas_libres,
        },
        "alertas": alertas,
        "recomendaciones": recomendaciones,
    }


# ============================================================
# DIRECTOR COMPRAS IA  (HEOS-PRO-01)
# ============================================================
def director_compras():
    gastos = q("SELECT categoria, SUM(monto) AS total FROM finanzas WHERE tipo='Gasto' GROUP BY categoria")
    g = {r["categoria"]: r["total"] for r in gastos}
    combustible = g.get("Combustible", 0)
    repuestos = g.get("Repuestos", 0)
    alertas = []
    recomendaciones = []
    if combustible > 0:
        alertas.append(("Bajo", "Compras",
                         f"Combustible representa {_gs(combustible)} en el mes",
                         "Revisar política de abastecimiento", 0))
        recomendaciones.append({
            "problema": "Costo de combustible elevado",
            "causa": "Proveedor y rutas sin optimizar",
            "impacto_gs": 0,
            "riesgo": "Bajo",
            "accion": "Renegociar proveedor de combustible y consolidar rutas de traslado",
            "responsable": "Director Compras IA",
            "beneficio": "Ahorro estimado Gs. 12 millones/año (ver manual 040)",
            "confianza": 78,
        })
    return {
        "nombre": "Director Compras IA",
        "codigo": "HEOS-PRO-01",
        "kpi": {"combustible": combustible, "repuestos": repuestos},
        "alertas": alertas,
        "recomendaciones": recomendaciones,
    }


# ============================================================
# DIRECTOR INVENTARIO IA  (HEOS-INV-01)
# ============================================================
def director_inventario():
    # Sin tabla de inventario detallada en la base mínima; reporta disponibilidad de flota
    # como proxy de disponibilidad de activos.
    disp = q("SELECT COUNT(*) AS n FROM flota WHERE estado='Disponible'")["n"]
    total = q("SELECT COUNT(*) AS n FROM flota")["n"]
    return {
        "nombre": "Director Inventario IA",
        "codigo": "HEOS-INV-01",
        "kpi": {"maquinas_disponibles": disp, "maquinas_totales": total},
        "alertas": [],
        "recomendaciones": [],
    }


# ============================================================
# DIRECTOR RRHH IA  (HEOS-HR-01)
# ============================================================
def director_rrhh():
    pers = q("SELECT rol, COUNT(*) AS n, AVG(productividad) AS prod FROM personal GROUP BY rol")
    activos = q("SELECT COUNT(*) AS n FROM personal")["n"]
    disp = q("SELECT COUNT(*) AS n FROM personal WHERE disponible=1")["n"]
    return {
        "nombre": "Director RRHH IA",
        "codigo": "HEOS-HR-01",
        "kpi": {"personal_activo": activos, "disponibles": disp, "por_rol": {p["rol"]: p["n"] for p in pers},
                "productividad_prom": round(sum(p["prod"] or 0 for p in pers) / len(pers), 1) if pers else 0},
        "alertas": [],
        "recomendaciones": [],
    }


# ============================================================
# DIRECTOR SEGURIDAD IA  (HEOS-SEC-01)
# ============================================================
def director_seguridad():
    inc = q("SELECT COUNT(*) AS n FROM incidentes WHERE estado='Abierto'")["n"]
    flota = q("SELECT COUNT(*) AS n FROM flota")
    total = flota["n"] if flota else 0
    safety = round(100 * (total - inc) / total, 1) if total else 100
    alertas = []
    if inc:
        alertas.append(("Alto", "Seguridad",
                         f"{inc} incidente(s) abierto(s)",
                         "Requiere acción correctiva", 0))
    return {
        "nombre": "Director Seguridad IA",
        "codigo": "HEOS-SEC-01",
        "kpi": {"incidentes_abiertos": inc, "safety_score": safety},
        "alertas": alertas,
        "recomendaciones": [],
    }


# ============================================================
# DIRECTOR INTELIGENCIA EMPRESARIAL IA  (HEOS-BI-01)
# ============================================================
def director_bi():
    """Calcula el IGE (Índice de Gestión Empresarial) agregando salud de áreas."""
    ops = director_operaciones()
    fin = director_financiero()
    mnt = director_mantenimiento()
    seg = director_seguridad()

    # IGE compuesto (0-100) ponderado
    salud_flota = 100 - (ops["kpi"]["fuera_servicio"] / ops["kpi"]["maquinas_totales"] * 100 if ops["kpi"]["maquinas_totales"] else 0)
    salud_fin = fin["kpi"]["rentabilidad_pct"]
    salud_mnt = 100 - min(100, mnt["kpi"]["equipos_proximos_servicio"] * 15)
    salud_seg = seg["kpi"]["safety_score"]
    ige = round(0.30 * salud_flota + 0.30 * max(0, salud_fin) + 0.20 * salud_mnt + 0.20 * salud_seg, 1)

    return {
        "nombre": "Director Inteligencia Empresarial IA",
        "codigo": "HEOS-BI-01",
        "kpi": {
            "IGE": ige,
            "salud_flota": round(salud_flota, 1),
            "salud_financiera": round(salud_fin, 1),
            "salud_mantenimiento": round(salud_mnt, 1),
            "salud_seguridad": round(salud_seg, 1),
        },
        "alertas": [],
        "recomendaciones": [],
    }


# Registro de directores para el Orchestrator
DIRECTORES = {
    "operaciones": director_operaciones,
    "financiero": director_financiero,
    "mantenimiento": director_mantenimiento,
    "comercial": director_comercial,
    "compras": director_compras,
    "inventario": director_inventario,
    "rrhh": director_rrhh,
    "seguridad": director_seguridad,
    "bi": director_bi,
}
