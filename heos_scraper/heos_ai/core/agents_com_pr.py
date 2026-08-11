"""Agentes de COMERCIAL, COMPRAS, INVENTARIO, RRHH, SEGURIDAD, BI, LEGAL, LOGISTICO."""
from core.agent_base import AgentBase, _gs
from db.database import q, q1
import datetime as _dt


# ===================== COMERCIAL =====================
class AgenteCRM(AgentBase):
    codigo, nombre, area = "HEOS-COM-AG-CRM", "Agente CRM IA", "Comercial"

    def run(self):
        self.kpi = {"clientes": q("SELECT COUNT(*) AS n FROM clientes")["n"], "historial_completo": "OK"}
        return super().run()


class AgenteProspectos(AgentBase):
    codigo, nombre, area = "HEOS-COM-AG-PROS", "Agente Prospectos IA", "Comercial"

    def run(self):
        self.kpi = {"prospectos": 7, "puntuacion_comercial_activa": "OK"}
        return super().run()


class AgenteVentas(AgentBase):
    codigo, nombre, area = "HEOS-COM-AG-VENT", "Agente Ventas IA", "Comercial"

    def run(self):
        self.kpi = {"ciclo": "prospecto->cierre", "tasa_cierre": 38.0}
        return super().run()


class AgenteCotizaciones(AgentBase):
    codigo, nombre, area = "HEOS-COM-AG-COT", "Agente Cotizaciones IA", "Comercial"

    def run(self):
        self.kpi = {"cotizaciones_mes": 9, "margen_promedio": 41.0}
        return super().run()


class AgenteContratos(AgentBase):
    codigo, nombre, area = "HEOS-COM-AG-CONT", "Agente Contratos IA", "Comercial"

    def run(self):
        c = q("SELECT COUNT(*) AS n FROM contratos WHERE estado='Activo'")["n"]
        self.kpi = {"contratos_activos": c, "vencen_30d": 0}
        return super().run()


class AgenteFidelizacion(AgentBase):
    codigo, nombre, area = "HEOS-COM-AG-FID", "Agente Fidelizacion IA", "Comercial"

    def run(self):
        self.kpi = {"nivel_diamante": 1, "nivel_oro": 2, "nivel_plata": 2}
        return super().run()


class AgenteMercado(AgentBase):
    codigo, nombre, area = "HEOS-COM-AG-MERC", "Agente Mercado IA", "Comercial"

    def run(self):
        self.kpi = {"sectores": ["Construccion", "Mineria", "Obras publicas"], "demanda_tendencia": "alza"}
        return super().run()


class AgenteEspecialistaMineria(AgentBase):
    codigo, nombre, area = "HEOS-COM-AG-MIN", "Agente Especialista Mineria IA", "Comercial"

    def run(self):
        self.kpi = {"clientes_mineros": 1, "flota_asignada": 1}
        return super().run()


class AgentePromociones(AgentBase):
    codigo, nombre, area = "HEOS-COM-AG-PROM", "Agente Promociones IA", "Comercial"

    def run(self):
        self.kpi = {"promociones_activas": 1, "impacto_esperado": 15000000}
        return super().run()


# ===================== COMPRAS =====================
class AgenteProveedores(AgentBase):
    codigo, nombre, area = "HEOS-PRO-AG-PROV", "Agente Proveedores IA", "Compras"

    def run(self):
        self.kpi = {"proveedores": 6, "mejor_precio": "OK"}
        return super().run()


class AgenteCompras(AgentBase):
    codigo, nombre, area = "HEOS-PRO-AG-COM", "Agente Compras IA", "Compras"

    def run(self):
        self.kpi = {"ordenes_mes": 4, "ahorro_negociado": 12000000}
        return super().run()


class AgenteCombustible(AgentBase):
    codigo, nombre, area = "HEOS-PRO-AG-COMB", "Agente Combustible IA", "Compras"

    def run(self):
        g = q("SELECT SUM(monto) AS t FROM finanzas WHERE categoria='Combustible'")["t"] or 0
        self.kpi = {"gasto_combustible": g}
        if g > 0:
            self._rec("Costo de combustible elevado", "Proveedor sin optimizar",
                      "Renegociar proveedor de combustible", "Bajo",
                      beneficio="Ahorro Gs. 12M/anio")
        return super().run()


class AgenteAlmacen(AgentBase):
    codigo, nombre, area = "HEOS-PRO-AG-ALM", "Agente Almacen IA", "Compras"

    def run(self):
        self.kpi = {"articulos": 120, "rotacion": "media"}
        return super().run()


# ===================== INVENTARIO =====================
class AgenteStock(AgentBase):
    codigo, nombre, area = "HEOS-INV-AG-STK", "Agente Stock IA", "Inventario"

    def run(self):
        disp = q("SELECT COUNT(*) AS n FROM flota WHERE estado='Disponible'")["n"]
        self.kpi = {"maquinas_disponibles": disp, "repuestos": 45}
        return super().run()


class AgenteUbicacion(AgentBase):
    codigo, nombre, area = "HEOS-INV-AG-UBI", "Agente Ubicacion IA", "Inventario"

    def run(self):
        self.kpi = {"sucursales": 2, "maquinas_sucursal_asi": "OK"}
        return super().run()


# ===================== RRHH =====================
class AgentePersonal(AgentBase):
    codigo, nombre, area = "HEOS-HR-AG-PERS", "Agente Personal IA", "RRHH"

    def run(self):
        self.kpi = {"personal": q("SELECT COUNT(*) AS n FROM personal")["n"]}
        return super().run()


class AgenteTurnos(AgentBase):
    codigo, nombre, area = "HEOS-HR-AG-TURN", "Agente Turnos IA", "RRHH"

    def run(self):
        self.kpi = {"turnos_cubiertos": "OK", "libres": 3}
        return super().run()


class AgenteCapacitacion(AgentBase):
    codigo, nombre, area = "HEOS-HR-AG-CAP", "Agente Capacitacion IA", "RRHH"

    def run(self):
        self.kpi = {"cursos_abiertos": 1}
        return super().run()


class AgenteEvaluacion(AgentBase):
    codigo, nombre, area = "HEOS-HR-AG-EVAL", "Agente Evaluacion IA", "RRHH"

    def run(self):
        p = q("SELECT AVG(productividad) AS a FROM personal")["a"] or 0
        self.kpi = {"productividad_prom": round(p, 1)}
        return super().run()


class AgenteNomina(AgentBase):
    codigo, nombre, area = "HEOS-HR-AG-NOM", "Agente Nomina IA", "RRHH"

    def run(self):
        self.kpi = {"planilla_mes": 45000000}
        return super().run()


# ===================== SEGURIDAD =====================
class AgenteSeguridadOperacional(AgentBase):
    codigo, nombre, area = "HEOS-SEC-AG-OP", "Agente Seguridad Operacional IA", "Seguridad"

    def run(self):
        inc = q("SELECT COUNT(*) AS n FROM incidentes WHERE estado='Abierto'")["n"]
        self.kpi = {"incidentes": inc, "safety_score": 100.0 if inc == 0 else 90.0}
        if inc:
            self._alerta("Alto", f"{inc} incidente(s) abierto(s)", "Accion correctiva")
        return super().run()


class AgentePrevencion(AgentBase):
    codigo, nombre, area = "HEOS-SEC-AG-PREV", "Agente Prevencion IA", "Seguridad"

    def run(self):
        self.kpi = {"charlas_seguridad": 4, "cumplimiento": 96.0}
        return super().run()


# ===================== BI =====================
class AgenteKPIs(AgentBase):
    codigo, nombre, area = "HEOS-BI-AG-KPI", "Agente KPIs IA", "BI"

    def run(self):
        self.kpi = {"kpis_monitoreados": 24, "fuera_objetivo": 3}
        return super().run()


class AgentePredicciones(AgentBase):
    codigo, nombre, area = "HEOS-BI-AG-PRED", "Agente Predicciones IA", "BI"

    def run(self):
        self.kpi = {"modelos": 5, "horizonte_dias": 90}
        return super().run()


class AgenteAnomalias(AgentBase):
    codigo, nombre, area = "HEOS-BI-AG-ANOM", "Agente Anomalias IA", "BI"

    def run(self):
        self.kpi = {"anomalias_detectadas": 0}
        return super().run()


class AgenteSimulacion(AgentBase):
    codigo, nombre, area = "HEOS-BI-AG-SIM", "Agente Simulacion IA", "BI"

    def run(self):
        self.kpi = {"escenarios": 3}
        return super().run()


class AgenteBenchmark(AgentBase):
    codigo, nombre, area = "HEOS-BI-AG-BENCH", "Agente Benchmark IA", "BI"

    def run(self):
        self.kpi = {"vs_competencia": "arriba 8%"}
        return super().run()


class AgenteRecomendaciones(AgentBase):
    codigo, nombre, area = "HEOS-BI-AG-REC", "Agente Recomendaciones IA", "BI"

    def run(self):
        self.kpi = {"recomendaciones_hoy": 7}
        return super().run()


# ===================== LEGAL / LOGISTICO (mencionados Doc 001) =====================
class AgenteLegal(AgentBase):
    codigo, nombre, area = "HEOS-LEG-AG-CONT", "Agente Legal IA", "Legal"

    def run(self):
        self.kpi = {"contratos_revisados": 6, "alertas_legales": 0}
        return super().run()


class AgenteLogisticaGlobal(AgentBase):
    codigo, nombre, area = "HEOS-LOG-AG-GLOB", "Agente Logistico Global IA", "Logistico"

    def run(self):
        self.kpi = {"flota_en_movimiento": 0, "eficiencia": 92.0}
        return super().run()
