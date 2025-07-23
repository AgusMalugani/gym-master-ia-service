import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Ajustar sys.path para importar desde la carpeta ia
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
sys.path.insert(0, PROJECT_ROOT)

def run():
    """
    Ejecuta proyecciones de ingresos usando modelo predictivo y simulación Monte Carlo
    """
    try:
        base_path = os.path.join(PROJECT_ROOT, 'ia', 'data_science', 'Data_Lake_CSV')
        
        resultados = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "mensaje": "Proyección de ingresos con modelo predictivo y Monte Carlo",
            "datos_fuente": "Pagos Supabase + Segmentación + Simulación Monte Carlo"
        }
        
        # 1. Cargar datos reales de pagos desde Supabase
        pagos_supabase_path = os.path.join(base_path, 'pagos_supabase.csv')
        segmentacion_path = os.path.join(base_path, 'segmentacion_socios.csv')
        
        if os.path.exists(pagos_supabase_path):
            pagos_df = pd.read_csv(pagos_supabase_path)
            
            # Convertir fechas
            pagos_df['fecha_pago'] = pd.to_datetime(pagos_df['fecha_pago'])
            
            # Calcular monto pagado (considerando descuentos)
            if 'monto' in pagos_df.columns and 'descuento' in pagos_df.columns:
                pagos_df['monto_pagado'] = pagos_df['monto'] - pagos_df['descuento']
            elif 'monto_pagado' in pagos_df.columns:
                pagos_df['monto_pagado'] = pagos_df['monto_pagado']
            else:
                pagos_df['monto_pagado'] = pagos_df.get('monto', 50)  # Fallback
            
            # Análisis histórico de ingresos
            ingresos_mensuales = pagos_df.groupby(pagos_df['fecha_pago'].dt.to_period('M')).agg({
                'monto_pagado': 'sum',
                'socio_id': 'nunique'
            }).rename(columns={'socio_id': 'socios_activos'})
            
            if len(ingresos_mensuales) > 0:
                # Calcular precio promedio mensual
                ingresos_mensuales['precio_promedio'] = ingresos_mensuales['monto_pagado'] / ingresos_mensuales['socios_activos']
                
                resultados["historico_ingresos"] = {
                    "ultimo_mes": {
                        "ingresos_totales": float(ingresos_mensuales['monto_pagado'].iloc[-1]),
                        "socios_activos": int(ingresos_mensuales['socios_activos'].iloc[-1]),
                        "precio_promedio": float(ingresos_mensuales['precio_promedio'].iloc[-1])
                    },
                    "promedio_6_meses": {
                        "ingresos_totales": float(ingresos_mensuales['monto_pagado'].tail(6).mean()),
                        "socios_activos": float(ingresos_mensuales['socios_activos'].tail(6).mean()),
                        "precio_promedio": float(ingresos_mensuales['precio_promedio'].tail(6).mean())
                    }
                }
        else:
            # Fallback a datos simulados
            pagos_simulados_path = os.path.join(base_path, 'pagos_simulados.csv')
            if os.path.exists(pagos_simulados_path):
                pagos_df = pd.read_csv(pagos_simulados_path)
                pagos_df['fecha_pago'] = pd.to_datetime(pagos_df['fecha_pago'])
                pagos_df['monto_pagado'] = pagos_df['monto'] - pagos_df['descuento']
                resultados["datos_fuente"] = "Pagos simulados (fallback)"
            else:
                return {"error": "No se encontraron datos de pagos"}
        
        # 2. Cargar segmentación para análisis avanzado
        if os.path.exists(segmentacion_path):
            segmentacion_df = pd.read_csv(segmentacion_path)
            
            # Unir con datos de pagos
            pagos_con_segmento = pagos_df.merge(
                segmentacion_df[['socio_id', 'segmento_pago']], 
                on='socio_id', 
                how='left'
            )
            
            # Análisis por segmento
            ingresos_por_segmento = pagos_con_segmento.groupby('segmento_pago')['monto_pagado'].agg(['sum', 'mean', 'count'])
            
            resultados["analisis_segmentos"] = {}
            for segmento in ingresos_por_segmento.index:
                resultados["analisis_segmentos"][segmento] = {
                    "ingresos_totales": float(ingresos_por_segmento.loc[segmento, 'sum']),
                    "promedio_pago": float(ingresos_por_segmento.loc[segmento, 'mean']),
                    "cantidad_pagos": int(ingresos_por_segmento.loc[segmento, 'count'])
                }
        
        # 3. Modelo predictivo con Random Forest
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_absolute_error, r2_score
            
            # Preparar datos para modelo predictivo
            historico = crear_datos_historicos(pagos_df)
            
            if len(historico) > 10:  # Necesitamos suficientes datos
                X = historico[['socios', 'precio_promedio', 'porc_puntuales', 'porc_retraso_leve', 'porc_morosos']]
                y = historico['ingresos']
                
                # Dividir datos
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Entrenar modelo
                modelo = RandomForestRegressor(n_estimators=100, random_state=42)
                modelo.fit(X_train, y_train)
                
                # Predicciones
                y_pred = modelo.predict(X_test)
                
                # Métricas
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Predicción próximo mes
                ultimo_mes = X.iloc[-1:].copy()
                prediccion_proximo = modelo.predict(ultimo_mes)[0]
                
                resultados["modelo_predictivo"] = {
                    "precision_mae": float(mae),
                    "r2_score": float(r2),
                    "prediccion_proximo_mes": float(prediccion_proximo),
                    "confianza": "Alta" if r2 > 0.8 else "Media" if r2 > 0.6 else "Baja"
                }
            else:
                resultados["modelo_predictivo"] = {"error": "Datos insuficientes para entrenamiento"}
        except ImportError:
            resultados["modelo_predictivo"] = {"error": "scikit-learn no disponible"}
        except Exception as e:
            resultados["modelo_predictivo"] = {"error": f"Error en modelo predictivo: {str(e)}"}
        
        # 4. Simulación Monte Carlo
        monte_carlo = ejecutar_simulacion_monte_carlo(pagos_df)
        resultados["simulacion_monte_carlo"] = monte_carlo
        
        # 5. Proyecciones por escenarios
        resultados["proyecciones_escenarios"] = calcular_escenarios(pagos_df)
        
        # 6. Recomendaciones financieras
        resultados["recomendaciones"] = [
            "Implementar descuentos diferenciados por segmento",
            "Focalizar retención en socios de alto valor",
            "Optimizar precios según elasticidad por segmento",
            "Establecer alertas de flujo de caja para escenarios pesimistas"
        ]
        
        return resultados
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error en proyección de ingresos: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def crear_datos_historicos(pagos_df):
    """Crea dataset histórico para modelo predictivo"""
    try:
        # Agrupar por mes
        historico = pagos_df.groupby(pagos_df['fecha_pago'].dt.to_period('M')).agg({
            'socio_id': 'nunique',
            'monto_pagado': 'sum',
            'dias_retraso': 'mean' if 'dias_retraso' in pagos_df.columns else lambda x: 0,
            'perfil_pago': lambda x: (x == 'puntual').mean() if 'perfil_pago' in pagos_df.columns else lambda x: 0.8
        }).round(2)
        
        historico.columns = ['socios', 'ingresos', 'retraso_promedio', 'porc_puntuales']
        
        if len(historico) > 0:
            historico['precio_promedio'] = historico['ingresos'] / historico['socios']
            
            # Simular distribución de comportamiento de pago
            historico['porc_retraso_leve'] = np.random.uniform(0.2, 0.3, size=len(historico))
            historico['porc_morosos'] = 1 - historico['porc_puntuales'] - historico['porc_retraso_leve']
            historico['porc_morosos'] = np.clip(historico['porc_morosos'], 0, 1)
        
        return historico.reset_index()
        
    except Exception as e:
        print(f"Error creando datos históricos: {e}")
        return pd.DataFrame()

def ejecutar_simulacion_monte_carlo(pagos_df):
    """Ejecuta simulación Monte Carlo para proyecciones"""
    try:
        # Parámetros base
        socios_actuales = pagos_df['socio_id'].nunique()
        precio_promedio = pagos_df['monto_pagado'].mean()
        
        # Parámetros de simulación
        n_simulaciones = 1000
        meses_proyeccion = 12
        
        # Parámetros de crecimiento/volatilidad
        crecimiento_medio = 0.02  # 2% mensual
        crecimiento_std = 0.01
        variacion_precio_media = 0.01
        variacion_precio_std = 0.005
        
        simulaciones = []
        
        for sim in range(n_simulaciones):
            socios = socios_actuales
            precio = precio_promedio
            ingresos_simulacion = []
            
            for mes in range(meses_proyeccion):
                # Crecimiento de socios
                tasa_crecimiento = np.random.normal(crecimiento_medio, crecimiento_std)
                socios *= (1 + tasa_crecimiento)
                
                # Variación de precio
                ajuste_precio = np.random.normal(variacion_precio_media, variacion_precio_std)
                precio *= (1 + ajuste_precio)
                
                # Calcular ingresos
                ingresos = socios * precio
                ingresos_simulacion.append(ingresos)
            
            simulaciones.append(ingresos_simulacion)
        
        simulaciones = np.array(simulaciones)
        
        # Calcular percentiles
        percentiles = [5, 50, 95]
        proyecciones = np.percentile(simulaciones, percentiles, axis=0)
        
        return {
            "meses_proyectados": meses_proyeccion,
            "simulaciones_realizadas": n_simulaciones,
            "proyecciones": {
                "pesimista_p5": [float(x) for x in proyecciones[0]],
                "esperado_p50": [float(x) for x in proyecciones[1]], 
                "optimista_p95": [float(x) for x in proyecciones[2]]
            },
            "parametros": {
                "socios_base": int(socios_actuales),
                "precio_base": float(precio_promedio),
                "crecimiento_mensual_esperado": f"{crecimiento_medio*100:.1f}%"
            }
        }
        
    except Exception as e:
        return {"error": f"Error en simulación Monte Carlo: {str(e)}"}

def calcular_escenarios(pagos_df):
    """Calcula proyecciones por escenarios optimista/conservador/pesimista"""
    try:
        ingreso_actual = pagos_df['monto_pagado'].sum()
        socios_actuales = pagos_df['socio_id'].nunique()
        
        escenarios = {
            "optimista": {
                "crecimiento_socios": 0.15,  # 15% anual
                "aumento_precio": 0.10,      # 10% anual
                "retencion": 0.95            # 95% retención
            },
            "conservador": {
                "crecimiento_socios": 0.05,  # 5% anual
                "aumento_precio": 0.03,      # 3% anual
                "retencion": 0.85            # 85% retención
            },
            "pesimista": {
                "crecimiento_socios": -0.05, # -5% anual
                "aumento_precio": 0.00,      # Sin aumento
                "retencion": 0.75            # 75% retención
            }
        }
        
        proyecciones = {}
        
        for escenario, params in escenarios.items():
            # Proyección a 12 meses
            socios_proyectados = socios_actuales * (1 + params["crecimiento_socios"]) * params["retencion"]
            precio_proyectado = (pagos_df['monto_pagado'].mean()) * (1 + params["aumento_precio"])
            ingresos_proyectados = socios_proyectados * precio_proyectado * 12
            
            proyecciones[escenario] = {
                "socios_proyectados": int(socios_proyectados),
                "precio_promedio": float(precio_proyectado),
                "ingresos_anuales": float(ingresos_proyectados),
                "crecimiento_vs_actual": float((ingresos_proyectados / (ingreso_actual * 12) - 1) * 100) if ingreso_actual > 0 else 0
            }
        
        return proyecciones
        
    except Exception as e:
        return {"error": f"Error calculando escenarios: {str(e)}"}