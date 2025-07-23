"""
Pipeline de Extracción y Transformación de Pagos desde Supabase
Ubicación sugerida: ia/data_science/Pipelines/pipeline_pagos.py

Este script extrae los pagos reales desde la tabla 'pago' en Supabase,
calcula días de retraso y guarda el resultado en el Data Lake CSV.
"""

import pandas as pd
from supabase import create_client
from datetime import datetime
from supabase import create_client, Client
import os

# 🔐 Conexion a Supabase
SUPABASE_URL = "https://brrxvwgjkuofcgdnmnfb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Extraer la tabla 'pago'
response = supabase.table('pago').select('*').execute()
pagos_data = response.data
pagos_df = pd.DataFrame(pagos_data)

# Asegurar formato datetime
pagos_df['fecha_pago'] = pd.to_datetime(pagos_df['fecha_pago'], errors='coerce')
pagos_df['fecha_vencimiento'] = pd.to_datetime(pagos_df['fecha_vencimiento'], errors='coerce')

# Calcular días de retraso
pagos_df['dias_retraso'] = (pagos_df['fecha_pago'] - pagos_df['fecha_vencimiento']).dt.days
pagos_df['dias_retraso'] = pagos_df['dias_retraso'].apply(lambda x: max(x, 0) if pd.notnull(x) else None)

# Renombrar columnas para estandarizar con el pipeline actual
pagos_df.rename(columns={
    'monto_pago': 'monto',
    'fecha_vencimiento': 'fecha_limite'
}, inplace=True)

# Guardar en el Data Lake CSV
os.makedirs('../../Data_Lake_CSV', exist_ok=True)
csv_path = '../../Data_Lake_CSV/pagos_supabase.csv'
pagos_df.to_csv(csv_path, index=False)

print(f"✅ Pagos extraídos y procesados. Archivo guardado en: {csv_path}")
