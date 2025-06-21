import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Base de datos: Supabase
    DB_PATH = os.path.join(BASEDIR, 'database', 'ventas.db')
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad y archivos
    # "SECRET_KEY" debe estar definido en el entorno para producción.
    # Si FLASK_ENV=development y no se definió, se genera uno temporal.
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        if os.environ.get("FLASK_ENV") == "development":
            SECRET_KEY = secrets.token_hex(16)
        else:
            raise RuntimeError("SECRET_KEY environment variable is required")
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # Admin por defecto (opcional si usás Supabase Auth)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
