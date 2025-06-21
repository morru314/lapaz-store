import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # Seguridad
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        if os.environ.get("FLASK_ENV") == "development":
            SECRET_KEY = secrets.token_hex(16)
        else:
            raise RuntimeError("SECRET_KEY environment variable is required")

    # Carpeta para uploads
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # Admin por defecto (solo si usás tu propio auth además de Supabase)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
