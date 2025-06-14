from app import create_app
from extensions import db
from models.models import *

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Base de datos creada correctamente.")
