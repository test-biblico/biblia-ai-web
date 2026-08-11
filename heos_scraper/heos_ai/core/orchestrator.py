"""AGT_MASTER_ORCHESTRATOR (FASE 1 del manual 040) + DIRECTOR GENERAL IA (CEO AI, Cap 2).

Coordina a los Directores IA, aplica el motor de prioridades (Cap 2.7),
gestiona la memoria de 5 niveles (Cap 2.5) y emite el Informe Ejecutivo
y el HEOS COMMAND CENTER (Cap 7).
"""
import datetime as _dt
from db.database import q, execute, q1
from core import directors


PESO_NIVEL = {"Critico": 4, "Alto": 3, "Medio": 2, "Bajo": 1}


def _ahora():
    return _dt.datetime.now().strftime("%d/%m/%Y %H:%M")


def inicializar():
    """COMANDO DE INICIALIZACIÓN (FASE 5 del manual 040):
    construye línea base, NO emite recomendaciones todavía.
    """
    empresa = q1("SELECT * FROM empresa WHERE id=1")
    if not empresa:
        return "ERROR: base de datos vacía. Ejecute carga de datos primero."
    # Ejecuta a todos los directores para validar que la información es consistente
    estado = {}
    for nombre, fn in directors.DIRECTORES.items():
        try:
            estado[nombre] = fn()
        except Exception as e:  # never break the orchestrator on one bad area
            estado[nombre] = {"error": str(e)}
    linea_base = {
        "fecha": _dt.date.today().isoformat(),
        "empresa": empresa["nombre"],
        "maquinas": q("SELECT COUNT(*) AS n FROM flota")[0]["n"],
        "clientes": q("SELECT COUNT(*) AS n FROM clientes")[0]["n"],
        "ingresos": sum(r["total"] for r in q("SELECT tipo,categoria,SUM(monto) total FROM finanzas GROUP BY tipo,categoria") if r["tipo"] == "Ingreso"),
    }
    # Memoria Estratégica: guardar línea base
    execute(
        "INSERT INTO memoria (nivel, clave, valor_text, fecha) VALUES (?,?,?,?)",
        ("Estrategica", "linea_base", str(linea_base), _dt.datetime.now().isoformat()),
    )
    return linea_base


def ejecutar_ciclo():
    """Ciclo de decisión del CEO AI (Cap 2.6): consulta directores, agrega,
    prioriza y emite recomendaciones (Fase 6 uso diario)."""
    resultado = {"fecha": _ahora(), "areas": {}, "alertas": [], "recomendaciones": []}
    todas_alertas = []
    todas_recs = []

    for nombre, fn in directors.DIRECTORES.items():
        try:
            r = fn()
        except Exception as e:
            r = {"error": str(e)}
        resultado["areas"][nombre] = r
        for a in r.get("alertas", []):
            todas_alertas.append(a)  # (nivel, area, titulo, detalle, impacto)
        for rec in r.get("recomendaciones", []):
            todas_recs.append(rec)

    # Persistir alertas en tabla (motor de reglas)
    for nivel, area, titulo, detalle, impacto in todas_alertas:
        execute(
            "INSERT INTO alertas (nivel, area, titulo, detalle, impacto_gs) VALUES (?,?,?,?,?)",
            (nivel, area, titulo, detalle, impacto or 0),
        )
    # Persistir recomendaciones
    for rec in todas_recs:
        execute(
            """INSERT INTO recomendaciones
               (problema, causa, impacto_gs, riesgo, accion, responsable, beneficio, confianza)
               VALUES (?,?,?,?,?,?,?,?)""",
            (rec.get("problema"), rec.get("causa"), rec.get("impacto_gs", 0),
             rec.get("riesgo"), rec.get("accion"), rec.get("responsable"),
             rec.get("beneficio"), rec.get("confianza", 0)),
        )

    # Ordenar recomendaciones por impacto y prioridad
    todas_recs.sort(key=lambda r: (PESO_NIVEL.get(r.get("riesgo"), 1), r.get("impacto_gs", 0) or 0), reverse=True)
    todas_alertas.sort(key=lambda a: PESO_NIVEL.get(a[0], 1), reverse=True)

    resultado["alertas"] = todas_alertas
    resultado["recomendaciones"] = todas_recs

    # Memoria Operativa: guardar resumen del día
    execute(
        "INSERT INTO memoria (nivel, clave, valor_num, fecha) VALUES (?,?,?,?)",
        ("Operativa", "alertas_hoy", len(todas_alertas), _dt.datetime.now().isoformat()),
    )

    # IGE global desde BI
    bi = resultado["areas"].get("bi", {}).get("kpi", {})
    resultado["IGE"] = bi.get("IGE", 0)
    return resultado


# ============================================================
# INFORMES (FASE 6 / Cap 7)
# ============================================================
def informe_ejecutivo():
    ciclo = ejecutar_ciclo()
    bi = ciclo["areas"].get("bi", {}).get("kpi", {})
    ops = ciclo["areas"].get("operaciones", {}).get("kpi", {})
    fin = ciclo["areas"].get("financiero", {}).get("kpi", {})
    mnt = ciclo["areas"].get("mantenimiento", {}).get("kpi", {})
    seg = ciclo["areas"].get("seguridad", {}).get("kpi", {})

    crit = sum(1 for a in ciclo["alertas"] if a[0] == "Critico")
    alt = sum(1 for a in ciclo["alertas"] if a[0] == "Alto")
    meio = sum(1 for a in ciclo["alertas"] if a[0] == "Medio")

    def barra(pct, ancho=10):
        lleno = int(round(pct / 100 * ancho))
        return "█" * lleno + "░" * (ancho - lleno)

    ige = bi.get("IGE", 0)
    estado = "BUENO" if ige >= 80 else ("REGULAR" if ige >= 60 else "CRÍTICO")

    lines = []
    lines.append("=" * 48)
    lines.append("              HEOS COMMAND CENTER")
    lines.append("=" * 48)
    lines.append("")
    lines.append("SALUD GENERAL EMPRESA")
    lines.append(f"{barra(ige)} {ige}%")
    lines.append("")
    lines.append("💰 FINANZAS")
    lines.append(f"Caja:        {_fmt(fin.get('caja_aprox'))}")
    lines.append(f"Rentabilidad:{fin.get('rentabilidad_pct')}%")
    lines.append("")
    lines.append("⚙ FLOTA")
    lines.append(f"Máquinas:    {ops.get('maquinas_totales')}")
    lines.append(f"Disponibles: {ops.get('disponibles')}")
    lines.append(f"En taller:   {ops.get('en_mantenimiento')+ops.get('fuera_servicio')}")
    lines.append(f"Utilización: {ops.get('utilizacion_pct')}%")
    lines.append("")
    lines.append("👷 PERSONAL")
    lines.append(f"Activos:     {ciclo['areas'].get('rrhh',{}).get('kpi',{}).get('personal_activo')}")
    lines.append(f"Productividad:{ciclo['areas'].get('rrhh',{}).get('kpi',{}).get('productividad_prom')}%")
    lines.append("")
    lines.append("🛡 SEGURIDAD")
    lines.append(f"Safety Score:{seg.get('safety_score')}%")
    lines.append("")
    lines.append("=" * 48)
    lines.append("")
    lines.append("ALERTAS")
    lines.append("")
    lines.append(f"🔴 CRÍTICAS    {crit}")
    lines.append(f"🟠 IMPORTANTES  {alt}")
    lines.append(f"🟡 MEJORAS      {meio}")
    lines.append("")
    lines.append("=" * 48)
    lines.append("")
    lines.append("RECOMENDACIÓN IA DEL DÍA")
    lines.append("")
    if ciclo["recomendaciones"]:
        rec0 = ciclo["recomendaciones"][0]
        lines.append(f"\"{rec0.get('accion')}\"")
        if rec0.get("impacto_gs"):
            lines.append(f"Impacto estimado: {_fmt(rec0['impacto_gs'])}")
    else:
        lines.append("Sin recomendaciones críticas por hoy.")
    lines.append("")
    lines.append("=" * 48)
    return "\n".join(lines), ciclo


def _fmt(n):
    try:
        return f"Gs. {float(n):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "Gs. 0"


def autoevaluacion():
    """Cap 2.9 — autoevaluación diaria del CEO AI."""
    recs = q1("SELECT COUNT(*) AS n FROM recomendaciones WHERE estado='Pendiente'")["n"]
    alertas = q1("SELECT COUNT(*) AS n FROM alertas WHERE estado='Activa'")["n"]
    return {
        "decisiones_acertadas": "Por validar con resultados reales",
        "recomendaciones_pendientes": recs,
        "alertas_activas": alertas,
        "mejora_continua": "Memoria de aprendizaje actualizada tras cada ciclo.",
    }


# ============================================================
# ECOSISTEMA COMPLETO: 60 AGENTES + 250+ SUBAGENTES (Doc 001)
# ============================================================
def _todas_clases_agentes():
    """Recolecta las 60 clases de agentes desde los modulos agents_*."""
    import importlib, pkgutil, inspect
    from core import agents_ops, agents_mnt_fin, agents_com_pr
    clases = []
    for mod in (agents_ops, agents_mnt_fin, agents_com_pr):
        for nombre, obj in inspect.getmembers(mod, inspect.isclass):
            if obj.__module__ == mod.__name__ and issubclass(obj, object) \
               and nombre.startswith("Agente") and hasattr(obj, "run"):
                clases.append(obj)
    # dedupe por nombre
    vistos = set()
    out = []
    for c in clases:
        if c.__name__ not in vistos:
            vistos.add(c.__name__)
            out.append(c)
    return out


def ejecutar_ecosistema():
    """Ejecuta los 60 agentes y los 250+ subagentes; consolida alertas/recs.
    Devuelve dict con conteos y resultados."""
    agentes = _todas_clases_agentes()
    resultados_agentes = []
    alertas = []
    recs = []
    for cls in agentes:
        try:
            inst = cls()
            r = inst.run()
            resultados_agentes.append(r)
            alertas += [(a[0], a[1], a[2], a[3], a[4]) for a in r.get("alertas", [])]
            recs += r.get("recomendaciones", [])
        except Exception as e:
            resultados_agentes.append({"codigo": getattr(cls, "codigo", "?"),
                                       "nombre": cls.__name__, "error": str(e)})

    from core import subagents
    insts_sub = subagents.instancias_subagentes()
    resultados_sub = []
    for s in insts_sub:
        try:
            resultados_sub.append(s.run())
        except Exception as e:
            resultados_sub.append({"codigo": s.codigo, "error": str(e)})

    return {
        "agentes_total": len(agentes),
        "subagentes_total": len(insts_sub),
        "agentes": resultados_agentes,
        "subagentes": resultados_sub,
        "alertas": alertas,
        "recomendaciones": recs,
    }


def resumen_ecosistema():
    eco = ejecutar_ecosistema()
    return (f"ECOSISTEMA HEOS-AI: {eco['agentes_total']} agentes especializados + "
            f"{eco['subagentes_total']} subagentes activos.")

