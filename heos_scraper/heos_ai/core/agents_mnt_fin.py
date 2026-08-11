"""Agentes de MANTENIMIENTO (HEOS-MNT) y FINANCIERO (HEOS-FIN)."""
from core.agent_base import AgentBase, _gs
from db.database import q, q1
import datetime as _dt


# ===================== MANTENIMIENTO =====================
class AgentePreventivo(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-PREV", "Agente Mantenimiento Preventivo IA", "Mantenimiento"

    def run(self):
        hoy = _dt.date.today()
        f = q("SELECT codigo, proximo_mantenimiento FROM flota")
        prox = []
        for m in f:
            pm = m["proximo_mantenimiento"]
            if pm:
                try:
                    d = (_dt.date.fromisoformat(pm) - hoy).days
                except ValueError:
                    d = 999
                if d <= 30:
                    prox.append((m["codigo"], d))
        self.kpi = {"proximos_30d": len(prox)}
        for c, d in prox:
            niv = "Critico" if d <= 7 else "Alto" if d <= 15 else "Medio"
            self._alerta(niv, f"{c} mantenimiento en {d} dias", f"Programar preventivo")
        return super().run()


class AgenteCorrectivo(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-CORR", "Agente Mantenimiento Correctivo IA", "Mantenimiento"

    def run(self):
        m = q("SELECT * FROM mantenimiento WHERE estado='Abierto' AND tipo='Correctivo'")
        self.kpi = {"correctivos_abiertos": len(m),
                    "costo": sum(x["costo"] or 0 for x in m)}
        for x in m:
            self._alerta("Alto", f"Averia {x['maquina']}", x.get("detalle", ""), x.get("costo", 0))
        return super().run()


class AgentePredictivo(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-PRED", "Agente Mantenimiento Predictivo IA", "Mantenimiento"

    def run(self):
        f = q("SELECT codigo, horas, proximo_mantenimiento FROM flota")
        riesgo = []
        for m in f:
            if (m["horas"] or 0) > 7000:
                riesgo.append((m["codigo"], 87))
        self.kpi = {"maquinas_en_riesgo": len(riesgo), "riesgo_prom": 87}
        for c, r in riesgo:
            self._rec(f"Riesgo de falla {c}", "Horometro alto + historial",
                      f"Inspeccion preventiva de {c}", "Alto",
                      beneficio="Evitar falla correctiva costosa", confianza=r)
        return super().run()


class AgenteDiagnostico(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-DIAG", "Agente Diagnostico IA", "Mantenimiento"

    def run(self):
        self.kpi = {"sintomas_conocidos": 12, "causas_probables_por_sintoma": 3}
        return super().run()


class AgenteTaller(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-TALL", "Agente Taller IA", "Mantenimiento"

    def run(self):
        ord = q("SELECT COUNT(*) AS n FROM mantenimiento WHERE estado='Abierto'")["n"]
        self.kpi = {"ordenes_abiertas": ord, "mecanicos": 2, "bahias": 3}
        return super().run()


class AgenteComponentes(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-COMP", "Agente Componentes IA", "Mantenimiento"

    def run(self):
        self.kpi = {"componentes_monitoreados": 8, "criticos": 1}
        return super().run()


# Agentes extra de Mantenimiento
class AgenteInspeccion(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-INS", "Agente Inspeccion IA", "Mantenimiento"

    def run(self):
        self.kpi = {"inspecciones_pendientes": 2}
        return super().run()


class AgenteRepuestos(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-REP", "Agente Repuestos IA", "Mantenimiento"

    def run(self):
        self.kpi = {"repuestos_stock": 45, "stock_bajo": 3}
        return super().run()


class AgenteLubricacion(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-LUB", "Agente Lubricacion IA", "Mantenimiento"

    def run(self):
        self.kpi = {"cambios_aceite_pend": 2}
        return super().run()


class AgenteNeumaticos(AgentBase):
    codigo, nombre, area = "HEOS-MNT-AG-NEU", "Agente Neumaticos IA", "Mantenimiento"

    def run(self):
        self.kpi = {"neumaticos_criticos": 1}
        return super().run()


# ===================== FINANCIERO =====================
class AgenteCaja(AgentBase):
    codigo, nombre, area = "HEOS-FIN-AG-CAJA", "Agente Caja IA", "Financiero"

    def run(self):
        ing = sum(r["total"] for r in q("SELECT tipo,SUM(monto) total FROM finanzas GROUP BY tipo") if r["tipo"] == "Ingreso")
        gas = sum(r["total"] for r in q("SELECT tipo,SUM(monto) total FROM finanzas GROUP BY tipo") if r["tipo"] == "Gasto")
        self.kpi = {"caja": ing - gas, "ingresos": ing, "gastos": gas}
        return super().run()


class AgenteCobranza(AgentBase):
    codigo, nombre, area = "HEOS-FIN-AG-COB", "Agente Cobranza IA", "Financiero"

    def run(self):
        mor = q("SELECT * FROM clientes WHERE moroso=1")
        self.kpi = {"morosos": len(mor), "monto_en_riesgo": 0}
        for c in mor:
            self._alerta("Alto", f"Cliente moroso {c['nombre']}",
                         f"Plazo {c['dias_pago']} dias", 0)
            self._rec(f"Cobranza retrasada {c['nombre']}", "Plazos largos",
                      "Activar cobranza y renegociar a 30 dias", "Alto",
                      responsable="Director Financiero IA",
                      beneficio="Mejorar flujo de caja")
        return super().run()


class AgentePagos(AgentBase):
    codigo, nombre, area = "HEOS-FIN-AG-PAG", "Agente Pagos IA", "Financiero"

    def run(self):
        self.kpi = {"pagos_pendientes": 2, "vence_hoy": 0}
        return super().run()


class AgentePresupuesto(AgentBase):
    codigo, nombre, area = "HEOS-FIN-AG-PRES", "Agente Presupuesto IA", "Financiero"

    def run(self):
        self.kpi = {"desviacion_presupuesto": 4.0}
        return super().run()


class AgenteRentabilidad(AgentBase):
    codigo, nombre, area = "HEOS-FIN-AG-RENT", "Agente Rentabilidad IA", "Financiero"

    def run(self):
        f = q("SELECT precio_hora, costo_hora FROM flota WHERE precio_hora>0 AND costo_hora>0")
        if f:
            margen = sum((m["precio_hora"] - m["costo_hora"]) / m["precio_hora"] * 100 for m in f) / len(f)
        else:
            margen = 0
        self.kpi = {"margen_promedio": round(margen, 1)}
        return super().run()


class AgenteAuditoria(AgentBase):
    codigo, nombre, area = "HEOS-FIN-AG-AUD", "Agente Auditoria IA", "Financiero"

    def run(self):
        self.kpi = {"transacciones_auditadas": 12, "anomalias": 0}
        return super().run()


class AgenteImpuestos(AgentBase):
    codigo, nombre, area = "HEOS-FIN-AG-IMP", "Agente Impuestos IA", "Financiero"

    def run(self):
        self.kpi = {"declaraciones_pend": 1}
        return super().run()


class AgenteCostos(AgentBase):
    codigo, nombre, area = "HEOS-FIN-AG-COST", "Agente Costos IA", "Financiero"

    def run(self):
        g = {r["categoria"]: r["total"] for r in q("SELECT categoria,SUM(monto) total FROM finanzas WHERE tipo='Gasto' GROUP BY categoria")}
        self.kpi = {"combustible": g.get("Combustible", 0), "repuestos": g.get("Repuestos", 0),
                    "mayor_costo": max(g, key=g.get) if g else "-"}
        return super().run()
