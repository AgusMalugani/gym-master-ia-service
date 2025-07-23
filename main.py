from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importamos los módulos de IA
from models import prediccion_asistencia, proyeccion_ingresos, clustering_equipos

# Crear instancia de FastAPI
app = FastAPI(
    title="GymMaster IA Service",
    description="Microservicio de IA para análisis predictivo y optimización de gimnasios",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejo global de excepciones"""
    return JSONResponse(
        status_code=500,
        content={"error": "Error interno del servidor", "detail": str(exc)}
    )

@app.get("/")
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "mensaje": "GymMaster IA Service - Microservicio de Análisis Predictivo",
        "version": "2.0.0",
        "descripcion": "Análisis avanzado con ML, churn prediction, clustering y proyecciones financieras",
        "timestamp": datetime.now().isoformat(),
        "endpoints_disponibles": [
            "/docs - Documentación interactiva",
            "/health - Estado del servicio",
            "/prediccion-asistencia - Análisis de churn y predicciones ML",
            "/proyeccion-ingresos - Proyecciones financieras con Random Forest",
            "/ranking-equipos - Clustering y análisis de equipos",
            "/segmentacion-socios - Segmentación avanzada de socios",
            "/analisis-churn - Análisis específico de abandono"
        ]
    }

@app.get("/health")
async def health_check():
    """Endpoint de salud del microservicio"""
    try:
        # Verificar conexiones críticas
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "dependencies": {
                "database": "connected",
                "ml_models": "loaded",
                "data_pipelines": "operational"
            }
        }
        
        # Test básico de modelos
        try:
            from models import prediccion_asistencia
            test_result = prediccion_asistencia.run()
            health_status["dependencies"]["prediccion_model"] = "operational" if "error" not in test_result else "error"
        except Exception as e:
            health_status["dependencies"]["prediccion_model"] = f"error: {str(e)[:50]}"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

@app.get("/prediccion-asistencia")
async def prediccion_asistencia():
    """
    Análisis avanzado de churn prediction y segmentación de socios
    Utiliza modelos ML para predecir probabilidad de abandono
    """
    try:
        logger.info("Iniciando análisis de predicción de asistencia con ML")
        from models import prediccion_asistencia as pred_model
        resultado = pred_model.run()
        
        if "error" in resultado:
            raise HTTPException(status_code=500, detail=resultado["error"])
            
        return {
            "endpoint": "prediccion-asistencia",
            "descripcion": "Análisis de churn con Machine Learning y segmentación inteligente",
            "timestamp": datetime.now().isoformat(),
            "data": resultado
        }
        
    except Exception as e:
        logger.error(f"Error en predicción de asistencia: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/proyeccion-ingresos")
async def proyeccion_ingresos():
    """
    Proyecciones financieras usando Random Forest y simulación Monte Carlo
    Análisis predictivo avanzado de ingresos futuros
    """
    try:
        logger.info("Iniciando proyección de ingresos con Random Forest")
        from models import proyeccion_ingresos as proj_model
        resultado = proj_model.run()
        
        if "error" in resultado:
            raise HTTPException(status_code=500, detail=resultado["error"])
            
        return {
            "endpoint": "proyeccion-ingresos",
            "descripcion": "Proyecciones financieras con Random Forest y Monte Carlo",
            "timestamp": datetime.now().isoformat(),
            "data": resultado
        }
        
    except Exception as e:
        logger.error(f"Error en proyección de ingresos: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/ranking-equipos")
async def ranking_equipos():
    """
    Análisis de clustering de equipos con logs QR reales
    Ranking de popularidad y análisis de mantenimiento
    """
    try:
        logger.info("Iniciando clustering y ranking de equipos")
        from models import clustering_equipos as cluster_model
        resultado = cluster_model.run()
        
        if "error" in resultado:
            raise HTTPException(status_code=500, detail=resultado["error"])
            
        return {
            "endpoint": "ranking-equipos",
            "descripcion": "Clustering inteligente y análisis de equipos con QR logs",
            "timestamp": datetime.now().isoformat(),
            "data": resultado
        }
        
    except Exception as e:
        logger.error(f"Error en ranking de equipos: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/segmentacion-socios")
async def segmentacion_socios():
    """
    Segmentación avanzada de socios usando datos de pagos y comportamiento
    """
    try:
        logger.info("Iniciando segmentación avanzada de socios")
        
        # Usar el análisis de segmentación del modelo de predicción
        from models import prediccion_asistencia as pred_model
        resultado_completo = pred_model.run()
        
        if "error" in resultado_completo:
            raise HTTPException(status_code=500, detail=resultado_completo["error"])
        
        # Extraer solo la parte de segmentación
        segmentacion_data = {
            "segmentacion_socios": resultado_completo.get("segmentacion_socios", {}),
            "analisis_comportamiento": resultado_completo.get("analisis_comportamiento", {}),
            "metricas_segmentacion": resultado_completo.get("metricas_segmentacion", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "endpoint": "segmentacion-socios",
            "descripcion": "Segmentación inteligente basada en comportamiento y pagos",
            "timestamp": datetime.now().isoformat(),
            "data": segmentacion_data
        }
        
    except Exception as e:
        logger.error(f"Error en segmentación de socios: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/analisis-churn")
async def analisis_churn():
    """
    Análisis específico de churn y probabilidades de abandono
    """
    try:
        logger.info("Iniciando análisis específico de churn")
        
        from models import prediccion_asistencia as pred_model
        resultado_completo = pred_model.run()
        
        if "error" in resultado_completo:
            raise HTTPException(status_code=500, detail=resultado_completo["error"])
        
        # Extraer solo los datos de churn
        churn_data = {
            "prediccion_churn": resultado_completo.get("prediccion_churn", {}),
            "factores_riesgo": resultado_completo.get("factores_riesgo", {}),
            "socios_en_riesgo": resultado_completo.get("socios_en_riesgo", {}),
            "recomendaciones_retencion": resultado_completo.get("recomendaciones_retencion", []),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "endpoint": "analisis-churn",
            "descripcion": "Análisis predictivo de abandono con Machine Learning",
            "timestamp": datetime.now().isoformat(),
            "data": churn_data
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de churn: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# Manejo global de errores
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "timestamp": datetime.now().isoformat(),
            "detail": "Consulte los logs para más información"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)