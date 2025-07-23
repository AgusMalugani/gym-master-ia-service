"""
Informe de Retención de Usuarios por Rol - Gym Master
-----------------------------------------------------

Este módulo contiene la función para calcular la retención de usuarios por rol.
"""

import pandas as pd

def calcular_retencion_por_rol(usuario_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la retención de usuarios por rol.

    Args:
        usuario_df (pd.DataFrame): DataFrame con los datos de la tabla usuario.

    Returns:
        pd.DataFrame: Resumen por rol con total de usuarios, cantidad de activos 
                      y porcentaje de retención.
    """
    resumen = (
        usuario_df.groupby('rol')
        .agg(
            total_usuarios=('id', 'count'),
            usuarios_activos=('activo', lambda x: x.sum())
        )
        .reset_index()
    )
    resumen['porcentaje_retencion'] = (resumen['usuarios_activos'] / resumen['total_usuarios']) * 100
    return resumen
