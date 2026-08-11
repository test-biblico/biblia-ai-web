"""HEOS-AI — CLI principal (AGT_MASTER_ORCHESTRATOR).

Uso:
  python heos.py cargar      # carga datos de ejemplo (Constructora XYZ)
  python heos.py init        # línea base (FASE 5 manual 040)
  python heos.py informe     # informe ejecutivo + Command Center (texto)
  python heos.py dashboard   # genera dashboard.html
  python heos.py ciclo       # ejecuta un ciclo completo de decisión
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from db import database, seed
from core import orchestrator
from core import dashboards


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
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
