# GYM MASTER - Microservicio de IA

Este microservicio proporciona análisis de inteligencia artificial para el sistema GYM MASTER, incluyendo predicciones de asistencia, proyecciones de ingresos y análisis de uso de equipos.

## 🚀 Instalación y Configuración

### 1. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configuración de Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales reales:
- `API_KEY`: Clave de autenticación para el microservicio
- `SUPABASE_URL`: URL de tu instancia de Supabase
- `SUPABASE_KEY`: Clave de API de Supabase

### 3. Ejecutar el Servicio

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 Endpoints Disponibles

### Autenticación (DESHABILITADA en desarrollo)
⚠️ **Nota:** La autenticación está temporalmente deshabilitada para facilitar el desarrollo y testing.

En producción, todos los endpoints principales requerirán el header:
```
X-API-Key: tu_api_key_aqui
```

### Endpoints Principales

#### `GET /`
Información general del servicio y lista de endpoints disponibles.

#### `GET /health`
Health check del servicio.

#### `GET /test-connection`
Prueba la conexión con la base de datos Supabase.

#### `GET /prediccion-asistencia`
Obtiene predicciones de asistencia general basadas en:
- Análisis de inactividad de socios
- Tendencias de asistencia
- Clasificación por riesgo de abandono

**Respuesta ejemplo:**
```json
{
  "predicciones": {
    "riesgo_bajo": 45,
    "riesgo_medio": 30,
    "riesgo_alto": 10,
    "inactivos": 5,
    "totales": 90
  },
  "tendencia": "estable",
  "recomendacion": "Enviar notificaciones personalizadas a usuarios de riesgo alto",
  "metricas_adicionales": {
    "asistencias_ultima_semana": 856,
    "asistencias_semana_anterior": 823,
    "cambio_porcentual": 4.01
  }
}
```

#### `GET /prediccion-asistencia/{gym_id}`
Obtiene predicciones específicas para un gimnasio.

**Parámetros:**
- `gym_id`: ID del gimnasio (1=gym_master, 2=gym_norte, 3=gym_sur)

#### `GET /proyeccion-ingresos`
Obtiene proyecciones de ingresos basadas en:
- Histórico de pagos
- Tendencias de suscripciones
- Análisis de métodos de pago

**Respuesta ejemplo:**
```json
{
  "proyeccion": {
    "proximo_mes": 12500.50,
    "siguiente_trimestre": 38000.00,
    "proximo_año": 155000.00
  },
  "por_mes": {
    "Enero": 11800.00,
    "Febrero": 12100.00,
    "Marzo": 12500.00
  },
  "factores_crecimiento": [
    "Método de pago predominante: Tarjeta",
    "Nivel de suscripción popular: Básico"
  ],
  "factores_riesgo": [
    "Competencia en el sector fitness"
  ]
}
```

#### `GET /ranking-equipos`
Obtiene análisis de uso de equipos basado en:
- Logs de uso históricos
- Popularidad por categoría
- Recomendaciones de optimización

**Respuesta ejemplo:**
```json
{
  "ranking_popularidad": [
    {
      "equipo": "Cinta de correr",
      "uso_promedio": 85.3,
      "categoria": "Cardio"
    }
  ],
  "categorias_populares": {
    "Cardio": 75.2,
    "Fuerza": 68.9,
    "Funcional": 45.6
  },
  "recomendaciones": [
    "Considerar añadir más unidades de Cinta de correr",
    "Ampliar zona de Cardio por alta demanda"
  ]
}
```

## 🗄️ Estructura de Datos

### Fuentes de Datos Utilizadas

1. **Supabase (Base de datos principal):**
   - Tabla `asistencia`: Registros de asistencia de socios
   - Tabla `socio`: Información de socios
   - Tabla `usuario`: Datos de usuarios del sistema

2. **Data Lake (archivos procesados):**
   - `ia/data_science/Data_Lake/Processed/asistencias/gym_master_asistencias.parquet`
   - `ia/data_science/Data_Lake/Processed/logs_uso/gym_master_logs_uso.parquet`
   - `ia/data_science/Data_Lake_CSV/pagos_simulados.csv`

### Modelos de IA Integrados

1. **Predicción de Asistencia (`models/prediccion_asistencia.py`):**
   - Utiliza `ia.data_science.Informes.informes_abandono`
   - Utiliza `ia.data_science.ETL.etl_login`

2. **Proyección de Ingresos (`models/proyeccion_ingresos.py`):**
   - Analiza datos de `pagos_simulados.csv`
   - Calcula tendencias y proyecciones financieras

3. **Clustering de Equipos (`models/clustering_equipos.py`):**
   - Analiza logs de uso de equipos
   - Genera rankings y recomendaciones

## 🔧 Desarrollo y Testing

### Datos de Prueba
Si no hay conexión a Supabase, el sistema automáticamente utiliza datos simulados para desarrollo.

### Manejo de Errores
- Logs detallados de errores
- Respuestas JSON estructuradas para errores
- Fallback a datos simulados cuando la conexión falla

### Monitoreo
- Endpoint `/health` para health checks
- Endpoint `/test-connection` para verificar conectividad
- Logs de aplicación para debugging

## 🚀 Despliegue

### Variables de Entorno para Producción
```bash
API_KEY=your_secure_api_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Docker (Opcional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 📝 Notas de Integración

1. **Autenticación:** Todos los endpoints requieren API Key en el header `X-API-Key`
2. **CORS:** Configurado para aceptar requests desde `localhost:3000`, `localhost:8080` y el dominio de producción
3. **Formato de Respuesta:** Todas las respuestas son en formato JSON
4. **Manejo de Errores:** HTTP status codes apropiados (400, 403, 404, 500)

## 🤝 Contribución

Al modificar los modelos de IA:
1. Mantén la estructura de respuesta JSON existente
2. Agrega nuevas métricas en `metricas_adicionales`
3. Documenta nuevos endpoints en este README
4. Realiza pruebas con datos simulados antes de integrar datos reales
