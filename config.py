import os
import secrets

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Base de datos
    DB_PATH = os.path.join(BASEDIR, 'database', 'ventas.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.replace(os.sep, '/')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad y archivos
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(16)

    # Credenciales de administrador para autenticación básica
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')  # esto es clave
