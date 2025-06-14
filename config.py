# config.py
import os

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Base de datos
    DB_PATH = os.path.join(BASEDIR, 'database', 'ventas.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.replace(os.sep, '/')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad y archivos
    SECRET_KEY = 'tu_clave_secreta'
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')  # esto es clave
