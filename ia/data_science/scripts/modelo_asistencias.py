# ✅ MODELO DE ASISTENCIA DETALLADO
#
# Este script analiza las asistencias al gimnasio en distintos periodos:
# - Diario
# - Semanal (ISO week)
# - Mensual
# - Trimestral
# - Semestral
# - Anual
#
# Se conecta a Supabase, cruza asistencia con datos de socios (sexo, fecha de nacimiento),
# y exporta un archivo Excel con todos los resúmenes.

import pandas as pd
from supabase import create_client, Client

# 🔐 Conexión a Supabase
SUPABASE_URL = "https://brrxvwgjkuofcgdnmnfb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📥 Cargar datos desde Supabase
def cargar_datos():
    asistencia = supabase.table("asistencia").select("*").execute()
    socio = supabase.table("socio").select("id_socio", "sexo", "fecnac").execute()
    df_asistencia = pd.DataFrame(asistencia.data)
    df_socio = pd.DataFrame(socio.data)
    return df_asistencia, df_socio

# 📊 Agrupar por diferentes periodos
def agrupar_asistencias(df):
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["año"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["semana"] = df["fecha"].dt.isocalendar().week
    df["trimestre"] = df["fecha"].dt.quarter
    df["semestre"] = df["mes"].apply(lambda x: 1 if x <= 6 else 2)
    
    resumen = {
        "diario": df.groupby(["fecha", "sexo"]).size().reset_index(name="asistencias"),
        "semanal": df.groupby(["año", "semana", "sexo"]).size().reset_index(name="asistencias"),
        "mensual": df.groupby(["año", "mes", "sexo"]).size().reset_index(name="asistencias"),
        "trimestral": df.groupby(["año", "trimestre", "sexo"]).size().reset_index(name="asistencias"),
        "semestral": df.groupby(["año", "semestre", "sexo"]).size().reset_index(name="asistencias"),
        "anual": df.groupby(["año", "sexo"]).size().reset_index(name="asistencias")
    }
    return resumen

# 💾 Exportar a Excel
def exportar_excel(resumen, archivo="modelo_asistencias.xlsx"):
    with pd.ExcelWriter(archivo) as writer:
        for periodo, df in resumen.items():
            df.to_excel(writer, sheet_name=periodo, index=False)
    print(f"✅ Exportado a {archivo}")

# ▶️ Ejecución principal
if __name__ == "__main__":
    asistencia, socios = cargar_datos()
    df = asistencia.merge(socios, left_on="socio_id", right_on="id_socio", how="left")
    resumen = agrupar_asistencias(df)

    for periodo, tabla in resumen.items():
        print(f"\n📌 {periodo.upper()}\n", tabla.head())

    exportar_excel(resumen)
