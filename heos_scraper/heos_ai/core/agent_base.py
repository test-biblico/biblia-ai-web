"""Framework base de agentes HEOS-AI.

Cada agente/subagente es una UNIDAD DE CALCULO con:
  - identidad (codigo, nombre, area, nivel)
  - run(): devuelve dict con kpi / alertas / recomendaciones / estado
El Orchestrator los invoca a todos y consolida.

Inspirado en los 40 documentos (Doc 001: +60 agentes / 250 subagentes;
Doc 003/004: arquitectura jerarquica; Doc 005-009: funciones por area).
"""
import datetime as _dt
from db.database import q, q1


def _gs(n):
    try:
        return f"Gs. {float(n):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "Gs. 0"


class AgentBase:
    """Clase base. Los agentes reales heredan y sobreescriben run()."""
    codigo = "HEOS-XXX-00"
    nombre = "Agente"
    area = "General"
    nivel = "agente"  # agente | subagente

    def __init__(self):
        self.kpi = {}
        self.alertas = []       # (nivel, area, titulo, detalle, impacto)
        self.recomendaciones = []

    def _alerta(self, nivel, titulo, detalle="", impacto=0):
        self.alertas.append((nivel, self.area, titulo, detalle, impacto))

    def _rec(self, problema, causa, accion, riesgo="Medio", responsable=None,
             beneficio="", impacto=0, confianza=80):
        self.recomendaciones.append({
            "problema": problema, "causa": causa, "accion": accion,
            "riesgo": riesgo, "responsable": responsable or self.nombre,
            "beneficio": beneficio, "impacto_gs": impacto, "confianza": confianza,
        })

    def run(self):
        """Devuelve el dict estandar del agente."""
        return {
            "codigo": self.codigo, "nombre": self.nombre, "area": self.area,
            "nivel": self.nivel, "kpi": self.kpi,
            "alertas": self.alertas, "recomendaciones": self.recomendaciones,
        }

    # ---- helpers de BD reutilizables ----
    def _flota(self):
        return q("SELECT * FROM flota")

    def _metricas_flota(self):
        f = self._flota()
        tot = len(f) or 1
        est = {}
        for m in f:
            est[m["estado"]] = est.get(m["estado"], 0) + 1
        return f, est, tot
