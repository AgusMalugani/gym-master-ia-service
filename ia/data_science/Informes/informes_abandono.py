"""
Informe de Inactividad / Abandono - Gym Master
----------------------------------------------

Este módulo permite detectar socios potencialmente inactivos
según su última asistencia registrada.

Criterio:
- Si no asistió en las últimas N semanas, se considera "Inactivo".

Requisitos:
- pandas
"""

import pandas as pd
from datetime import datetime


def detectar_inactividad(asistencia_df: pd.DataFrame, semanas_umbral: int = 4) -> pd.DataFrame:
    """
    Detecta socios inactivos por gimnasio.

    Args:
        asistencia_df (pd.DataFrame): DataFrame con las asistencias, debe incluir 'gimnasio', 'socio_id', 'fecha'.
        semanas_umbral (int): Número de semanas sin asistir para considerar inactividad.

    Returns:
        pd.DataFrame: Socios con semanas sin asistir y estado (Activo/Inactivo).
    """
    asistencia_df['fecha'] = pd.to_datetime(asistencia_df['fecha'])
    hoy = pd.Timestamp(datetime.now().date())

    ultima_asistencia = (
        asistencia_df.groupby(['gimnasio', 'socio_id'])['fecha']
        .max()
        .reset_index(name='ultima_asistencia')
    )

    ultima_asistencia['semanas_sin_asistir'] = ultima_asistencia['ultima_asistencia'].apply(
        lambda x: ((hoy - x).days) // 7
    )

    ultima_asistencia['estado'] = ultima_asistencia['semanas_sin_asistir'].apply(
        lambda semanas: 'Inactivo' if semanas >= semanas_umbral else 'Activo'
    )

    return ultima_asistencia
