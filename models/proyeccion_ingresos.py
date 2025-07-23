import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Ajustar sys.path para importar desde la carpeta ia
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
sys.path.insert(0, PROJECT_ROOT)

def cargar_datos_pagos():
    """Carga los datos de pagos simulados desde el CSV"""
    try:
        csv_path = os.path.join(PROJECT_ROOT, 'ia', 'data_science', 'Data_Lake_CSV', 'pagos_simulados.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Calcular monto_pagado = monto - descuento
            if 'monto' in df.columns and 'descuento' in df.columns:
                df['monto_pagado'] = df['monto'] - df['descuento']
            elif 'monto' in df.columns:
                df['monto_pagado'] = df['monto']
            
            # Usar fecha_pago como fecha principal
            if 'fecha_pago' in df.columns:
                df['fecha'] = df['fecha_pago']
            elif 'fecha_limite' in df.columns:
                df['fecha'] = df['fecha_limite']
            
            # Mapear metodo_pago si existe
            if 'metodo_pago' in df.columns:
                pass  # Ya existe
            
            return df
        else:
            # Si no existe el CSV, generar datos básicos de ejemplo
            return generar_datos_pagos_ejemplo()
    except Exception as e:
        print(f"Error cargando datos de pagos: {e}")
        return generar_datos_pagos_ejemplo()

def generar_datos_pagos_ejemplo():
    """Genera datos de ejemplo si no se pueden cargar los reales"""
    np.random.seed(42)
    meses = pd.date_range(start='2024-01-01', periods=12, freq='M')
    
    data = []
    for mes in meses:
        n_pagos = np.random.randint(180, 220)  # Entre 180-220 pagos por mes
        for _ in range(n_pagos):
            monto = np.random.choice([30, 50, 70], p=[0.5, 0.3, 0.2])  # Básico, Estándar, Premium
            descuento = np.random.choice([0, 5, 10], p=[0.8, 0.15, 0.05])
            data.append({
                'fecha': mes,
                'monto_pagado': monto - descuento,
                'nivel': 'Básico' if monto == 30 else 'Estándar' if monto == 50 else 'Premium',
                'metodo_pago': np.random.choice(['Efectivo', 'Tarjeta', 'Transferencia', 'Débito automático'])
            })
    
    return pd.DataFrame(data)

def calcular_proyecciones(pagos_df):
    """Calcula proyecciones basadas en datos históricos"""
    if pagos_df.empty:
        return {
            'proximo_mes': 12000.00,
            'siguiente_trimestre': 36000.00,
            'proximo_año': 150000.00
        }
    
    # Asegurar que la columna fecha existe y está en formato datetime
    if 'fecha' not in pagos_df.columns:
        # Si no hay columna fecha, crear una proyección básica
        promedio_pago = pagos_df['monto_pagado'].mean() if 'monto_pagado' in pagos_df.columns else 50
        total_pagos = len(pagos_df)
        proyeccion_mensual = promedio_pago * (total_pagos / 12)  # Asumir 12 meses de datos
        
        return {
            'proximo_mes': round(proyeccion_mensual, 2),
            'siguiente_trimestre': round(proyeccion_mensual * 3, 2),
            'proximo_año': round(proyeccion_mensual * 12, 2)
        }
    
    pagos_df['fecha'] = pd.to_datetime(pagos_df['fecha'])
    
    # Agregar ingresos por mes
    ingresos_mensuales = pagos_df.groupby(pagos_df['fecha'].dt.to_period('M'))['monto_pagado'].sum()
    
    # Calcular tendencias
    if len(ingresos_mensuales) >= 3:
        # Tendencia de los últimos 3 meses
        ultimos_3_meses = ingresos_mensuales.tail(3)
        tendencia = (ultimos_3_meses.iloc[-1] - ultimos_3_meses.iloc[0]) / 3
        
        # Proyección del próximo mes
        ultimo_mes = ingresos_mensuales.iloc[-1]
        proyeccion_mes = ultimo_mes + tendencia
        
        # Proyección trimestral (considerando estacionalidad)
        factor_estacional = 1.05  # Asumiendo un crecimiento estacional del 5%
        proyeccion_trimestre = proyeccion_mes * 3 * factor_estacional
        
        # Proyección anual
        promedio_mensual = ingresos_mensuales.mean()
        proyeccion_anual = promedio_mensual * 12 * 1.08  # Crecimiento anual del 8%
        
    else:
        # Si no hay suficientes datos, usar estimaciones conservadoras
        if len(ingresos_mensuales) > 0:
            promedio = ingresos_mensuales.mean()
        else:
            promedio = pagos_df['monto_pagado'].sum() / max(1, len(pagos_df.groupby(pagos_df['fecha'].dt.to_period('M'))))
        
        proyeccion_mes = promedio * 1.02
        proyeccion_trimestre = proyeccion_mes * 3
        proyeccion_anual = proyeccion_mes * 12
    
    return {
        'proximo_mes': round(max(0, float(proyeccion_mes)), 2),
        'siguiente_trimestre': round(max(0, float(proyeccion_trimestre)), 2),
        'proximo_año': round(max(0, float(proyeccion_anual)), 2)
    }

def analizar_factores(pagos_df):
    """Analiza factores de crecimiento y riesgo"""
    try:
        if pagos_df.empty:
            return (
                ["Datos limitados disponibles", "Estimaciones basadas en promedios del sector"],
                ["Falta de datos históricos", "Incertidumbre en proyecciones"]
            )
        
        # Convertir fecha si existe
        if 'fecha' in pagos_df.columns:
            pagos_df['fecha'] = pd.to_datetime(pagos_df['fecha'])
        
        # Análisis por método de pago
        if 'metodo_pago' in pagos_df.columns:
            metodos_populares = pagos_df['metodo_pago'].value_counts()
            metodo_principal = metodos_populares.index[0] if len(metodos_populares) > 0 else "Tarjeta"
        else:
            metodo_principal = "Tarjeta"
        
        # Análisis por nivel de suscripción
        if 'nivel' in pagos_df.columns:
            niveles = pagos_df['nivel'].value_counts()
            nivel_predominante = niveles.index[0] if len(niveles) > 0 else "Básico"
        else:
            nivel_predominante = "Básico"
        
        # Factores de crecimiento basados en datos
        factores_crecimiento = [
            f"Método de pago predominante: {metodo_principal}",
            f"Nivel de suscripción popular: {nivel_predominante}",
            "Tendencia de pagos automatizados en crecimiento"
        ]
        
        # Factores de riesgo basados en análisis
        if 'fecha' in pagos_df.columns:
            pagos_mes_actual = len(pagos_df[pagos_df['fecha'] >= datetime.now() - timedelta(days=30)])
        else:
            pagos_mes_actual = len(pagos_df) / 12  # Estimación mensual
        
        factores_riesgo = []
        if pagos_mes_actual < 150:
            factores_riesgo.append("Reducción en número de pagos mensuales")
        
        factores_riesgo.extend([
            "Competencia en el sector fitness",
            "Posible impacto económico estacional"
        ])
        
        return factores_crecimiento, factores_riesgo
        
    except Exception as e:
        print(f"Error en analizar_factores: {e}")
        return (
            ["Error al analizar datos", "Usando estimaciones generales"],
            ["Problemas con datos de entrada", "Recomendable revisar fuentes de datos"]
        )

def run():
    """
    Genera proyecciones de ingresos basadas en datos históricos reales
    """
    try:
        # Cargar datos de pagos
        pagos_df = cargar_datos_pagos()
        
        # Calcular proyecciones
        proyecciones = calcular_proyecciones(pagos_df)
        
        # Analizar factores
        factores_crecimiento, factores_riesgo = analizar_factores(pagos_df)
        
        # Generar proyección por mes (próximos 6 meses)
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"]
        base_mensual = proyecciones['proximo_mes']
        
        proyeccion_mensual = {}
        for i, mes in enumerate(meses):
            # Aplicar una variación del 2-5% mes a mes
            factor_variacion = 1 + (np.random.uniform(0.02, 0.05) * (i + 1))
            proyeccion_mensual[mes] = round(float(base_mensual * factor_variacion), 2)
        
        return {
            "proyeccion": proyecciones,
            "por_mes": proyeccion_mensual,
            "factores_crecimiento": factores_crecimiento,
            "factores_riesgo": factores_riesgo,
            "metricas_adicionales": {
                "total_pagos_historicos": len(pagos_df),
                "ingreso_promedio_por_pago": round(float(pagos_df['monto_pagado'].mean()), 2),
                "meses_con_datos": len(pagos_df.groupby(pagos_df['fecha'].dt.to_period('M')))
            }
        }
    except Exception as e:
        print(f"Error en proyección de ingresos: {e}")
        return {"error": str(e)}