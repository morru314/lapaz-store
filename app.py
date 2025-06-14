from flask import Flask, render_template
from config import Config
from extensions import db
from routes.stock import stock_routes
from routes.clientes import clientes_routes
from routes.ventas import ventas_routes
from routes.deudas import deudas_routes
from routes.dashboard import dashboard_routes
from flask import redirect
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    # Registrar Blueprints
    app.register_blueprint(stock_routes)
    app.register_blueprint(clientes_routes)
    app.register_blueprint(ventas_routes)
    app.register_blueprint(deudas_routes)
    app.register_blueprint(dashboard_routes)

    # ✅ Esta será la página principal
    @app.route("/")
    def index():
        return redirect("/dashboard")

    # Filtro personalizado para templates
    @app.template_filter('format_currency')
    def format_currency(value):
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return app

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        from models.models import *
        db.create_all()

    app.run(debug=True)
