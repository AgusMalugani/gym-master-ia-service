"""
Pipeline de ETL + Informe de Retención - Gym Master
---------------------------------------------------

Este pipeline ejecuta:
1. ETL para un gimnasio específico.
2. Informe de retención de usuarios por rol.
3. Guarda el resultado en CSV dentro de la carpeta /output.

Uso:
$ python ia/data_science/Pipelines/pipeline_retencion.py
"""

import sys
import os

# Ajustar el sys.path para importar desde la raíz del proyecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '../../..'))
sys.path.insert(0, PROJECT_ROOT)

from ia.data_science.ETL.etl_login import run_etl
from ia.data_science.Informes.informes_retencion import calcular_retencion_por_rol


def main():
    gimnasio = "gym_master"
    print(f"🚀 Iniciando pipeline para: {gimnasio}")

    data = run_etl(gimnasio)
    usuario_df = data['usuario']

    print("📊 Generando informe de retención por rol...")
    retencion_df = calcular_retencion_por_rol(usuario_df)

    # Crear carpeta output si no existe
    output_dir = os.path.join(PROJECT_ROOT, 'output')
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f'{gimnasio}_retencion_usuarios.csv')
    retencion_df.to_csv(output_file, index=False)
    print(f"✅ Informe de retención guardado en: {output_file}")


if __name__ == "__main__":
    main()
