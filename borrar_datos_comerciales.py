from flask import Flask
from extensions import db
from models.models import Cliente, Venta, DetalleVenta, Deuda, Pago
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    try:
        # Orden correcta para evitar errores por claves foráneas
        print("🧹 Eliminando detalles de venta...")
        db.session.query(DetalleVenta).delete()

        print("🧹 Eliminando ventas...")
        db.session.query(Venta).delete()

        print("🧹 Eliminando deudas...")
        db.session.query(Deuda).delete()

        print("🧹 Eliminando pagos...")
        db.session.query(Pago).delete()

        print("🧹 Eliminando clientes...")
        db.session.query(Cliente).delete()

        db.session.commit()
        print("✅ Todos los datos de ventas, clientes y deudas han sido eliminados correctamente.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al borrar datos: {e}")
