@echo off
echo =============================
echo INICIANDO SISTEMA LA PAZ STORE - PRODUCCIÓN (Supabase)
echo =============================

REM 1. Activar entorno virtual (solo si no está activo)
IF NOT DEFINED VIRTUAL_ENV (
    echo 🔄 Activando entorno virtual...
    call venv\Scripts\activate
)

REM 2. Instalar dependencias
if exist requirements.txt (
    echo 📦 Instalando dependencias...
    pip install -r requirements.txt
) else (
    echo ⚠️ No se encontró 'requirements.txt'
)

REM 3. Ejecutar la app con Supabase configurado
echo 🚀 Ejecutando LaPazStoreWebApp en modo producción...
set FLASK_ENV=production
python app.py

echo.
pause
