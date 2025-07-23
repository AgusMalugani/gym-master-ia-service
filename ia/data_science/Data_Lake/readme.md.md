
# 🗂️ Data Lake - Gym Master

## 📌 Descripción

Este Data Lake centraliza y consolida la información de **todos los gimnasios** gestionados en Gym Master. La arquitectura está diseñada para soportar:
- Análisis globales y comparativas entre gimnasios.
- Modelos de Machine Learning centralizados.
- Dashboards y reporting avanzados.

La estructura sigue un enfoque en **capas**, actualmente implementamos la capa **Processed** con datos limpios y unificados.

---

## 📂 Estructura de Carpetas

```
ia/data_science/Data_Lake/Processed/
│
├── usuarios/
│    └── {gimnasio}_usuarios.parquet
│
├── asistencias/
│    └── {gimnasio}_asistencias.parquet
│
├── rutinas/
│    └── {gimnasio}_rutinas.parquet
│
└── logs_uso/
     └── {gimnasio}_logs_uso.parquet
```

Cada archivo Parquet lleva el prefijo del gimnasio correspondiente.

---

## 🏷️ Esquema de Datos

### usuarios
| campo     | tipo    |
|-----------|---------|
| socio_id  | UUID    |
| gimnasio  | texto   |
| email     | texto   |
| sexo      | M/F     |
| edad      | int     |
| nivel     | texto   |
| objetivo  | texto   |
| rol       | texto   |
| activo    | bool    |
| creado_en | timestamp |

---

### asistencias
| campo         | tipo    |
|---------------|---------|
| asistencia_id | UUID    |
| socio_id      | UUID    |
| gimnasio      | texto   |
| fecha         | date    |
| dia_semana    | texto   |
| hora_ingreso  | time    |
| hora_egreso   | time    |
| creado_en     | timestamp |

---

### rutinas
| campo     | tipo    |
|-----------|---------|
| rutina_id | UUID    |
| socio_id  | UUID    |
| gimnasio  | texto   |
| semana    | int     |
| nombre    | texto   |
| contenido | JSON    |
| creado_en | timestamp |

---

### logs_uso
| campo     | tipo    |
|-----------|---------|
| log_id    | UUID    |
| gimnasio  | texto   |
| usuario_id| UUID    |
| accion    | texto   |
| detalle   | texto   |
| fecha_hora| timestamp |

---

## ⚙️ Pipelines Disponibles

### 1. Crear estructura Parquet vacía
```
python ia/data_science/Setup/setup_data_lake.py
```

### 2. Cargar datos al Data Lake
```
python ia/data_science/Pipelines/pipeline_carga_data_lake.py
```

> Este pipeline toma los datos del ETL, los unifica y los guarda en las carpetas correspondientes.

---

## 🚀 Próximos pasos

- Implementar capa **Raw** para almacenamiento de datos crudos.
- Particionar Parquet por fechas o gimnasio para optimizar queries.
- Integrar logs de uso reales.
- Implementar versiones en la capa **Aggregated** para modelos ML.

---

## 📅 Actualizado por
**Octavio Alvarez** - Julio 2025
