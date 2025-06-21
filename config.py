import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Base de datos: Supabase
    DB_PATH = os.path.join(BASEDIR, 'database', 'ventas.db')
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
        print(
            f"[!] SQLALCHEMY_DATABASE_URI not set. Using SQLite database at {SQLALCHEMY_DATABASE_URI}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad y archivos
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(16)
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # Admin por defecto (opcional si usás Supabase Auth)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
