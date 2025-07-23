'''
Script: Evolución Promedio por Objetivo en Gym Master
----------------------------------------------------
Este script analiza la evolución promedio por objetivo de los socios.
Como no hay registro explícito de progreso, se utiliza la cantidad de asistencias mensuales
como proxy de compromiso y progreso.

**Datos requeridos:**
- Tabla `socio`: contiene el campo `objetivo`.
- Tabla `asistencia`: registro de asistencias al gimnasio con fecha.

**Output:**
Un dataframe con:
- Objetivo
- Mes y año
- Promedio de asistencias por socio
'''

from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# --- Configuración de conexión a Supabase ---
# 🔐 Conexión a Supabase
SUPABASE_URL = "https://brrxvwgjkuofcgdnmnfb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Carga de datos desde Supabase ---
print("Cargando datos desde Supabase...")

socios_response = supabase.table('socio').select('id_socio, objetivo').execute()
asistencia_response = supabase.table('asistencia').select('socio_id, fecha').execute()

df_socios = pd.DataFrame(socios_response.data)
df_asistencia = pd.DataFrame(asistencia_response.data)

# --- Procesamiento de fechas ---
df_asistencia['fecha'] = pd.to_datetime(df_asistencia['fecha'])
df_asistencia['año_mes'] = df_asistencia['fecha'].dt.to_period('M')

# --- Calcular asistencias por socio y mes ---
asistencias_mensuales = df_asistencia.groupby(['socio_id', 'año_mes']).size().reset_index(name='asistencias_registradas')

# --- Unir con el objetivo de cada socio ---
df_objetivo = asistencias_mensuales.merge(df_socios, left_on='socio_id', right_on='id_socio', how='left')

# --- Calcular promedio de asistencias por objetivo y mes ---
promedio_objetivo = df_objetivo.groupby(['objetivo', 'año_mes'])['asistencias_registradas'].mean().reset_index(name='promedio_asistencias')

# --- Resultado final ---
print("\nEvolución promedio de asistencias por objetivo:")
print(promedio_objetivo)
