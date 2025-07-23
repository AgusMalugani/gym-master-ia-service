#!/usr/bin/env python3
"""
Script de debugging para probar el modelo de proyección de ingresos
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from models import proyeccion_ingresos

def test_proyeccion_ingresos():
    """Prueba directa del modelo de proyección"""
    print("🧪 Probando modelo de proyección de ingresos...")
    
    try:
        result = proyeccion_ingresos.run()
        print("✅ Éxito!")
        print(f"Resultado: {result}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_proyeccion_ingresos()
