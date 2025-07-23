"""
Pipeline Comparativo entre Gimnasios - Gym Master
-------------------------------------------------

Este pipeline:
1. Ejecuta el ETL para cada gimnasio configurado.
2. Consolida los datos de todos los gimnasios.
3. Genera informes comparativos:
    - Retención por gimnasio
    - Asistencias promedio por socio
    - Concurrencia promedio por día
    - Concurrencia promedio por hora
4. Guarda cada informe en /output/comparativas.

Uso:
$ python ia/data_science/Pipelines/pipeline_comparativa.py
"""

import sys
import os
import pandas as pd

# Ajustar sys.path para importar desde la raíz
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '../../..'))
sys.path.insert(0, PROJECT_ROOT)

from ia.data_science.ETL.etl_login import run_etl
from ia.data_science.Informes.informes_comparativa import (
    calcular_retencion_por_gimnasio,
    asistencias_promedio_por_socio,
    concurrencia_promedio_por_dia,
    concurrencia_promedio_por_hora
)


def main():
    # --- Configurar gimnasios ---
    gimnasios = [
        {
            'nombre': 'gym_master',
            'supabase_url': "https://brrxvwgjkuofcgdnmnfb.supabase.co",
            'supabase_key': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBh..."
        },
        # Agregar más gimnasios aquí si tenés en el futuro
    ]

    all_usuarios = []
    all_asistencias = []

    print("🚀 Iniciando comparativa entre gimnasios...")

    for gym in gimnasios:
        nombre = gym['nombre']
        print(f"\n🔍 Extrayendo datos para: {nombre}")

        # Asumimos que run_etl ya incluye conexión según gimnasio
        data = run_etl(nombre)
        
        # Agregamos la columna gimnasio por consistencia
        data['usuario']['gimnasio'] = nombre
        data['asistencia']['gimnasio'] = nombre

        all_usuarios.append(data['usuario'])
        all_asistencias.append(data['asistencia'])

    # Consolidar en DataFrames globales
    usuarios_df = pd.concat(all_usuarios, ignore_index=True)
    asistencias_df = pd.concat(all_asistencias, ignore_index=True)

    output_dir = os.path.join(PROJECT_ROOT, 'output', 'comparativas')
    os.makedirs(output_dir, exist_ok=True)

    # --- Generar informes ---
    print("\n📊 Calculando retención por gimnasio...")
    retencion_df = calcular_retencion_por_gimnasio(usuarios_df)
    retencion_df.to_csv(os.path.join(output_dir, 'retencion_por_gimnasio.csv'), index=False)

    print("📊 Calculando asistencias promedio por socio...")
    asistencias_prom_socio_df = asistencias_promedio_por_socio(asistencias_df)
    asistencias_prom_socio_df.to_csv(os.path.join(output_dir, 'asistencias_promedio_por_socio.csv'), index=False)

    print("📊 Calculando concurrencia promedio por día...")
    concurrencia_dia_df = concurrencia_promedio_por_dia(asistencias_df)
    concurrencia_dia_df.to_csv(os.path.join(output_dir, 'concurrencia_promedio_por_dia.csv'), index=False)

    print("📊 Calculando concurrencia promedio por hora...")
    concurrencia_hora_df = concurrencia_promedio_por_hora(asistencias_df)
    concurrencia_hora_df.to_csv(os.path.join(output_dir, 'concurrencia_promedio_por_hora.csv'), index=False)

    print(f"\n✅ Todos los informes comparativos fueron guardados en: {output_dir}")


if __name__ == "__main__":
    main()
