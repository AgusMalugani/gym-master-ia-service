# ✅ ANALISIS DE CONCURRENCIA POR SEXO
#
# Este script realiza un análisis de asistencia al gimnasio diferenciando por sexo.
# Datos fuente: tablas `asistencia` y `socio` en Supabase.
#
# 🔹 Funcionalidades:
# - Conexión automática a Supabase
# - Carga de datos de asistencia y datos demográficos de socios (sexo, fecnac)
# - Agrupación de asistencias por:
#   • Semana (año + número de semana ISO)
#   • Mes (año + mes)
#   • Año
# - Conteo de concurrencias por sexo en cada período
# - Visualización con gráficos de barras (matplotlib)
# - Exportación de resultados a archivo Excel `concurrencia.xlsx`
#
# 💡 Uso:
# Ejecutar directamente este script para obtener resúmenes tabulares, gráficos y el Excel


import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client, Client

# Conexión a Supabase
SUPABASE_URL = "https://brrxvwgjkuofcgdnmnfb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cargar datos de asistencia y socios
def cargar_datos():
    asistencia = supabase.table("asistencia").select("*").execute()
    socio = supabase.table("socio").select("id_socio", "sexo", "fecnac").execute()
    df_asistencia = pd.DataFrame(asistencia.data)
    df_socio = pd.DataFrame(socio.data)
    return df_asistencia, df_socio

# Procesar concurrencia por sexo y periodo
def analizar_concurrencia(asistencia, socios):
    df = asistencia.merge(socios, left_on="socio_id", right_on="id_socio", how="left")
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["año"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["semana"] = df["fecha"].dt.isocalendar().week

    resumen = {
        "semanal": df.groupby(["año", "semana", "sexo"]).size().reset_index(name="asistencias"),
        "mensual": df.groupby(["año", "mes", "sexo"]).size().reset_index(name="asistencias"),
        "anual": df.groupby(["año", "sexo"]).size().reset_index(name="asistencias")
    }
    return resumen

# Visualizar gráfico de barras por periodo
def graficar_concurrencia(df, titulo):
    pivot = df.groupby([df.columns[0], "sexo"])["asistencias"].sum().unstack(fill_value=0)
    pivot.plot(kind="bar", stacked=True, figsize=(10, 6))
    plt.title(titulo)
    plt.ylabel("Asistencias")
    plt.xlabel(df.columns[0])
    plt.xticks(rotation=45)
    plt.legend(title="Sexo")
    plt.tight_layout()
    plt.show()

# Exportar los resultados a Excel
def exportar_resumen_excel(resumen_dict, archivo="concurrencia.xlsx"):
    with pd.ExcelWriter(archivo) as writer:
        for clave, df in resumen_dict.items():
            df.to_excel(writer, sheet_name=clave, index=False)
    print(f"✅ Archivo exportado como {archivo}")

# Ejecución principal
if __name__ == "__main__":
    asistencia, socios = cargar_datos()
    resumen = analizar_concurrencia(asistencia, socios)

    print("\n📊 Concurrencia semanal:")
    print(resumen["semanal"].head())

    print("\n📊 Concurrencia mensual:")
    print(resumen["mensual"].head())

    print("\n📊 Concurrencia anual:")
    print(resumen["anual"].head())

    graficar_concurrencia(resumen["semanal"], "Concurrencia semanal por sexo")
    graficar_concurrencia(resumen["mensual"], "Concurrencia mensual por sexo")
    graficar_concurrencia(resumen["anual"], "Concurrencia anual por sexo")

    exportar_resumen_excel(resumen)