@echo off
echo =============================
echo INICIANDO SISTEMA LA PAZ STORE
echo =============================

REM 1. Crear entorno virtual si no existe
if not exist venv (
    echo 🔧 Creando entorno virtual...
    python -m venv venv
)

REM 2. Activar entorno virtual
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate

REM 3. Instalar dependencias
if exist requirements.txt (
    echo 📦 Instalando dependencias...
    pip install -r requirements.txt
) else (
    echo ⚠️ No se encontró 'requirements.txt'
)

REM 4. Crear base de datos si no existe
if not exist database\ventas.db (
    echo 🗃️  Creando base de datos...
    if exist init_db.py (
        python init_db.py
    ) else (
        echo ❌ No se encontró el archivo init_db.py
    )
) else (
    echo ✅ Base de datos ya existe.
)

REM 5. Ejecutar la app
echo 🚀 Ejecutando LaPazStoreWebApp...
python app.py

REM 6. Pausar consola al final
echo.
pause
