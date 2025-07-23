"""
Pipeline de Detección de Inactividad / Abandono - Gym Master
------------------------------------------------------------

Este pipeline:
1. Ejecuta el ETL para un gimnasio o lista de gimnasios.
2. Detecta los socios que no asistieron en las últimas N semanas.
3. Guarda el informe en /output/abandono.

Uso:
$ python ia/data_science/Pipelines/pipeline_abandono.py
"""

import sys
import os
import pandas as pd

# Ajustar sys.path para importar desde la raíz
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '../../..'))
sys.path.insert(0, PROJECT_ROOT)

from ia.data_science.ETL.etl_login import run_etl
from ia.data_science.Informes.informes_abandono import detectar_inactividad


def main():
    gimnasio = "gym_master"
    semanas_umbral = 4  # Número de semanas sin asistir para marcar inactividad

    print(f"🚀 Iniciando pipeline de abandono para: {gimnasio}")
    print(f"⚠️  Umbral de inactividad: {semanas_umbral} semanas")

    # --- ETL ---
    data = run_etl(gimnasio)
    asistencia_df = data['asistencia']
    asistencia_df['gimnasio'] = gimnasio  # aseguramos columna gimnasio

    # --- Detección de inactividad ---
    print("🔎 Detectando socios inactivos...")
    abandono_df = detectar_inactividad(asistencia_df, semanas_umbral=semanas_umbral)

    # --- Guardar resultados ---
    output_dir = os.path.join(PROJECT_ROOT, 'output', 'abandono')
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f'{gimnasio}_socios_inactivos.csv')
    abandono_df.to_csv(output_file, index=False)
    print(f"✅ Informe de inactividad guardado en: {output_file}")


if __name__ == "__main__":
    main()
