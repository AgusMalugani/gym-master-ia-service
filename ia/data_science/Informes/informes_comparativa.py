"""
Informes Comparativos entre Gimnasios - Gym Master
--------------------------------------------------

Este módulo contiene funciones para generar métricas comparativas entre distintos gimnasios
a partir de los datos consolidados de usuarios, asistencias y rutinas.

Métricas disponibles:
1. Retención por gimnasio.
2. Asistencias promedio por socio por gimnasio.
3. Concurrencia promedio por día de la semana por gimnasio.
4. Concurrencia promedio por hora por gimnasio.

✅ Resumen de funciones
calcular_retencion_por_gimnasio: % de usuarios activos por gimnasio.

asistencias_promedio_por_socio: promedio de asistencias por socio.

concurrencia_promedio_por_dia: concurrencia total por día de la semana.

concurrencia_promedio_por_hora: concurrencia total por hora.
"""

import pandas as pd


def calcular_retencion_por_gimnasio(usuario_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la retención de usuarios activos por gimnasio.

    Args:
        usuario_df (pd.DataFrame): DataFrame con los usuarios, debe incluir columnas 'gimnasio' y 'activo'.

    Returns:
        pd.DataFrame: Retención (%) y cantidad de usuarios activos por gimnasio.
    """
    resumen = (
        usuario_df.groupby('gimnasio')
        .agg(
            total_usuarios=('id', 'count'),
            usuarios_activos=('activo', lambda x: x.sum())
        )
        .reset_index()
    )
    resumen['retencion_%'] = (resumen['usuarios_activos'] / resumen['total_usuarios']) * 100
    return resumen


def asistencias_promedio_por_socio(asistencia_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la cantidad promedio de asistencias por socio en cada gimnasio.

    Args:
        asistencia_df (pd.DataFrame): DataFrame con las asistencias, debe incluir 'gimnasio' y 'socio_id'.

    Returns:
        pd.DataFrame: Promedio de asistencias por socio por gimnasio.
    """
    asistencias_por_gimnasio = (
        asistencia_df.groupby(['gimnasio', 'socio_id'])
        .size()
        .groupby('gimnasio')
        .mean()
        .reset_index(name='asistencias_promedio_por_socio')
    )
    return asistencias_por_gimnasio


def concurrencia_promedio_por_dia(asistencia_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la concurrencia promedio por día de la semana en cada gimnasio.

    Args:
        asistencia_df (pd.DataFrame): DataFrame con las asistencias, debe incluir 'gimnasio' y 'fecha'.

    Returns:
        pd.DataFrame: Concurrencia promedio por día de la semana y gimnasio.
    """
    asistencia_df['dia_semana'] = pd.to_datetime(asistencia_df['fecha']).dt.day_name()

    concurrencia = (
        asistencia_df.groupby(['gimnasio', 'dia_semana'])
        .size()
        .reset_index(name='total_asistencias')
    )

    return concurrencia


def concurrencia_promedio_por_hora(asistencia_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la concurrencia promedio por hora en cada gimnasio.

    Args:
        asistencia_df (pd.DataFrame): DataFrame con las asistencias, debe incluir 'gimnasio' y 'hora_ingreso'.

    Returns:
        pd.DataFrame: Concurrencia promedio por hora y gimnasio.
    """
    asistencia_df['hora'] = asistencia_df['hora_ingreso'].astype(str).str[:5]

    concurrencia = (
        asistencia_df.groupby(['gimnasio', 'hora'])
        .size()
        .reset_index(name='total_asistencias')
    )

    return concurrencia
