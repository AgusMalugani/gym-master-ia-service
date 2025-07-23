import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://brrxvwgjkuofcgdnmnfb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJycnh2d2dqa3VvZmNnZG5tbmZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzQxNjIsImV4cCI6MjA2NDc1MDE2Mn0.pJDbApLOkF0LGAAV-d4AJ-HUoQ-13FtLIVMJXwlqT5s")

# Cliente de Supabase global
supabase: Client = None

def get_supabase_client():
    """Obtiene el cliente de Supabase inicializándolo si es necesario"""
    global supabase
    if supabase is None:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"Error creando cliente Supabase: {e}")
            supabase = None
    return supabase

def get_asistencia_data():
    """
    Obtiene datos de asistencia desde Supabase
    """
    try:
        client = get_supabase_client()
        if client is None:
            print("Cliente Supabase no disponible, usando datos simulados")
            return get_simulated_asistencia()
            
        response = client.table("asistencia").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        print(f"Error obteniendo datos de asistencia: {e}")
        return get_simulated_asistencia()

def get_socios_data():
    """
    Obtiene datos de socios desde Supabase
    """
    try:
        client = get_supabase_client()
        response = client.table("socio").select("id_socio", "sexo", "fecnac", "activo").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        print(f"Error obteniendo datos de socios: {e}")
        return pd.DataFrame()

def get_usuarios_data():
    """
    Obtiene datos de usuarios desde Supabase
    """
    try:
        client = get_supabase_client()
        response = client.table("usuario").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        print(f"Error obteniendo datos de usuarios: {e}")
        return pd.DataFrame()

def test_connection():
    """
    Prueba la conexión con Supabase
    """
    try:
        client = get_supabase_client()
        # Intentar una consulta simple
        response = client.table("socio").select("count", count="exact").execute()
        return {"status": "success", "message": f"Conexión exitosa. Total socios: {response.count}"}
    except Exception as e:
        return {"status": "error", "message": f"Error de conexión: {str(e)}"}

# Funciones de respaldo para datos simulados si la conexión falla
def get_simulated_asistencia():
    """Datos simulados de asistencia para desarrollo/testing"""
    import numpy as np
    from datetime import datetime, timedelta
    
    np.random.seed(42)
    fechas = pd.date_range(start=datetime.now() - timedelta(days=90), periods=90)
    
    data = []
    for fecha in fechas:
        # Simular entre 50-150 asistencias por día
        n_asistencias = np.random.randint(50, 150)
        for _ in range(n_asistencias):
            data.append({
                'fecha': fecha,
                'socio_id': np.random.randint(1, 200),
                'hora_entrada': np.random.choice(['06:00', '07:00', '08:00', '18:00', '19:00', '20:00']),
                'gimnasio': 'gym_master'
            })
    
    return pd.DataFrame(data)

def get_simulated_socios():
    """Datos simulados de socios para desarrollo/testing"""
    import numpy as np
    np.random.seed(42)
    
    data = []
    for i in range(1, 201):  # 200 socios
        data.append({
            'id_socio': i,
            'sexo': np.random.choice(['M', 'F']),
            'fecnac': f"199{np.random.randint(0, 9)}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
            'activo': np.random.choice([True, False], p=[0.85, 0.15])
        })
    
    return pd.DataFrame(data)