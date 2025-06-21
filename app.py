from flask import Flask, render_template, redirect
from config import Config
from routes.stock import stock_routes
from routes.clientes import clientes_routes
from routes.ventas import ventas_routes
from routes.deudas import deudas_routes
from routes.dashboard import dashboard_routes
from routes.auth import auth_routes
from supabase_client import supabase
from flask_login import LoginManager, current_user
from models.usuario import Usuario  # Asegurate de tener este modelo

import os

# Flask app
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_routes.login"  # Redirige si no está logueado
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Registrar rutas
app.register_blueprint(stock_routes)
app.register_blueprint(clientes_routes)
app.register_blueprint(ventas_routes)
app.register_blueprint(deudas_routes)
app.register_blueprint(dashboard_routes)
app.register_blueprint(auth_routes)

# Redirección al dashboard
@app.route("/")
def index():
    return redirect("/dashboard")

# Filtro para moneda
@app.template_filter('format_currency')
def format_currency(value):
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Correr app
if __name__ == "__main__":
    if not os.environ.get("RENDER"):
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
