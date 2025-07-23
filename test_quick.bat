@echo off
REM Script simple para probar endpoints del microservicio IA

echo 🚀 Probando microservicio GYM MASTER IA
echo.

echo 📋 Información del servicio:
curl -s http://localhost:8000/ | python -m json.tool
echo.

echo 💗 Health check:
curl -s http://localhost:8000/health | python -m json.tool
echo.

echo 🔗 Test de conexión:
curl -s http://localhost:8000/test-connection | python -m json.tool
echo.

echo 📊 Predicción de asistencia:
curl -s http://localhost:8000/prediccion-asistencia | python -m json.tool
echo.

echo ✨ ¡Pruebas completadas!
pause
