"""
Pipeline Multi-Gimnasio para Carga al Data Lake - Gym Master
------------------------------------------------------------

Este pipeline:
1. Ejecuta el ETL para cada gimnasio configurado.
2. Consolida y guarda cada tabla en formato Parquet dentro del Data Lake particionado.

Output por gimnasio:
- ia/data_science/Data_Lake/Processed/usuarios/{gimnasio}_usuarios.parquet
- ia/data_science/Data_Lake/Processed/asistencias/{gimnasio}_asistencias.parquet
- ia/data_science/Data_Lake/Processed/rutinas/{gimnasio}_rutinas.parquet
- ia/data_science/Data_Lake/Processed/logs_uso/{gimnasio}_logs_uso.parquet

Uso:
$ python ia/data_science/Pipelines/pipeline_carga_data_lake_multi.py
"""

import sys
import os
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '../../..'))
sys.path.insert(0, PROJECT_ROOT)

from ia.data_science.ETL.etl_login import run_etl

DATA_LAKE_PATH = os.path.join(PROJECT_ROOT, 'ia', 'data_science', 'Data_Lake', 'Processed')


def guardar_parquet(df: pd.DataFrame, tabla: str, gimnasio: str):
    """Guarda un DataFrame en la carpeta correspondiente del Data Lake."""
    tabla_path = os.path.join(DATA_LAKE_PATH, tabla)
    os.makedirs(tabla_path, exist_ok=True)

    output_file = os.path.join(tabla_path, f'{gimnasio}_{tabla}.parquet')
    df.to_parquet(output_file, index=False)
    print(f"✅ {tabla} guardado en: {output_file}")


def main():
    # Lista de gimnasios configurados
    gimnasios = [
        {'nombre': 'gym_master'},
        # Agregar más gimnasios en el futuro
        # {'nombre': 'gym_fit'},
        # {'nombre': 'gym_power'},
    ]

    print("🚀 Iniciando carga multi-gimnasio al Data Lake...")

    for gym in gimnasios:
        gimnasio = gym['nombre']
        print(f"\n🔍 Procesando gimnasio: {gimnasio}")

        data = run_etl(gimnasio)

        guardar_parquet(data['usuario'], 'usuarios', gimnasio)
        guardar_parquet(data['asistencia'], 'asistencias', gimnasio)
        guardar_parquet(data['rutina'], 'rutinas', gimnasio)

        # Logs: vacío por ahora
        logs_df = pd.DataFrame(columns=['log_id', 'gimnasio', 'usuario_id', 'accion', 'detalle', 'fecha_hora'])
        guardar_parquet(logs_df, 'logs_uso', gimnasio)

    print("\n✅ Carga completa para todos los gimnasios configurados.")


if __name__ == "__main__":
    main()
