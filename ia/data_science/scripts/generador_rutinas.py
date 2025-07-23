# ✅ GENERADOR DE RUTINAS SEMANALES PERSONALIZADAS
#
# Este script genera rutinas de entrenamiento semanales personalizadas para cada socio.
# Está integrado con Supabase (PostgreSQL) y utiliza un modelo de lógica configurable.
#
# 🔹 Funcionalidades:
# - Conexión a Supabase para obtener:
#   • Tabla `socio` (nivel, objetivo, días por semana)
#   • Tabla `ejercicio` con relaciones a `nivel`, `objetivo` y `grupo_muscular`
# - Generación de una rutina semanal personalizada:
#   • Evita repetir grupos musculares consecutivos
#   • Días con 1 grupo → 6 ejercicios
#   • Días con 2 grupos → 8 ejercicios (4 por grupo)
# - Formato de salida: JSON estructurado con días y ejercicios
# - Guardado:
#   • Localmente como archivo `.json`
#   • Remotamente en la tabla `rutina` de Supabase (`rutina_desc`)
#
# 💡 Uso:
# Ejecutar este script para generar o actualizar la rutina semanal de todos los socios registrados.



import pandas as pd
import json
import random
import os
from supabase import create_client, Client

# Conexión a Supabase
SUPABASE_URL = "https://brrxvwgjkuofcgdnmnfb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Crear carpeta para guardar los JSON si no existe
os.makedirs("rutinas", exist_ok=True)

# Cargar datos desde Supabase
def cargar_datos_supabase():
    tablas = ["ejercicio", "nivel", "objetivo", "grupo_muscular", "socio"]
    datos = {}
    for tabla in tablas:
        response = supabase.table(tabla).select("*").execute()
        datos[tabla] = pd.DataFrame(response.data)
    return datos

# Generar rutina semanal con 6/8 ejercicios según grupos musculares
def generar_rutina(ejercicios, dias_por_semana=3, id_socio=None):
    grupos = list(ejercicios["grupo_muscular"].unique())
    if len(grupos) < 1:
        print(f"⚠️ No hay grupos musculares disponibles para el socio {id_socio}.")
        return None

    semana = {}
    dias_disponibles = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
    random.shuffle(dias_disponibles)
    dias_usados = dias_disponibles[:dias_por_semana]

    for dia in dias_usados:
        ejercicios_dia = []
        usar_dos_grupos = random.choice([True, False])
        grupos_dia = random.sample(grupos, 2 if usar_dos_grupos and len(grupos) >= 2 else 1)

        for grupo in grupos_dia:
            ejercicios_grupo = ejercicios[ejercicios["grupo_muscular"] == grupo]
            cantidad = 4 if len(grupos_dia) == 2 else 6
            cantidad_por_grupo = 4 if len(grupos_dia) == 2 else 6

            if len(ejercicios_grupo) < cantidad_por_grupo:
                cantidad_por_grupo = len(ejercicios_grupo)

            seleccionados = ejercicios_grupo.sample(cantidad_por_grupo)
            for _, ejercicio in seleccionados.iterrows():
                ejercicios_dia.append({
                    "grupo_muscular": grupo,
                    "ejercicio": ejercicio["nombre_ejercicio"],
                    "series": random.choice([3, 4]),
                    "repeticiones": random.choice([8, 10, 12, 15]),
                    "descanso": random.choice(["60s", "90s"]),
                    "imagen": ejercicio["imagen"]
                })
        semana[dia] = ejercicios_dia

    return {"semana": semana}

# Guardar JSON local
def guardar_json(rutina, nombre_archivo):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(rutina, f, indent=4, ensure_ascii=False)

# Guardar o actualizar en Supabase
def guardar_en_supabase(rutina_json, id_socio):
    try:
        resultado = supabase.table("rutina").select("id_rutina").eq("id_socio", id_socio).execute()
        if resultado.data:
            id_rutina_existente = resultado.data[0]["id_rutina"]
            supabase.table("rutina").update({"rutina_desc": rutina_json}).eq("id_rutina", id_rutina_existente).execute()
            print(f"🔄 Rutina actualizada para socio {id_socio}.")
        else:
            supabase.table("rutina").insert({"id_socio": id_socio, "rutina_desc": rutina_json}).execute()
            print(f"✅ Nueva rutina creada para socio {id_socio}.")
    except Exception as e:
        print(f"❌ Error Supabase: {e}")

# Main
if __name__ == "__main__":
    datos = cargar_datos_supabase()
    ejercicios = datos["ejercicio"]
    socios = datos["socio"]

    # Reemplazar id_gm por el nombre del grupo muscular
    grupo_muscular = datos["grupo_muscular"]
    ejercicios = ejercicios.merge(
        grupo_muscular[["id_gm", "nombre_gp"]],
        on="id_gm",
        how="left"
    )
    ejercicios.rename(columns={"nombre_gp": "grupo_muscular"}, inplace=True)

    print("Columnas disponibles en la tabla socio:", socios.columns.tolist())

    for _, socio in socios.iterrows():
        id_socio = socio["id_socio"]
        nivel = socio["nivel"]
        objetivo = socio["objetivo"]
        dias_por_semana = int(socio["dias_por_semana"]) if pd.notna(socio["dias_por_semana"]) else 3

        print(f"\n🔧 Generando rutina para {socio['nombre_completo']} (ID: {id_socio})")

        ejercicios_filtrados = ejercicios[
            (ejercicios["id_nivel"] == nivel) &
            (ejercicios["id_objetivo"] == objetivo)
        ]

        rutina = generar_rutina(ejercicios_filtrados, dias_por_semana, id_socio)
        if rutina:
            archivo = f"rutinas/rutina_socio_{id_socio}.json"
            guardar_json(rutina, archivo)
            guardar_en_supabase(rutina, id_socio)

    print("\n✅ Todas las rutinas fueron procesadas.")

