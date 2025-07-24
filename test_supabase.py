#!/usr/bin/env python3
"""
Script de prueba para verificar conexión con Supabase
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_supabase_client

def test_supabase_connection():
    """Prueba la conexión con Supabase"""
    print("🔍 Probando conexión con Supabase...")
    
    try:
        client = get_supabase_client()
        
        if client is None:
            print("❌ No se pudo obtener cliente de Supabase")
            return False
        
        # Probar una consulta simple
        response = client.table('socio').select('id_socio').limit(1).execute()
        
        if response.data:
            print(f"✅ Conexión exitosa! Datos encontrados: {len(response.data)} registros")
            return True
        else:
            print("⚠️ Conexión OK pero sin datos en tabla 'socio'")
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    if success:
        print("🚀 Listo para deploy en Render!")
    else:
        print("💥 Revisar configuración de Supabase")
