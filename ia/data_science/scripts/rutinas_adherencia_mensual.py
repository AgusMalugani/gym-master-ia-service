'''
Script: Adherencia Mensual a Rutinas en Gym Master
--------------------------------------------------
Este script analiza la adherencia mensual de los socios a las rutinas asignadas.
Para cada socio y mes, calcula el porcentaje de sesiones completadas respecto a las sesiones recomendadas.

**Datos requeridos:**
- Tabla `rutina`: contiene la estructura de la rutina asignada en formato JSON.
- Tabla `asistencia`: registro de asistencias al gimnasio con fecha.

**Nota:** Como la rutina no guarda explícitamente la cantidad de sesiones por semana,
se asume que el campo `contenido` incluye el número de sesiones o puede ser derivado
de la lógica del negocio.

**Output:**
Un dataframe con:
- ID del socio
- Mes y año
- Asistencias registradas
- Sesiones recomendadas en el mes (valor aproximado o extraído del contenido)
- % de adherencia
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

socios_response = supabase.table('socio').select('id_socio, usuario_id').execute()
rutinas_response = supabase.table('rutina').select('id_socio, contenido').execute()
asistencia_response = supabase.table('asistencia').select('socio_id, fecha').execute()

df_socios = pd.DataFrame(socios_response.data)
df_rutinas = pd.DataFrame(rutinas_response.data)
df_asistencia = pd.DataFrame(asistencia_response.data)

# --- Procesamiento de fechas ---
df_asistencia['fecha'] = pd.to_datetime(df_asistencia['fecha'])
df_asistencia['año_mes'] = df_asistencia['fecha'].dt.to_period('M')

# --- Calcular asistencias por socio y mes ---
asistencias_mensuales = df_asistencia.groupby(['socio_id', 'año_mes']).size().reset_index(name='asistencias_registradas')

# --- Extraer sesiones recomendadas ---
# Por ahora, estableceremos un valor fijo de 3 sesiones por semana como placeholder.
df_rutinas['dias_por_semana'] = 3  # TODO: reemplazar con extracción desde 'contenido' si está estructurado.

# --- Unir con rutinas para sesiones recomendadas ---
df_adherencia = asistencias_mensuales.merge(df_rutinas, left_on='socio_id', right_on='id_socio', how='left')

# --- Calcular sesiones recomendadas por mes ---
df_adherencia['sesiones_recomendadas'] = df_adherencia['dias_por_semana'] * 4  # Aproximación mensual

# --- Calcular % de adherencia ---
df_adherencia['porcentaje_adherencia'] = (df_adherencia['asistencias_registradas'] / df_adherencia['sesiones_recomendadas']) * 100

# --- Unir con identificadores de socios ---
df_adherencia = df_adherencia.merge(df_socios, left_on='socio_id', right_on='id_socio', how='left')

# --- Resultado final ---
df_resultado = df_adherencia[[
    'socio_id', 'año_mes', 'asistencias_registradas',
    'sesiones_recomendadas', 'porcentaje_adherencia', 'usuario_id'
]].sort_values(by=['año_mes', 'usuario_id'])

print("\nAdherencia mensual a rutinas:")
print(df_resultado)
