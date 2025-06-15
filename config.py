# config.py
import os
import secrets

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Base de datos
    DB_PATH = os.path.join(BASEDIR, 'database', 'ventas.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.replace(os.sep, '/')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad y archivos
    # La clave secreta se obtiene de la variable de entorno SECRET_KEY para evitar
    # exponerla en el código fuente. Si no está definida, se genera una de
    # forma aleatoria en ejecución.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')  # esto es clave
