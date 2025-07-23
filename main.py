from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importamos los módulos de IA
from models import prediccion_asistencia, proyeccion_ingresos, clustering_equipos

app = FastAPI(
    title="GYM MASTER - IA Service",
    description="Microservicio de Inteligencia Artificial para análisis y predicciones del gimnasio",
    version="1.0.0"
)

# Configuración de CORS para permitir peticiones desde ciertos orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gymmaster.com", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración básica de seguridad con API Key
API_KEY = os.environ.get("API_KEY", "default_dev_key_change_in_production")
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verifica que la API Key sea correcta"""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403, 
            detail="No autorizado. API key inválida"
        )
    return api_key

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejo global de excepciones"""
    return JSONResponse(
        status_code=500,
        content={"error": "Error interno del servidor", "detail": str(exc)}
    )

@app.get("/")
def root():
    """Endpoint principal para verificar que el servicio está funcionando"""
    return {
        "status": "ok", 
        "message": "Microservicio IA activo",
        "version": "1.0.0",
        "endpoints": [
            "/prediccion-asistencia",
            "/proyeccion-ingresos",
            "/ranking-equipos",
            "/prediccion-asistencia/{gym_id}",
            "/health",
            "/test-connection"
        ]
    }

@app.get("/health")
def health_check():
    """Endpoint de health check para monitoreo"""
    return {"status": "healthy", "timestamp": str(pd.Timestamp.now())}

@app.get("/test-connection")
def test_database_connection():
    """Endpoint para probar la conexión con la base de datos"""
    try:
        from utils.db import test_connection
        result = test_connection()
        return result
    except Exception as e:
        return {"status": "error", "message": f"Error al probar conexión: {str(e)}"}

@app.get("/prediccion-asistencia")
def get_prediccion_asistencia():
    """
    Endpoint para obtener predicciones de asistencia general
    
    Retorna análisis de riesgo de abandono de socios basado en:
    - Patrones de asistencia históricos
    - Inactividad por períodos
    - Tendencias de asistencia
    """
    try:
        result = prediccion_asistencia.run()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción de asistencia: {str(e)}")

@app.get("/proyeccion-ingresos")
def get_proyeccion_ingresos():
    """
    Endpoint para obtener proyecciones de ingresos
    
    Retorna proyecciones financieras basadas en:
    - Histórico de pagos
    - Tendencias de suscripciones
    - Análisis de métodos de pago
    """
    try:
        result = proyeccion_ingresos.run()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en proyección de ingresos: {str(e)}")

@app.get("/ranking-equipos")
def get_ranking_equipos():
    """
    Endpoint para obtener el ranking de equipos
    
    Retorna análisis de uso de equipos basado en:
    - Logs de uso históricos
    - Popularidad por categoría
    - Recomendaciones de optimización
    """
    try:
        result = clustering_equipos.run()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en ranking de equipos: {str(e)}")

# Endpoint adicional que acepta parámetros
@app.get("/prediccion-asistencia/{gym_id}")
def get_prediccion_asistencia_por_gym(gym_id: int):
    """
    Endpoint para obtener predicciones para un gimnasio específico
    
    Args:
        gym_id: ID del gimnasio (1=gym_master, 2=gym_norte, 3=gym_sur)
    
    Retorna análisis específico del gimnasio solicitado
    """
    try:
        if gym_id < 1:
            raise HTTPException(status_code=400, detail="ID de gimnasio debe ser mayor a 0")
            
        result = prediccion_asistencia.run_by_gym(gym_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción para gym {gym_id}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Configuración del servidor desde variables de entorno
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)