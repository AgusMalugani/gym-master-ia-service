import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Ajustar sys.path para importar desde la carpeta ia
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
sys.path.insert(0, PROJECT_ROOT)

def cargar_datos_asistencia():
    """Carga datos de asistencia, con fallback a datos simulados"""
    try:
        # Intentar cargar desde el sistema ETL real
        from ia.data_science.ETL.etl_login import run_etl
        from ia.data_science.Informes.informes_abandono import detectar_inactividad
        
        data = run_etl("gym_master")
        return data['asistencia'], True  # True indica datos reales
    except Exception as e:
        print(f"Usando datos simulados debido a: {e}")
        # Fallback a datos simulados
        return generar_datos_asistencia_simulados(), False

def generar_datos_asistencia_simulados():
    """Genera datos simulados de asistencia para desarrollo"""
    import numpy as np
    np.random.seed(42)
    
    # Generar 90 días de datos
    fechas = pd.date_range(start=datetime.now() - timedelta(days=90), periods=90)
    data = []
    
    # Simular 200 socios
    for socio_id in range(1, 201):
        # Algunos socios asisten más que otros
        probabilidad_asistencia = np.random.choice([0.8, 0.5, 0.2], p=[0.4, 0.4, 0.2])
        
        for fecha in fechas:
            if np.random.random() < probabilidad_asistencia:
                data.append({
                    'fecha': fecha,
                    'socio_id': socio_id,
                    'gimnasio': 'gym_master'
                })
    
    df = pd.DataFrame(data)
    df['gimnasio'] = 'gym_master'
    return df

def detectar_inactividad_simple(asistencia_df, semanas_umbral=4):
    """Versión simplificada de detección de inactividad para datos simulados"""
    asistencia_df['fecha'] = pd.to_datetime(asistencia_df['fecha'])
    fecha_limite = datetime.now() - timedelta(weeks=semanas_umbral)
    
    # Últimas asistencias por socio
    ultima_asistencia = asistencia_df.groupby('socio_id')['fecha'].max().reset_index()
    
    # Determinar estado
    ultima_asistencia['estado'] = ultima_asistencia['fecha'].apply(
        lambda x: 'Activo' if x >= fecha_limite else 'Inactivo'
    )
    
    # Calcular semanas sin asistir
    ultima_asistencia['semanas_sin_asistir'] = (
        (datetime.now() - ultima_asistencia['fecha']).dt.days / 7
    ).round(1)
    
    return ultima_asistencia

def run():
    """
    Ejecuta la predicción de asistencia general para todos los gimnasios
    """
    try:
        # Cargar datos de asistencia
        asistencia_df, datos_reales = cargar_datos_asistencia()
        
        if len(asistencia_df) == 0:
            return {"error": "No se pudieron cargar datos de asistencia"}
        
        # Detectar inactividad con diferentes umbrales
        if datos_reales:
            try:
                from ia.data_science.Informes.informes_abandono import detectar_inactividad
                abandono_4_sem = detectar_inactividad(asistencia_df, semanas_umbral=4)
                abandono_2_sem = detectar_inactividad(asistencia_df, semanas_umbral=2)
                abandono_6_sem = detectar_inactividad(asistencia_df, semanas_umbral=6)
            except:
                # Fallback a función simple
                abandono_4_sem = detectar_inactividad_simple(asistencia_df, 4)
                abandono_2_sem = detectar_inactividad_simple(asistencia_df, 2)
                abandono_6_sem = detectar_inactividad_simple(asistencia_df, 6)
        else:
            abandono_4_sem = detectar_inactividad_simple(asistencia_df, 4)
            abandono_2_sem = detectar_inactividad_simple(asistencia_df, 2)
            abandono_6_sem = detectar_inactividad_simple(asistencia_df, 6)
        
        # Calcular métricas de riesgo
        total_socios = len(abandono_4_sem)
        riesgo_alto = len(abandono_4_sem[abandono_4_sem['estado'] == 'Inactivo'])
        riesgo_medio = max(0, len(abandono_2_sem[abandono_2_sem['estado'] == 'Inactivo']) - riesgo_alto)
        riesgo_bajo = max(0, total_socios - riesgo_alto - riesgo_medio)
        inactivos_cronicos = len(abandono_6_sem[abandono_6_sem['estado'] == 'Inactivo'])
        
        # Calcular tendencia basada en asistencias de la última semana vs semana anterior
        asistencia_df['fecha'] = pd.to_datetime(asistencia_df['fecha'])
        fecha_actual = datetime.now()
        ultima_semana = asistencia_df[asistencia_df['fecha'] >= fecha_actual - timedelta(days=7)]
        semana_anterior = asistencia_df[
            (asistencia_df['fecha'] >= fecha_actual - timedelta(days=14)) &
            (asistencia_df['fecha'] < fecha_actual - timedelta(days=7))
        ]
        
        asistencias_ultima = len(ultima_semana)
        asistencias_anterior = len(semana_anterior)
        
        if asistencias_anterior > 0:
            cambio_porcentual = ((asistencias_ultima - asistencias_anterior) / asistencias_anterior) * 100
            if cambio_porcentual > 5:
                tendencia = "crecimiento"
            elif cambio_porcentual < -5:
                tendencia = "decrecimiento"
            else:
                tendencia = "estable"
        else:
            tendencia = "estable"
            cambio_porcentual = 0
        
        # Generar recomendación basada en los datos
        if riesgo_alto > total_socios * 0.15:  # Si más del 15% está en riesgo alto
            recomendacion = "Urgente: Lanzar campaña masiva de reactivación"
        elif riesgo_alto > total_socios * 0.10:  # Si más del 10% está en riesgo alto
            recomendacion = "Enviar notificaciones personalizadas a usuarios de riesgo alto"
        else:
            recomendacion = "Mantener programa de retención actual"
        
        return {
            "predicciones": {
                "riesgo_bajo": riesgo_bajo,
                "riesgo_medio": riesgo_medio,
                "riesgo_alto": riesgo_alto,
                "inactivos": inactivos_cronicos,
                "totales": total_socios
            },
            "tendencia": tendencia,
            "recomendacion": recomendacion,
            "metricas_adicionales": {
                "asistencias_ultima_semana": asistencias_ultima,
                "asistencias_semana_anterior": asistencias_anterior,
                "cambio_porcentual": round(cambio_porcentual, 2),
                "datos_reales": datos_reales
            }
        }
    except Exception as e:
        print(f"Error en predicción de asistencia: {e}")
        return {"error": str(e)}

def run_by_gym(gym_id: int):
    """
    Ejecuta la predicción de asistencia para un gimnasio específico
    """
    try:
        # Mapear gym_id a nombre de gimnasio
        gym_mapping = {
            1: "gym_master",
            2: "gym_norte", 
            3: "gym_sur"
        }
        
        if gym_id not in gym_mapping:
            return {"error": "Gimnasio no encontrado"}
        
        gimnasio = gym_mapping[gym_id]
        
        # Cargar datos (por ahora usar los mismos datos para todos los gyms)
        asistencia_df, datos_reales = cargar_datos_asistencia()
        
        if len(asistencia_df) == 0:
            return {"error": "No se pudieron cargar datos de asistencia"}
        
        # Filtrar por gimnasio si hay datos reales
        if datos_reales:
            asistencia_df = asistencia_df[asistencia_df['gimnasio'] == gimnasio]
            if len(asistencia_df) == 0:
                # Si no hay datos para ese gym, usar datos simulados
                asistencia_df = generar_datos_asistencia_simulados()
                datos_reales = False
        
        # Detectar inactividad
        if datos_reales:
            try:
                from ia.data_science.Informes.informes_abandono import detectar_inactividad
                abandono_df = detectar_inactividad(asistencia_df, semanas_umbral=4)
            except:
                abandono_df = detectar_inactividad_simple(asistencia_df, 4)
        else:
            abandono_df = detectar_inactividad_simple(asistencia_df, 4)
        
        # Calcular métricas específicas del gimnasio
        total_socios = len(abandono_df)
        riesgo_alto = len(abandono_df[abandono_df['estado'] == 'Inactivo'])
        riesgo_medio = max(0, int(total_socios * 0.2))  # Estimación del 20%
        riesgo_bajo = max(0, total_socios - riesgo_alto - riesgo_medio)
        
        # Calcular tendencia específica del gimnasio
        asistencia_df['fecha'] = pd.to_datetime(asistencia_df['fecha'])
        asistencias_recientes = asistencia_df[asistencia_df['fecha'] >= datetime.now() - timedelta(days=30)]
        promedio_diario = len(asistencias_recientes) / 30 if len(asistencias_recientes) > 0 else 0
        
        if promedio_diario > 50:
            tendencia = "crecimiento"
            recomendacion = "Considerar expansión de horarios"
        elif promedio_diario < 20:
            tendencia = "decrecimiento"
            recomendacion = "Implementar programa de incentivos urgente"
        else:
            tendencia = "estable"
            recomendacion = "Mantener estrategia actual de retención"
            
        return {
            "gym_id": gym_id,
            "gimnasio": gimnasio,
            "predicciones": {
                "riesgo_bajo": riesgo_bajo,
                "riesgo_medio": riesgo_medio,
                "riesgo_alto": riesgo_alto
            },
            "tendencia": tendencia,
            "recomendacion": recomendacion,
            "metricas_adicionales": {
                "total_socios": total_socios,
                "promedio_asistencia_diaria": round(promedio_diario, 2),
                "datos_reales": datos_reales
            }
        }
    except Exception as e:
        print(f"Error en predicción para gym {gym_id}: {e}")
        return {"error": str(e)}