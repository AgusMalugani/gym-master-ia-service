"""
Descripción:
Este script genera un dataset simulado de pagos mensuales de 200 socios de un gimnasio durante 12 meses.
Cada socio tiene un perfil de pago (puntual, leve retraso o moroso crónico) que determina la probabilidad
de pagar a tiempo o con retraso, o incluso no pagar. También se aplican descuentos aleatorios a socios puntuales,
se simulan diferentes métodos de pago y se calculan días de retraso.

El resultado se guarda en formato CSV en:
gym-master/ia/data_science/Data_Lake/pagos_simulados.csv
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Configuraciones básicas
np.random.seed(42)
n_socios = 200
n_meses = 12
metodos_pago = ['Efectivo', 'Tarjeta', 'Transferencia', 'Débito automático']
niveles_suscripcion = {'Básico': 30, 'Estándar': 50, 'Premium': 70}
nivel_prob = [0.5, 0.3, 0.2]

# Generar socios con perfil de pago
socios = []
for socio_id in range(1, n_socios + 1):
    perfil_pago = np.random.choice(['puntual', 'leve_retraso', 'moroso'], p=[0.6, 0.25, 0.15])
    nivel = np.random.choice(list(niveles_suscripcion.keys()), p=nivel_prob)
    socios.append({'socio_id': socio_id, 'perfil_pago': perfil_pago, 'nivel': nivel})

socios_df = pd.DataFrame(socios)

# Simulación de pagos
pagos = []
start_date = datetime(2024, 7, 1)

for _, socio in socios_df.iterrows():
    for mes in range(n_meses):
        fecha_limite = start_date + pd.DateOffset(months=mes)
        monto_base = niveles_suscripcion[socio['nivel']]

        descuento = 0
        if socio['perfil_pago'] == 'puntual' and np.random.rand() < 0.2:
            descuento = np.random.choice([5, 10])  # $5 o $10 descuento
        monto_pagado = monto_base - descuento

        # Simular retraso
        if socio['perfil_pago'] == 'puntual':
            dias_retraso = int(np.random.choice([0, 1, 2], p=[0.85, 0.1, 0.05]))
        elif socio['perfil_pago'] == 'leve_retraso':
            dias_retraso = int(np.random.choice([0, 3, 5, 7], p=[0.3, 0.3, 0.3, 0.1]))
        else:  # moroso
            if np.random.rand() < 0.2:
                continue  # no paga ese mes
            dias_retraso = int(np.random.choice([5, 10, 15, 20], p=[0.4, 0.3, 0.2, 0.1]))

        fecha_pago = fecha_limite + timedelta(days=dias_retraso)
        metodo_pago = np.random.choice(metodos_pago, p=[0.3, 0.4, 0.2, 0.1])

        pagos.append({
            'pago_id': len(pagos) + 1,
            'socio_id': socio['socio_id'],
            'nivel': socio['nivel'],
            'perfil_pago': socio['perfil_pago'],
            'monto': monto_pagado,
            'descuento': descuento,
            'fecha_limite': fecha_limite.date(),
            'fecha_pago': fecha_pago.date(),
            'dias_retraso': dias_retraso,
            'metodo_pago': metodo_pago
        })

pagos_df = pd.DataFrame(pagos)

# Guardar el dataframe como CSV con ruta absoluta dinámica
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Data_Lake_CSV'))
os.makedirs(base_dir, exist_ok=True)

csv_path = os.path.join(base_dir, 'pagos_simulados.csv')
pagos_df.to_csv(csv_path, index=False)

print(f"✅ Dataset de pagos simulados guardado en {csv_path}")
