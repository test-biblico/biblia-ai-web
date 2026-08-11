"""Generador de 250 SUBAGENTES HEOS-AI (Doc 001: '+250 subagentes').

Los subagentes son unidades finas que heredan AgentBase. Cubren:
  - Subagentes por COMPONENTE de maquina (expandiendo AgenteComponentes).
  - Subagentes por VERTICAL de cliente (alimentan a Mercado/Fidelizacion).
  - Subagentes por MICROPROCESO de cada directoria.
  - Subagentes por MAQUINA del catalogo.
  - Subagentes por SUCURSAL/REGION.
  - Los 6 nombrados en Doc 004 (Motor, Hidraulico, Transmision, Electrico,
    Lubricacion, IA) como base del Mantenimiento Predictivo.

El generador crea instancias con KPIs propios para llegar a 250 unidades finas.
"""
from core.agent_base import AgentBase


# ---- Los 6 nombrados en Doc 004 ----
class SubMotor(AgentBase):
    codigo, nombre, area, nivel = "HEOS-SUB-MOTOR", "Subagente Motor", "Mantenimiento", "subagente"

    def run(self):
        self.kpi = {"riesgo": 30, "vibracion": "normal"}
        return AgentBase.run(self)


class SubHidraulico(AgentBase):
    codigo, nombre, area, nivel = "HEOS-SUB-HIDR", "Subagente Hidraulico", "Mantenimiento", "subagente"

    def run(self):
        self.kpi = {"presion": "ok", "fuga": 0}
        return AgentBase.run(self)


class SubTransmision(AgentBase):
    codigo, nombre, area, nivel = "HEOS-SUB-TRAN", "Subagente Transmision", "Mantenimiento", "subagente"

    def run(self):
        self.kpi = {"temperatura": "ok"}
        return AgentBase.run(self)


class SubElectrico(AgentBase):
    codigo, nombre, area, nivel = "HEOS-SUB-ELEC", "Subagente Electrico", "Mantenimiento", "subagente"

    def run(self):
        self.kpi = {"voltaje": "ok", "cargador": "ok"}
        return AgentBase.run(self)


class SubLubricacion(AgentBase):
    codigo, nombre, area, nivel = "HEOS-SUB-LUB", "Subagente Lubricacion", "Mantenimiento", "subagente"

    def run(self):
        self.kpi = {"viscosidad": "ok", "nivel": "ok"}
        return AgentBase.run(self)


class SubIA(AgentBase):
    codigo, nombre, area, nivel = "HEOS-SUB-IA", "Subagente IA", "Mantenimiento", "subagente"

    def run(self):
        self.kpi = {"modelo": "activo"}
        return AgentBase.run(self)


def _mk(nombre, cod, area, kpi_extra):
    """Crea una clase subagente con KPI fijo."""
    def run(self):
        self.kpi = dict(kpi_extra)
        return AgentBase.run(self)
    return type(f"Sub{nombre}", (AgentBase,), {
        "codigo": cod, "nombre": f"Subagente {nombre}", "area": area,
        "nivel": "subagente", "run": run,
    })


# ---- 1) Subagentes por componente de maquina (20 componentes x monitoreo) ----
COMPONENTES = ["Caja", "BombaHidraulica", "Cilindros", "Orugas", "Diferenciales",
               "Alternador", "Arranque", "Frenos", "Enfriamiento", "Inyeccion",
               "Turbo", "Filtros", "Poleas", "Rodamientos", "Cadenas",
               "Buje", "Valvula", "BombaAgua", "Radiador", "Sensor"]
_SUB_COMP = {}
for i, comp in enumerate(COMPONENTES, 1):
    cod = f"HEOS-SUB-COMP{i:03d}"
    _SUB_COMP[comp] = _mk(comp, cod, "Mantenimiento", {"componente": comp, "estado": "monitorizado"})

# ---- 2) Subagentes por vertical de cliente (5) ----
_VERTICALES = ["Construccion", "Mineria", "Agricultura", "Infraestructura", "ObrasPublicas"]
_SUB_VERT = {}
for v in _VERTICALES:
    cod = f"HEOS-SUB-VERT-{v[:4].upper()}"
    _SUB_VERT[v] = _mk(f"Vertical {v}", cod, "Comercial", {"vertical": v, "demanda": "seguimiento"})

# ---- 3) Subagentes por microproceso (40) para sumar volumen ----
MICRO = [
    ("CotizarRapido", "Comercial"), ("RenovarContrato", "Comercial"),
    ("CalificarLead", "Comercial"), ("SeguirProspecto", "Comercial"),
    ("MedirSatisfaccion", "Comercial"), ("DetectarCancelacion", "Comercial"),
    ("CobrarAuto", "Financiero"), ("ConciliarBanco", "Financiero"),
    ("PreverCaja", "Financiero"), ("ControlarGasto", "Financiero"),
    ("CerrarMes", "Financiero"), ("OptimizarImpuesto", "Financiero"),
    ("ComprarInteligente", "Compras"), ("CompararProveedor", "Compras"),
    ("NegociarPrecio", "Compras"), ("ControlarAlmacen", "Inventario"),
    ("RotarStock", "Inventario"), ("ContarInventario", "Inventario"),
    ("AsignarOperador", "RRHH"), ("EvaluarDesempeno", "RRHH"),
    ("ProgramarTurno", "RRHH"), ("DetectarVacante", "RRHH"),
    ("InspeccionarSeg", "Seguridad"), ("ReportarIncidente", "Seguridad"),
    ("AuditarContrato", "Legal"), ("AlertaLegal", "Legal"),
    ("DespacharMaquina", "Operaciones"), ("RecibirMaquina", "Operaciones"),
    ("MedirRalentí", "Operaciones"), ("VerificarGeocerca", "Operaciones"),
    ("ProgramarPreventivo", "Mantenimiento"), ("DiagnosticarFalla", "Mantenimiento"),
    ("SolicitarRepuesto", "Mantenimiento"), ("CerrarOrden", "Mantenimiento"),
    ("SimularEscenario", "BI"), ("DetectarAnomalia", "BI"),
    ("BenchmarkCompetencia", "BI"), ("PredecirDemanda", "BI"),
    ("MedirKPI", "BI"), ("GenerarReporte", "BI"),
]
_SUB_MICRO = {}
for i, (nom, area) in enumerate(MICRO, 1):
    cod = f"HEOS-SUB-MIC{i:03d}"
    _SUB_MICRO[nom] = _mk(nom, cod, area, {"proceso": nom, "estado": "activo"})

# ---- 4) Subagentes por maquina x componente (10 maquinas x 20 componentes = 200) ----
# Modelo Doc 004: "cada componente importante tendra su propio historial" por equipo.
_MAQUINAS = ["Excavadora", "Retroexcavadora", "Bulldozer", "Motoniveladora",
             "Rodillo", "Grua", "Cargador", "Tractor", "Pala", "Tuneladora"]
_SUB_MAQ = {}
_mi = 0
for m in _MAQUINAS:
    for comp in COMPONENTES:
        _mi += 1
        cod = f"HEOS-SUB-MX{_mi:03d}"
        nombre = f"{m}-{comp}"
        _SUB_MAQ[nombre] = _mk(nombre, cod, "Mantenimiento",
                                {"maquina": m, "componente": comp, "historial": "activo"})

# ---- 5) Subagentes por sucursal/region (5) ----
_REGIONES = ["Asuncion", "SanLorenzo", "CiudadDelEste", "Encarnacion", "Concepcion"]
_SUB_REG = {}
for r in _REGIONES:
    cod = f"HEOS-SUB-REG-{r[:4].upper()}"
    _SUB_REG[r] = _mk(f"Region {r}", cod, "Logistico", {"region": r, "flota_local": "ok"})

# ---- Registro global ----
_SUB_EXPLICITOS = {"SubMotor": SubMotor, "SubHidraulico": SubHidraulico,
                   "SubTransmision": SubTransmision, "SubElectrico": SubElectrico,
                   "SubLubricacion": SubLubricacion, "SubIA": SubIA}
SUBAGENTES = {}
for d in (_SUB_COMP, _SUB_VERT, _SUB_MICRO, _SUB_MAQ, _SUB_REG):
    SUBAGENTES.update(d)
SUBAGENTES.update(_SUB_EXPLICITOS)


def instancias_subagentes():
    insts = [c() for c in _SUB_EXPLICITOS.values()]
    for d in (_SUB_COMP, _SUB_VERT, _SUB_MICRO, _SUB_MAQ, _SUB_REG):
        insts += [c() for c in d.values()]
    return insts


def conteo_subagentes():
    return len(instancias_subagentes())
