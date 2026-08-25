"""
Orquestador completo: ejecuta todos los scripts de análisis en orden.
"""

import sys


def main():
    print("=" * 60)
    print("  Pipeline completo: Tactical Narrative Graph Analysis")
    print("=" * 60)

    errors = []

    # 1. Export visualizations (includes graph build, analysis, benchmark)
    print("\n[1/4] Ejecutando export_visualizations...")
    try:
        from export_visualizations import main as export_main

        export_main()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] export_visualizations: {e}")
        errors.append("export_visualizations")

    # 2. Statistical tests
    print("\n[2/4] Ejecutando statistical_tests...")
    try:
        from statistical_tests import run_statistical_tests

        run_statistical_tests()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] statistical_tests: {e}")
        errors.append("statistical_tests")

    # 3. Generate tables
    print("\n[3/4] Ejecutando generate_tables...")
    try:
        from generate_tables import generate as generate_exec_tables

        generate_exec_tables()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] generate_tables: {e}")
        errors.append("generate_tables")

    # 4. Graph builder standalone (render HTML graph)
    print("\n[4/4] Ejecutando graph_builder (render HTML)...")
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
