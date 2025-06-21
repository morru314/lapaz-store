from app import app
from extensions import db
from models.models import *

with app.app_context():
    db.create_all()
    print("✅ Base de datos creada correctamente.")
