import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Ajustar sys.path para importar desde la carpeta ia
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
sys.path.insert(0, PROJECT_ROOT)

def cargar_datos_logs_uso():
    """Carga los datos de logs de uso de equipos desde parquet"""
    try:
        parquet_path = os.path.join(PROJECT_ROOT, 'ia', 'data_science', 'Data_Lake', 'Processed', 'logs_uso', 'gym_master_logs_uso.parquet')
        if os.path.exists(parquet_path):
            return pd.read_parquet(parquet_path)
        else:
            return generar_datos_equipos_ejemplo()
    except Exception as e:
        print(f"Error cargando logs de uso: {e}")
        return generar_datos_equipos_ejemplo()

def generar_datos_equipos_ejemplo():
    """Genera datos de ejemplo de uso de equipos"""
    np.random.seed(42)
    
    equipos = [
        {"equipo": "Cinta de correr", "categoria": "Cardio"},
        {"equipo": "Banco de pesas", "categoria": "Fuerza"},
        {"equipo": "Máquina Smith", "categoria": "Fuerza"},
        {"equipo": "Bicicleta estática", "categoria": "Cardio"},
        {"equipo": "Máquina de remo", "categoria": "Cardio"},
        {"equipo": "Prensa de piernas", "categoria": "Fuerza"},
        {"equipo": "Máquina de dorsales", "categoria": "Fuerza"},
        {"equipo": "Elíptica", "categoria": "Cardio"},
        {"equipo": "Mancuernas", "categoria": "Fuerza"},
        {"equipo": "Máquina de abdominales", "categoria": "Funcional"},
        {"equipo": "TRX", "categoria": "Funcional"},
        {"equipo": "Kettlebells", "categoria": "Funcional"},
        {"equipo": "Colchonetas", "categoria": "Flexibilidad"},
        {"equipo": "Barras de stretching", "categoria": "Flexibilidad"}
    ]
    
    data = []
    fecha_inicio = datetime.now() - timedelta(days=90)
    
    for i in range(90):  # 90 días de datos
        fecha = fecha_inicio + timedelta(days=i)
        for equipo_info in equipos:
            # Simular uso variable por categoría
            if equipo_info["categoria"] == "Cardio":
                usos_diarios = np.random.poisson(25)  # Más popular
            elif equipo_info["categoria"] == "Fuerza":
                usos_diarios = np.random.poisson(20)
            elif equipo_info["categoria"] == "Funcional":
                usos_diarios = np.random.poisson(15)
            else:  # Flexibilidad
                usos_diarios = np.random.poisson(8)
            
            data.append({
                'fecha': fecha,
                'equipo': equipo_info["equipo"],
                'categoria': equipo_info["categoria"],
                'usos': usos_diarios,
                'tiempo_uso_promedio': np.random.uniform(15, 45)  # minutos
            })
    
    return pd.DataFrame(data)

def analizar_uso_equipos(logs_df):
    """Analiza el uso de equipos y genera ranking"""
    
    # Calcular métricas por equipo
    uso_por_equipo = logs_df.groupby(['equipo', 'categoria']).agg({
        'usos': 'sum',
        'tiempo_uso_promedio': 'mean'
    }).reset_index()
    
    # Calcular uso promedio diario
    dias_totales = (logs_df['fecha'].max() - logs_df['fecha'].min()).days + 1
    uso_por_equipo['uso_promedio_diario'] = uso_por_equipo['usos'] / dias_totales
    
    # Calcular puntuación de popularidad (normalizada 0-100)
    max_uso = uso_por_equipo['uso_promedio_diario'].max()
    uso_por_equipo['uso_promedio'] = (uso_por_equipo['uso_promedio_diario'] / max_uso * 100).round(1)
    
    # Ordenar por popularidad
    uso_por_equipo = uso_por_equipo.sort_values('uso_promedio', ascending=False)
    
    return uso_por_equipo

def generar_recomendaciones(uso_equipos_df, uso_por_categoria):
    """Genera recomendaciones basadas en el análisis"""
    recomendaciones = []
    
    # Top 3 equipos más populares
    top_3 = uso_equipos_df.head(3)
    for _, equipo in top_3.iterrows():
        if equipo['uso_promedio'] > 80:
            recomendaciones.append(f"Considerar añadir más unidades de {equipo['equipo']}")
    
    # Equipos con poco uso
    poco_uso = uso_equipos_df[uso_equipos_df['uso_promedio'] < 30]
    if len(poco_uso) > 0:
        equipo_menos_usado = poco_uso.iloc[-1]
        recomendaciones.append(f"Evaluar reemplazo o reubicación de {equipo_menos_usado['equipo']}")
    
    # Recomendaciones por categoría
    categoria_popular = uso_por_categoria.idxmax()
    categoria_menos_popular = uso_por_categoria.idxmin()
    
    recomendaciones.append(f"Ampliar zona de {categoria_popular} por alta demanda")
    
    if uso_por_categoria[categoria_menos_popular] < 40:
        recomendaciones.append(f"Promocionar actividades de {categoria_menos_popular}")
    
    return recomendaciones

def run():
    """
    Ejecuta el análisis de clustering para determinar el ranking y uso de equipos
    """
    try:
        # Cargar datos de logs de uso
        logs_df = cargar_datos_logs_uso()
        
        # Asegurar que la fecha esté en formato datetime
        logs_df['fecha'] = pd.to_datetime(logs_df['fecha'])
        
        # Analizar uso de equipos
        uso_equipos = analizar_uso_equipos(logs_df)
        
        # Crear ranking de popularidad
        ranking_popularidad = []
        for _, row in uso_equipos.iterrows():
            ranking_popularidad.append({
                "equipo": row['equipo'],
                "uso_promedio": row['uso_promedio'],
                "categoria": row['categoria']
            })
        
        # Analizar por categorías
        uso_por_categoria = logs_df.groupby('categoria')['usos'].mean()
        categorias_populares = {}
        max_categoria = uso_por_categoria.max()
        
        for categoria, uso_medio in uso_por_categoria.items():
            categorias_populares[categoria] = round((uso_medio / max_categoria * 100), 1)
        
        # Generar recomendaciones
        recomendaciones = generar_recomendaciones(uso_equipos, uso_por_categoria)
        
        # Métricas adicionales
        total_usos = logs_df['usos'].sum()
        equipo_mas_popular = uso_equipos.iloc[0]['equipo']
        dias_analizados = (logs_df['fecha'].max() - logs_df['fecha'].min()).days + 1
        
        return {
            "ranking_popularidad": ranking_popularidad,
            "categorias_populares": categorias_populares,
            "recomendaciones": recomendaciones,
            "metricas_adicionales": {
                "total_usos_periodo": int(total_usos),
                "equipo_mas_popular": equipo_mas_popular,
                "dias_analizados": dias_analizados,
                "uso_promedio_diario_total": round(total_usos / dias_analizados, 1)
            }
        }
    except Exception as e:
        print(f"Error en clustering de equipos: {e}")
        return {"error": str(e)}