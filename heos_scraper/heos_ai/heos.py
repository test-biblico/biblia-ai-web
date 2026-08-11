"""HEOS-AI — CLI principal (AGT_MASTER_ORCHESTRATOR).

Uso:
  python heos.py cargar      # carga datos de ejemplo (Constructora XYZ)
  python heos.py init        # línea base (FASE 5 manual 040)
  python heos.py informe     # informe ejecutivo + Command Center (texto)
  python heos.py dashboard   # genera dashboard.html
  python heos.py ciclo       # ejecuta un ciclo completo de decisión
  python heos.py auto        # ejecuta automatizaciones + notificaciones (FASE 7)
  python heos.py todo        # FLUJO COMPLETO: cargar->init->ciclo->auto->dashboard->autoeval
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from db import database, seed
from core import orchestrator
from core import dashboards
from core import automations


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "informe"
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if cmd == "cargar":
        seed.seed()
    elif cmd == "init":
        database.init_db()
        lb = orchestrator.inicializar()
        print("Línea base construida:")
        print(lb)
    elif cmd == "informe":
        database.init_db()
        texto, _ = orchestrator.informe_ejecutivo()
        print(texto)
    elif cmd == "dashboard":
        database.init_db()
        path = dashboards.save_dashboard()
        print("Dashboard generado:", os.path.abspath(path))
    elif cmd == "ciclo":
        database.init_db()
        ciclo = orchestrator.ejecutar_ciclo()
        print(f"Ciclo {ciclo['fecha']} | IGE={ciclo['IGE']} | "
              f"alertas={len(ciclo['alertas'])} | recs={len(ciclo['recomendaciones'])}")
        for nivel, area, titulo, detalle, impacto in ciclo["alertas"][:10]:
            print(f"  [{nivel}] {area}: {titulo}")
    elif cmd == "auto":
        database.init_db()
        acciones = automations.ejecutar_automatizaciones()
        print(f"Automatizaciones disparadas: {len(acciones)}")
        for area, msg in acciones:
            print(f"  [{area}] {msg}")
    elif cmd == "todo":
        flujo_completo()
    else:
        print(__doc__)


def flujo_completo():
    """FLUJO COMPLETO (Fases 2->7 del manual 040)."""
    print("=" * 56)
    print("  HEOS-AI — FLUJO COMPLETO DE IMPLEMENTACION")
    print("=" * 56)

    print("\n[FASE 2/4] Carga de datos (Constructora XYZ)...")
    seed.seed()

    print("[FASE 5] Inicializacion / linea base...")
    database.init_db()
    lb = orchestrator.inicializar()
    print(f"  Empresa: {lb['empresa']} | Maquinas: {lb['maquinas']} | "
          f"Clientes: {lb['clientes']} | Ingresos: Gs. {lb['ingresos']:,.0f}".replace(",", "."))

    print("[CICLO] Ejecucion del Director General IA (CEO)...")
    ciclo = orchestrator.ejecutar_ciclo()
    print(f"  IGE={ciclo['IGE']}% | Alertas={len(ciclo['alertas'])} | "
          f"Recomendaciones={len(ciclo['recomendaciones'])}")
    for nivel, area, titulo, detalle, impacto in ciclo["alertas"][:8]:
        print(f"   [{nivel}] {area}: {titulo}")

    print("[FASE 7] Automatizaciones y notificaciones...")
    acciones = automations.ejecutar_automatizaciones()
    print(f"  Acciones automaticas: {len(acciones)}")
    for area, msg in acciones[:8]:
        print(f"   -> [{area}] {msg[:70]}")

    print("[AUTOEVAL] Autoevaluacion diaria del CEO AI (Cap 2.9)...")
    ae = orchestrator.autoevaluacion()
    print(f"  Recomendaciones pendientes: {ae['recomendaciones_pendientes']} | "
          f"Alertas activas: {ae['alertas_activas']}")

    print("[DASHBOARD] Generando HEOS COMMAND CENTER...")
    path = dashboards.save_dashboard()
    print(f"  Dashboard: {os.path.abspath(path)}")

    print("\n" + "=" * 56)
    print("  FLUJO COMPLETO FINALIZADO")
    print("=" * 56)


if __name__ == "__main__":
    main()
