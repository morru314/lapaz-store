from flask import Flask
from extensions import db
from models.models import Producto
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    try:
        deleted = db.session.query(Producto).delete()
        db.session.commit()
        print(f"✅ Se eliminaron {deleted} productos de la base de datos.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al borrar productos: {e}")
