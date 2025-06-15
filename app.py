from flask import Flask, render_template, redirect
from config import Config
from extensions import db, login_manager
from routes.stock import stock_routes
from routes.clientes import clientes_routes
from routes.ventas import ventas_routes
from routes.deudas import deudas_routes
from routes.dashboard import dashboard_routes
from routes.auth import auth_routes
import os

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth_routes.login'

@login_manager.user_loader
def load_user(user_id):
    from models.models import User
    return User.query.get(int(user_id))

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

import os

if __name__ == "__main__":
    with app.app_context():
        from models.models import *

        print(f"[*] DB PATH: {Config.DB_PATH}")
        print(f"[*] DB exists? {os.path.exists(Config.DB_PATH)}")

        if os.path.exists(Config.DB_PATH):
            print("[*] Existing tables in DB:")
            tables = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            for t in tables:
                print(" -", t[0])
        else:
            print("[!] Database file NOT found!")

        db.create_all()
        print("[*] db.create_all() executed")

        # Crear usuario admin si no existe
        admin = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
        if not admin:
            print("[*] Admin not found, creating...")
            admin = User(
                username=Config.ADMIN_USERNAME,
                full_name="Administrador",
                email="admin@example.com",
                perfil="Admin",
            )
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
        else:
            print("[*] Admin already exists.")
