'''
Script: Análisis Costo-Beneficio de Mantenimiento en Equipamiento Gym Master
------------------------------------------------------
Este script se conecta a Supabase para calcular el costo-beneficio de mantenimiento de cada equipo,
evaluando si es rentable seguir manteniendo el equipo o si es mejor reemplazarlo.

Para cada equipo, el script calcula:
- Antigüedad en años.
- Costo total de mantenimientos.
- Costo promedio anual de mantenimiento.
- Relación costo-beneficio (costo anual / valor estimado de reposición).

**Nota:** Este script asume que el valor estimado de reposición se encuentra en un campo opcional llamado
`valor_reposicion` en la tabla `equipamiento`. Si no existe, se puede agregar o definir un valor promedio por tipo de equipo.
'''

from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# --- Configuración de conexión a Supabase ---
SUPABASE_URL = "https://brrxvwgjkuofcgdnmnfb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Carga de datos desde Supabase ---
print("Cargando datos desde Supabase...")

equipos_response = supabase.table('equipamiento').select('*').execute()
mantenimientos_response = supabase.table('mantenimiento').select('*').execute()

df_equipos = pd.DataFrame(equipos_response.data)
df_mantenimientos = pd.DataFrame(mantenimientos_response.data)

# --- Procesamiento de fechas ---
hoy = datetime.now()
df_equipos['fecha_adquisicion'] = pd.to_datetime(df_equipos['fecha_adquisicion'])
df_mantenimientos['fecha_mantenimiento'] = pd.to_datetime(df_mantenimientos['fecha_mantenimiento'])

# --- Costo total de mantenimientos por equipo ---
mantenimientos_summary = df_mantenimientos.groupby('id_equipamiento').agg(
    costo_total_mantenimiento=('costo', 'sum')
).reset_index()

# --- Unir mantenimientos con equipos ---
df_estado = df_equipos.merge(mantenimientos_summary, how='left', left_on='id', right_on='id_equipamiento')
df_estado['costo_total_mantenimiento'] = df_estado['costo_total_mantenimiento'].fillna(0)

# --- Cálculo de antigüedad y costo promedio anual ---
df_estado['antiguedad_anios'] = df_estado['fecha_adquisicion'].apply(lambda x: (hoy - x).days / 365 if pd.notnull(x) else 0)
df_estado['costo_promedio_anual'] = df_estado.apply(
    lambda row: row['costo_total_mantenimiento'] / row['antiguedad_anios'] if row['antiguedad_anios'] > 0 else 0,
    axis=1
)

# --- Costo-beneficio: se asume valor_reposicion en tabla equipamiento ---
if 'valor_reposicion' not in df_estado.columns:
    df_estado['valor_reposicion'] = 1000  # valor estimado si no existe el campo

df_estado['costo_beneficio_ratio'] = df_estado.apply(
    lambda row: row['costo_promedio_anual'] / row['valor_reposicion'] if row['valor_reposicion'] > 0 else 0,
    axis=1
)

# --- Resultado final ---
df_resultado = df_estado[[
    'id', 'nombre', 'fecha_adquisicion', 'antiguedad_anios',
    'costo_total_mantenimiento', 'costo_promedio_anual',
    'valor_reposicion', 'costo_beneficio_ratio'
]]

# --- Mostrar resultado ---
print("\nAnálisis Costo-Beneficio de Mantenimiento:")
print(df_resultado)