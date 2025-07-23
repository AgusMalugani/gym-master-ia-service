'''
Script: Ranking de Fallos de Equipamiento en Gym Master
------------------------------------------------------
Este script se conecta a Supabase para obtener la información de mantenimientos de los equipos
y genera un ranking de fallos basado en la cantidad y el costo acumulado de mantenimientos correctivos.

Consideramos cada mantenimiento de tipo "correctivo" como un fallo.

El ranking resultante incluye:
- ID y nombre del equipo.
- Total de fallos (correctivos).
- Costo total asociado.
- Ranking por cantidad de fallos (descendente).
'''

from supabase import create_client, Client
import pandas as pd

# --- Configuración de conexión a Supabase ---
SUPABASE_URL = "https://brrxvwgjkuofcgdnmnfb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Carga de datos desde Supabase ---
print("Cargando datos desde Supabase...")

equipos_response = supabase.table('equipamiento').select('id, nombre').execute()
mantenimientos_response = supabase.table('mantenimiento').select('*').execute()

df_equipos = pd.DataFrame(equipos_response.data)
df_mantenimientos = pd.DataFrame(mantenimientos_response.data)

# --- Filtrar mantenimientos correctivos ---
df_correctivos = df_mantenimientos[df_mantenimientos['tipo_mantenimiento'] == 'correctivo']

# --- Agrupar por equipo: cantidad de fallos y costo total ---
fallos_summary = df_correctivos.groupby('id_equipamiento').agg(
    total_fallos=('id', 'count'),
    costo_total=('costo', 'sum')
).reset_index()

# --- Unir con nombres de equipos ---
fallos_summary = fallos_summary.merge(df_equipos, how='left', left_on='id_equipamiento', right_on='id')

# --- Agregar ranking ---
fallos_summary['ranking'] = fallos_summary['total_fallos'].rank(method='dense', ascending=False).astype(int)

# --- Ordenar por ranking ---
fallos_summary = fallos_summary.sort_values(by='ranking')

# --- Selección de columnas finales ---
df_resultado = fallos_summary[[
    'id_equipamiento', 'nombre', 'total_fallos', 'costo_total', 'ranking'
]]

# --- Mostrar resultado ---
print("\nRanking de fallos de equipamiento:")
print(df_resultado)