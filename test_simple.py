#!/usr/bin/env python3
"""
Script simple para probar el microservicio sin autenticación
"""

import sys
import os
import subprocess

def test_endpoint(endpoint, description):
    """Prueba un endpoint usando curl"""
    print(f"\n🧪 {description}")
    print(f"   Endpoint: {endpoint}")
    
    try:
        # Usar curl para hacer la petición
        cmd = f'curl -s -w "\\n%{{http_code}}" http://localhost:8000{endpoint}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            response_body = '\n'.join(lines[:-1])
            status_code = lines[-1]
            
            print(f"   Status: {status_code}")
            
            if status_code == "200":
                print(f"   ✅ Éxito")
                # Mostrar primeras líneas de la respuesta
                if len(response_body) > 100:
                    print(f"   Respuesta: {response_body[:100]}...")
                else:
                    print(f"   Respuesta: {response_body}")
                return True
            else:
                print(f"   ❌ Error HTTP {status_code}")
                print(f"   Respuesta: {response_body}")
                return False
        else:
            print(f"   ❌ Respuesta inesperada: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Ejecuta las pruebas simples"""
    print("🚀 Pruebas simples del microservicio GYM MASTER IA")
    print("   Usando curl para las peticiones HTTP")
    
    # Verificar que curl esté disponible
    try:
        subprocess.run("curl --version", shell=True, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ curl no está disponible. Instala curl o usa 'python test_service.py'")
        return 1
    
    tests = [
        ("/", "Información del servicio"),
        ("/health", "Health check"),
        ("/test-connection", "Prueba de conexión"),
        ("/prediccion-asistencia", "Predicción de asistencia"),
        ("/proyeccion-ingresos", "Proyección de ingresos"),
        ("/ranking-equipos", "Ranking de equipos"),
        ("/prediccion-asistencia/1", "Predicción para gym 1"),
    ]
    
    results = []
    for endpoint, description in tests:
        success = test_endpoint(endpoint, description)
        results.append((endpoint, success))
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN")
    print("="*50)
    
    successful = 0
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {endpoint}")
        if success:
            successful += 1
    
    total = len(results)
    print(f"\n📈 {successful}/{total} pruebas exitosas ({successful/total*100:.1f}%)")
    
    if successful == total:
        print("🎉 ¡Todas las pruebas pasaron!")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
