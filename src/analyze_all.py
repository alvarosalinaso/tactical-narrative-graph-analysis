"""
Orquestador completo: ejecuta exportaciones y visualizacion del grafo.
"""

import sys


def main():
    print("=" * 60)
    print("  Pipeline: Tactical Narrative Graph Analysis")
    print("=" * 60)

    errors = []

    # 1. Export visualizations (includes graph build, analysis, benchmark, stats, tables)
    print("\n[1/2] Ejecutando export_visualizations...")
    try:
        from export_visualizations import main as export_main
        export_main()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] export_visualizations: {e}")
        errors.append("export_visualizations")

    # 2. Graph builder standalone (render interactive HTML)
    print("\n[2/2] Ejecutando graph_builder (render HTML)...")
    try:
        from graph_builder import analyze_and_visualize, build_graph, load_passing_data
        df = load_passing_data()
        G = build_graph(df)
        analyze_and_visualize(G)
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] graph_builder: {e}")
        errors.append("graph_builder")

    print("\n" + "=" * 60)
    if errors:
        print(f"  Pipeline completado con errores: {', '.join(errors)}")
    else:
        print("  Pipeline completado exitosamente")
    print("=" * 60)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
