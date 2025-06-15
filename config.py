import os
import secrets

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Base de datos
    DB_PATH = os.path.join(BASEDIR, 'database', 'ventas.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{DB_PATH.replace(os.sep, '/')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad y archivos
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # Admin por defecto
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
