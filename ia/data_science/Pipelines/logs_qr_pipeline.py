"""
Pipeline para la simulación e inserción de logs QR en Supabase.

Este script genera un conjunto de logs simulados que representan ingresos al gimnasio mediante el escaneo de un código QR.
Cada log contiene:
- socio_id: Identificador del socio.
- timestamp: Fecha y hora del acceso.
- dispositivo: Dispositivo desde el cual se escaneó el QR.
- fecha: Fecha simplificada (AAAA-MM-DD).
- hora: Hora del acceso.

Los registros simulados se insertan en la tabla 'logs_qr' de la base de datos Supabase definida por las credenciales.

"""

import pandas as pd
from datetime import datetime, timedelta
import random
from supabase import create_client, Client

# ===========================
# Configuración de conexión a Supabase
# ===========================
SUPABASE_URL = "https://brrxvwgjkuofcgdnmnfb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===========================
# Generador de logs QR simulados
# ===========================
def generar_logs_qr(n_logs=500):
    usuarios = [f'socio_{i}' for i in range(1, 21)]
    dispositivos = ['mobile', 'tablet', 'kiosk']
    logs = []
    base_time = datetime.now() - timedelta(days=30)
    
    for _ in range(n_logs):
        socio = random.choice(usuarios)
        timestamp = base_time + timedelta(
            days=random.randint(0, 29),
            hours=random.randint(6, 22),
            minutes=random.randint(0, 59)
        )
        dispositivo = random.choice(dispositivos)
        logs.append({
            'socio_id': socio,
            'timestamp': timestamp.isoformat(),
            'dispositivo': dispositivo,
            'fecha': timestamp.date().isoformat(),
            'hora': timestamp.hour
        })
    return logs

# ===========================
# Generación de logs
# ===========================
logs = generar_logs_qr()
print(f"Generados {len(logs)} logs QR simulados.\n")

# ===========================
# Inserción en Supabase con depuración
# ===========================
for idx, log in enumerate(logs, 1):
    response = supabase.table('logs_qr').insert(log).execute()

    if response.data is None:
        print(f"[{idx}] Error al insertar log: {log}")
    else:
        print(f"[{idx}] Log insertado correctamente.")

print("\nProceso de inserción finalizado.")