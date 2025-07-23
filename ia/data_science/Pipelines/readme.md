Pipelines de Data Science - Gym Master

Este directorio contiene distintos pipelines de procesamiento, análisis y modelado de datos utilizados en el proyecto Gym Master.

Descripción de archivos

logs_qr_pipeline.py

Genera datos simulados de ingresos al gimnasio mediante QR y los inserta en la tabla logs_qr en Supabase. Es la base para análisis de comportamiento y modelos predictivos de asistencia.

pipeline_abandono.py

Pipeline para el modelado predictivo de abandono de socios. Permite anticipar posibles bajas en la membresía.

pipeline_carga_data_lake.py

Carga y procesamiento de datos desde fuentes originales al Data Lake. Diseñado para mover datos en bruto a una capa estructurada.

pipeline_carga_data_lake_multi.py

Versión extendida del pipeline de carga, soportando múltiples fuentes y formatos.

pipeline_comparativa.py

Genera reportes comparativos de métricas entre periodos (ej: mes a mes o año contra año).

pipeline_horarios.py

Análisis y visualización de concurrencia por horarios y días de la semana. Fundamental para optimizar horarios y recursos.

pipeline_retencion.py

Modelo predictivo para calcular la probabilidad de retención de cada socio y generar estrategias proactivas.

Uso sugerido

Cada pipeline se puede ejecutar de forma independiente.

Para flujos automatizados, se recomienda centralizar la ejecución con un orquestador tipo Airflow, Prefect o un script maestro.

Complementar con los scripts en ia/data_science/scripts y las notebooks de exploración en EDA.