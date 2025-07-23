'''
Script: Estado Semáforo de Equipamiento en Gym Master
------------------------------------------------------
Este script se conecta a la base de datos Supabase para obtener la información de los equipos
y sus mantenimientos. Genera un indicador de estado tipo semáforo (🟢🟡🔴) para cada equipo
del gimnasio según los siguientes criterios:

- 🟢 Bueno:
    - Última revisión hace menos de 3 meses Y
    - Próxima revisión programada en más de 1 mes.

- 🟡 Atención:
    - Última revisión hace entre 3 y 6 meses O
    - Próxima revisión dentro del próximo mes.

- 🔴 Crítico:
    - Última revisión hace más de 6 meses O
    - Próxima revisión vencida O
    - 2 o más mantenimientos en los últimos 3 meses.

También calcula el total de mantenimientos y el costo acumulado en los últimos 3 meses por equipo.
'''

from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta

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
df_equipos['ultima_revision'] = pd.to_datetime(df_equipos['ultima_revision'])
df_equipos['proxima_revision'] = pd.to_datetime(df_equipos['proxima_revision'])
df_mantenimientos['fecha_mantenimiento'] = pd.to_datetime(df_mantenimientos['fecha_mantenimiento'])

# --- Conteo de mantenimientos y costos últimos 3 meses ---
fecha_hace_3_meses = hoy - timedelta(days=90)
df_mantenimientos_recientes = df_mantenimientos[df_mantenimientos['fecha_mantenimiento'] >= fecha_hace_3_meses]

mantenimientos_summary = df_mantenimientos_recientes.groupby('id_equipamiento').agg(
    mantenimientos_ultimos_3m=('id', 'count'),
    costo_ultimos_3m=('costo', 'sum')
).reset_index()

# --- Unir mantenimientos recientes con equipos ---
df_estado = df_equipos.merge(mantenimientos_summary, how='left', left_on='id', right_on='id_equipamiento')
df_estado[['mantenimientos_ultimos_3m', 'costo_ultimos_3m']] = df_estado[['mantenimientos_ultimos_3m', 'costo_ultimos_3m']].fillna(0)

# --- Clasificación tipo semáforo ---

def clasificar_estado(row):
    if pd.isnull(row['ultima_revision']):
        return '🔴 Crítico'

    meses_desde_revision = (hoy - row['ultima_revision']).days / 30
    dias_proxima_revision = (row['proxima_revision'] - hoy).days if pd.notnull(row['proxima_revision']) else -1

    if meses_desde_revision > 6 or dias_proxima_revision < 0 or row['mantenimientos_ultimos_3m'] >= 2:
        return '🔴 Crítico'
    elif 3 <= meses_desde_revision <= 6 or (0 <= dias_proxima_revision <= 30):
        return '🟡 Atención'
    else:
        return '🟢 Bueno'

df_estado['estado_semaforo'] = df_estado.apply(clasificar_estado, axis=1)

# --- Selección de columnas finales ---
df_resultado = df_estado[[
    'id', 'nombre', 'ultima_revision', 'proxima_revision',
    'mantenimientos_ultimos_3m', 'costo_ultimos_3m', 'estado_semaforo'
]]

# --- Mostrar resultado ---
print("\nEstado actual de los equipos:")
print(df_resultado)

