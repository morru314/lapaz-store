from flask import Flask, render_template, redirect
from config import Config
from extensions import db
from routes.stock import stock_routes
from routes.clientes import clientes_routes
from routes.ventas import ventas_routes
from routes.deudas import deudas_routes
from routes.dashboard import dashboard_routes
from routes.auth import auth_routes
import os

# Supabase client
from supabase import create_client, Client

# Crear cliente de Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar SQLAlchemy
db.init_app(app)

# Crear las tablas siempre que arranca la app
with app.app_context():
    from models.models import *
    db.create_all()
    print("[*] Tablas inicializadas en Supabase Postgres")

# Registrar rutas
app.register_blueprint(stock_routes)
app.register_blueprint(clientes_routes)
app.register_blueprint(ventas_routes)
app.register_blueprint(deudas_routes)
app.register_blueprint(dashboard_routes)
app.register_blueprint(auth_routes)

@app.route("/")
def index():
    return redirect("/dashboard")

@app.template_filter('format_currency')
def format_currency(value):
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

if __name__ == "__main__":
    if not os.environ.get("RENDER"):
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
