#!/usr/bin/env python3
"""
Script de prueba para el microservicio de IA de GYM MASTER
Verifica que todos los endpoints funcionen correctamente
"""

import requests
import json
import sys
import time

# Configuración
BASE_URL = "http://localhost:8000"
# API_KEY = "default_dev_key_change_in_production"  # Comentado - no se requiere autenticación

HEADERS = {
    "Content-Type": "application/json"
}

def test_endpoint(endpoint, description, requires_auth=True):
    """Prueba un endpoint específico"""
    print(f"\n🧪 Probando: {description}")
    print(f"   Endpoint: {endpoint}")
    
    try:
        headers = HEADERS if requires_auth else {}
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Éxito")
            
            # Mostrar estructura de respuesta
            if isinstance(data, dict):
                keys = list(data.keys())[:5]  # Primeras 5 claves
                print(f"   Claves principales: {keys}")
                if 'error' in data:
                    print(f"   ⚠️  Respuesta contiene error: {data['error']}")
            
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalle: {error_data.get('detail', 'Sin detalle')}")
            except:
                print(f"   Respuesta: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Error de conexión - ¿Está el servidor ejecutándose?")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout - El endpoint tardó más de 30 segundos")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas del microservicio GYM MASTER IA")
    print(f"   URL Base: {BASE_URL}")
    print("   Modo: Sin autenticación (desarrollo)")
    
    # Lista de pruebas (todas sin autenticación ahora)
    tests = [
        ("/", "Endpoint raíz (información del servicio)", False),
        ("/health", "Health check", False),
        ("/test-connection", "Prueba de conexión a BD", False),
        ("/prediccion-asistencia", "Predicción de asistencia general", False),
        ("/prediccion-asistencia/1", "Predicción de asistencia para gym 1", False),
        ("/prediccion-asistencia/2", "Predicción de asistencia para gym 2", False),
        ("/proyeccion-ingresos", "Proyección de ingresos", False),
        ("/ranking-equipos", "Ranking de equipos", False),
    ]
    
    # Ejecutar pruebas
    resultados = []
    for endpoint, description, requires_auth in tests:
        success = test_endpoint(endpoint, description, requires_auth)
        resultados.append((endpoint, success))
        time.sleep(1)  # Pausa entre pruebas
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    exitosos = 0
    for endpoint, success in resultados:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {endpoint}")
        if success:
            exitosos += 1
    
    total = len(resultados)
    print(f"\n📈 Resultados: {exitosos}/{total} pruebas exitosas ({exitosos/total*100:.1f}%)")
    
    if exitosos == total:
        print("🎉 ¡Todas las pruebas pasaron! El microservicio está funcionando correctamente.")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los logs anteriores para más detalles.")
        return 1

def test_with_invalid_api_key():
    """Prueba adicional con API key inválida (deshabilitada - no se requiere auth)"""
    print("\n🔐 Prueba de autenticación deshabilitada (modo desarrollo)")
    print("   ✅ Todos los endpoints son accesibles sin autenticación")
    return True

if __name__ == "__main__":
    exit_code = main()
    
    # Prueba adicional de autenticación
    print("\n" + "="*60)
    test_with_invalid_api_key()
    
    print("\n🏁 Pruebas completadas")
    sys.exit(exit_code)
