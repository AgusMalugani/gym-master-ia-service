"""
Pipeline de Carga al Data Lake - Gym Master
-------------------------------------------

Este pipeline:
1. Ejecuta el ETL para un gimnasio o varios.
2. Consolida los datos.
3. Carga cada tabla en formato Parquet en la carpeta correspondiente del Data Lake.

Output:
- ia/data_science/Data_Lake/Processed/usuarios/
- ia/data_science/Data_Lake/Processed/asistencias/
- ia/data_science/Data_Lake/Processed/rutinas/
- ia/data_science/Data_Lake/Processed/logs_uso/  (vacío en esta versión si no hay logs)

Uso:
$ python ia/data_science/Pipelines/pipeline_carga_data_lake.py
"""

import sys
import os
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '../../..'))
sys.path.insert(0, PROJECT_ROOT)

from ia.data_science.ETL.etl_login import run_etl

# Path base del Data Lake
DATA_LAKE_PATH = os.path.join(PROJECT_ROOT, 'ia', 'data_science', 'Data_Lake', 'Processed')


def guardar_parquet(df: pd.DataFrame, tabla: str, gimnasio: str):
    """Guarda el DataFrame en la carpeta correspondiente del Data Lake."""
    tabla_path = os.path.join(DATA_LAKE_PATH, tabla)
    os.makedirs(tabla_path, exist_ok=True)

    output_file = os.path.join(tabla_path, f'{gimnasio}_{tabla}.parquet')
    df.to_parquet(output_file, index=False)
    print(f"✅ {tabla} guardado en: {output_file}")


def main():
    gimnasio = "gym_master"
    print(f"🚀 Iniciando carga al Data Lake para: {gimnasio}")

    data = run_etl(gimnasio)

    # Guardar cada tabla
    guardar_parquet(data['usuario'], 'usuarios', gimnasio)
    guardar_parquet(data['asistencia'], 'asistencias', gimnasio)
    guardar_parquet(data['rutina'], 'rutinas', gimnasio)

    # Logs de uso: simulamos vacío por ahora
    logs_df = pd.DataFrame(columns=['log_id', 'gimnasio', 'usuario_id', 'accion', 'detalle', 'fecha_hora'])
    guardar_parquet(logs_df, 'logs_uso', gimnasio)

    print(f"\n✅ Carga al Data Lake completada para: {gimnasio}")


if __name__ == "__main__":
    main()
