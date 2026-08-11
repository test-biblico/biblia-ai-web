"""Genera el DASHBOARD FINAL CEO y dashboards por área en HTML (Cap 7 y Doc 007)."""
import datetime as _dt
import os
from core import orchestrator
from db.database import q

# Ubicacion de entrega por defecto: Escritorio del usuario
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
DASHBOARD_PATH = os.path.join(DESKTOP, "HEOS_COMMAND_CENTER.html")


def _gs(n):
    try:
        return f"Gs. {float(n):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "Gs. 0"


def _bar(pct, color):
    pct = max(0, min(100, pct))
    return (f'<div class="bar"><div class="fill" style="width:{pct}%;'
            f'background:{color}"></div></div>')


def render_html():
    texto, ciclo = orchestrator.informe_ejecutivo()
    bi = ciclo["areas"].get("bi", {}).get("kpi", {})
    ops = ciclo["areas"].get("operaciones", {})
    fin = ciclo["areas"].get("financiero", {})
    mnt = ciclo["areas"].get("mantenimiento", {})
    com = ciclo["areas"].get("comercial", {})
    hr = ciclo["areas"].get("rrhh", {})
    seg = ciclo["areas"].get("seguridad", {})

    ige = bi.get("IGE", 0)
    alertas = ciclo["alertas"]
    crit = sum(1 for a in alertas if a[0] == "Critico")
    alt = sum(1 for a in alertas if a[0] == "Alto")
    meio = sum(1 for a in alertas if a[0] == "Medio")
    recs_html = ""
    for i, r in enumerate(ciclo["recomendaciones"][:8], 1):
        recs_html += f"""
        <div class="rec">
          <div class="rec-h">#{i} · <b>{r.get('riesgo')}</b> · {r.get('responsable')} · {r.get('confianza')}% conf.</div>
          <div class="rec-prob">⚠ {r.get('problema')}</div>
          <div class="rec-acc">➡ {r.get('accion')}</div>
          <div class="rec-ben">{r.get('beneficio')}</div>
        </div>"""

    alertas_html = ""
    for nivel, area, titulo, detalle, impacto in alertas[:15]:
        color = {"Critico": "#e03131", "Alto": "#f08c00", "Medio": "#f59f00", "Bajo": "#74b816"}[nivel]
        alertas_html += (f'<div class="al" style="border-left:4px solid {color}">'
                         f'<b style="color:{color}">{nivel}</b> · {area} — {titulo}<br>'
                         f'<span class="muted">{detalle}</span></div>')

    ops_k = ops.get("kpi", {})
    fin_k = fin.get("kpi", {})
    mnt_k = mnt.get("kpi", {})
    com_k = com.get("kpi", {})
    hr_k = hr.get("kpi", {})
    seg_k = seg.get("kpi", {})

    html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HEOS COMMAND CENTER — Constructora XYZ</title>
<style>
*{{box-sizing:border-box;font-family:Segoe UI,system-ui,sans-serif}}
body{{margin:0;background:#0f1115;color:#e6e6e6}}
header{{padding:18px 24px;background:linear-gradient(90deg,#10312e,#0f1115);border-bottom:1px solid #1c2b29}}
header h1{{margin:0;font-size:20px;letter-spacing:1px}}
header .sub{{color:#7fd1c4;font-size:13px}}
.wrap{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;padding:20px}}
.card{{background:#171b21;border:1px solid #232a32;border-radius:10px;padding:16px}}
.card h3{{margin:0 0 10px;font-size:13px;color:#9fb3ae;text-transform:uppercase;letter-spacing:1px}}
.big{{font-size:30px;font-weight:700}}
.bar{{height:10px;background:#222a31;border-radius:6px;overflow:hidden;margin-top:8px}}
.fill{{height:100%;border-radius:6px}}
.kpis{{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:#cdd6d3}}
.section{{padding:0 20px 24px}}
.section h2{{font-size:16px;border-bottom:1px solid #232a32;padding-bottom:8px}}
.al{{background:#171b21;border:1px solid #232a32;border-radius:8px;padding:10px 12px;margin:8px 0;font-size:13px}}
.rec{{background:#141a1f;border-left:4px solid #109b8a;padding:10px 12px;margin:10px 0;border-radius:6px}}
.rec-h{{font-size:12px;color:#7fd1c4;margin-bottom:4px}}
.rec-prob{{font-size:14px}}
.rec-acc{{font-size:13px;color:#ffd8a8;margin-top:2px}}
.rec-ben{{font-size:12px;color:#a9c0ba;margin-top:2px}}
.muted{{color:#8a9691;font-size:12px}}
.igebar{{display:flex;align-items:center;gap:12px}}
</style></head>
<body>
<header>
  <h1>HEOS COMMAND CENTER</h1>
  <div class="sub">Constructora XYZ · {_dt.datetime.now().strftime('%d/%m/%Y %H:%M')} · HEOS-AI v1.0</div>
</header>

<div class="wrap">
  <div class="card">
    <h3>Salud General (IGE)</h3>
    <div class="igebar"><div class="big">{ige}%</div></div>
    {_bar(ige, '#109b8a')}
  </div>
  <div class="card">
    <h3>Flota</h3>
    <div class="big">{ops_k.get('maquinas_totales',0)}</div>
    <div class="kpis">
      <span>Disponibles: {ops_k.get('disponibles',0)}</span>
      <span>Trabajando: {ops_k.get('trabajando',0)}</span>
      <span>Taller: {ops_k.get('en_mantenimiento',0)+ops_k.get('fuera_servicio',0)}</span>
      <span>Utilización: {ops_k.get('utilizacion_pct',0)}%</span>
    </div>
  </div>
  <div class="card">
    <h3>Finanzas</h3>
    <div class="big">{_gs(fin_k.get('caja_aprox',0))}</div>
    <div class="kpis">
      <span>Rentabilidad: {fin_k.get('rentabilidad_pct',0)}%</span>
      <span>Ingresos: {_gs(fin_k.get('ingresos',0))}</span>
      <span>Gastos: {_gs(fin_k.get('gastos',0))}</span>
    </div>
  </div>
  <div class="card">
    <h3>Mantenimiento</h3>
    <div class="big">{mnt_k.get('equipos_proximos_servicio',0)}</div>
    <div class="kpis"><span>equipos próximos a servicio</span></div>
  </div>
  <div class="card">
    <h3>Comercial</h3>
    <div class="big">{com_k.get('contratos_activos',0)}</div>
    <div class="kpis">
      <span>Clientes: {com_k.get('clientes',0)}</span>
      <span>Disp. máquinas: {com_k.get('maquinas_disponibles',0)}</span>
      <span>Top: {com_k.get('cliente_top','')}</span>
    </div>
  </div>
  <div class="card">
    <h3>Personal</h3>
    <div class="big">{hr_k.get('personal_activo',0)}</div>
    <div class="kpis">
      <span>Disponibles: {hr_k.get('disponibles',0)}</span>
      <span>Prod: {hr_k.get('productividad_prom',0)}%</span>
    </div>
  </div>
  <div class="card">
    <h3>Seguridad</h3>
    <div class="big">{seg_k.get('safety_score',0)}%</div>
    <div class="kpis"><span>Incidentes ab.: {seg_k.get('incidentes_abiertos',0)}</span></div>
  </div>
  <div class="card">
    <h3>Alertas</h3>
    <div class="kpis">
      <span style="color:#e03131">🔴 {crit}</span>
      <span style="color:#f08c00">🟠 {alt}</span>
      <span style="color:#f59f00">🟡 {meio}</span>
    </div>
  </div>
</div>

<div class="section">
  <h2>🔔 Alertas activas</h2>
  {alertas_html or '<div class="muted">Sin alertas.</div>'}
</div>

<div class="section">
  <h2>🧠 Recomendaciones IA del día</h2>
  {recs_html or '<div class="muted">Sin recomendaciones críticas.</div>'}
</div>
</body></html>"""
    return html


def save_dashboard(path=None):
    if path is None:
        path = DASHBOARD_PATH
    html = render_html()
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
