#!/bin/bash

# Script de inicio para GymMaster IA Service
echo "🚀 Iniciando GymMaster IA Service..."

# Verificar versión de Python
echo "📋 Python version: $(python --version)"

# Verificar dependencias críticas
echo "📦 Verificando dependencias..."
python -c "import fastapi, pandas, sklearn; print('✅ Dependencias OK')"

# Ejecutar aplicación
echo "🏃 Ejecutando aplicación..."
exec python main.py
