"""
Pipeline de ETL + Informe de Horarios Más Activos + Heatmap - Gym Master
------------------------------------------------------------------------

Este pipeline:
1. Extrae datos con el ETL.
2. Genera:
    - Informe de asistencias por día de la semana.
    - Informe de asistencias por hora.
    - Heatmap día vs hora.
3. Guarda los resultados en CSV dentro de /output/horarios.
4. Opcional: muestra el heatmap como gráfico.

Uso:
$ python ia/data_science/Pipelines/pipeline_horarios.py
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ajustar el sys.path para importar desde la raíz del proyecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '../../..'))
sys.path.insert(0, PROJECT_ROOT)

from ia.data_science.ETL.etl_login import run_etl


def generar_informe_horarios(asistencia_df: pd.DataFrame) -> dict:
    """Genera el resumen de asistencias por día de la semana y hora de ingreso."""
    
    asistencia_df['dia_semana'] = pd.to_datetime(asistencia_df['fecha']).dt.day_name()
    asistencia_df['hora'] = asistencia_df['hora_ingreso'].astype(str).str[:5]

    asistencia_por_dia = asistencia_df.groupby('dia_semana').size().reset_index(name='total_asistencias')
    asistencia_por_dia = asistencia_por_dia.sort_values(by='total_asistencias', ascending=False)

    asistencia_por_hora = asistencia_df.groupby('hora').size().reset_index(name='total_asistencias')
    asistencia_por_hora = asistencia_por_hora.sort_values(by='hora')

    return {
        'por_dia': asistencia_por_dia,
        'por_hora': asistencia_por_hora
    }


def generar_heatmap_dia_hora(asistencia_df: pd.DataFrame) -> pd.DataFrame:
    """Genera un DataFrame estilo heatmap de asistencias por día de la semana y hora de ingreso."""
    asistencia_df['dia_semana'] = pd.to_datetime(asistencia_df['fecha']).dt.day_name()
    asistencia_df['hora'] = asistencia_df['hora_ingreso'].astype(str).str[:5]
    
    heatmap_df = asistencia_df.pivot_table(
        index='dia_semana',
        columns='hora',
        values='id',
        aggfunc='count',
        fill_value=0
    )
    
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_df = heatmap_df.reindex(dias_orden)

    return heatmap_df


def graficar_heatmap(heatmap_df: pd.DataFrame, gimnasio: str, output_dir: str):
    """Genera y guarda una imagen del heatmap."""
    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_df, cmap="YlGnBu", linewidths=.5, annot=True, fmt='.0f')
    plt.title(f'Heatmap de Asistencias - {gimnasio}')
    plt.ylabel('Día de la Semana')
    plt.xlabel('Hora')
    
    output_image = os.path.join(output_dir, f'{gimnasio}_heatmap_dia_hora.png')
    plt.savefig(output_image)
    plt.close()
    print(f"🖼️  Heatmap gráfico guardado en: {output_image}")


def main():
    gimnasio = "gym_master"
    print(f"🚀 Iniciando pipeline de horarios para: {gimnasio}")

    data = run_etl(gimnasio)
    asistencia_df = data['asistencia']

    print("📊 Generando informe de horarios más activos...")
    informes = generar_informe_horarios(asistencia_df)

    output_dir = os.path.join(PROJECT_ROOT, 'output', 'horarios')
    os.makedirs(output_dir, exist_ok=True)

    informes['por_dia'].to_csv(os.path.join(output_dir, f'{gimnasio}_asistencias_por_dia.csv'), index=False)
    informes['por_hora'].to_csv(os.path.join(output_dir, f'{gimnasio}_asistencias_por_hora.csv'), index=False)
    print(f"✅ Informes por día y hora guardados en: {output_dir}")

    print("🎨 Generando heatmap de concurrencia día vs hora...")
    heatmap_df = generar_heatmap_dia_hora(asistencia_df)

    heatmap_csv = os.path.join(output_dir, f'{gimnasio}_heatmap_dia_hora.csv')
    heatmap_df.to_csv(heatmap_csv)
    print(f"✅ Heatmap en CSV guardado en: {heatmap_csv}")

    # Opcional: generar imagen del heatmap
    graficar_heatmap(heatmap_df, gimnasio, output_dir)


if __name__ == "__main__":
    main()
