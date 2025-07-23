"""
ETL Supabase para Gym Master
----------------------------

Este script se conecta a la base de datos de Supabase de un gimnasio específico,
extrae las tablas usuario, asistencia y rutina, les agrega una columna 'gimnasio' 
para identificar la fuente de datos y guarda los resultados en archivos CSV 
dentro de la carpeta /output/etl.

Requisitos:
- pandas
- supabase-py
"""

import pandas as pd
import os
from supabase import create_client, Client

# --- Parámetros de conexión ---
SUPABASE_URL = "https://brrxvwgjkuofcgdnmnfb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Detectar la raíz del proyecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '../../..'))

def extract_table(table_name: str, gimnasio: str) -> pd.DataFrame:
    """Extrae una tabla desde Supabase y agrega columna de gimnasio"""
    response = supabase.table(table_name).select("*").execute()
    data = response.data
    df = pd.DataFrame(data)
    df['gimnasio'] = gimnasio
    return df


def run_etl(gimnasio: str) -> dict:
    print(f"🔍 Extrayendo datos para el gimnasio: {gimnasio}")
    
    usuario_df = extract_table('usuario', gimnasio)
    asistencia_df = extract_table('asistencia', gimnasio)
    rutina_df = extract_table('rutina', gimnasio)

    # Crear carpeta output/etl si no existe
    output_dir = os.path.join(PROJECT_ROOT, 'output', 'etl')
    os.makedirs(output_dir, exist_ok=True)

    usuario_df.to_csv(os.path.join(output_dir, f'{gimnasio}_usuario.csv'), index=False)
    asistencia_df.to_csv(os.path.join(output_dir, f'{gimnasio}_asistencia.csv'), index=False)
    rutina_df.to_csv(os.path.join(output_dir, f'{gimnasio}_rutina.csv'), index=False)
    
    print("✅ Extracción y guardado completo en output/etl.")
    
    return {
        'usuario': usuario_df,
        'asistencia': asistencia_df,
        'rutina': rutina_df
    }


if __name__ == "__main__":
    gimnasio = "gym_master"  
    run_etl(gimnasio)
