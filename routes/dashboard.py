from flask import Blueprint, render_template, session, redirect, url_for
from supabase_client import supabase
from datetime import datetime
import os

# Blueprint

dashboard_routes = Blueprint('dashboard_routes', __name__, template_folder='../templates')

# Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Decorador para validar login con Supabase
from functools import wraps

def login_required_sb(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("sb_token"):
            return redirect(url_for("auth_routes.login"))
        return f(*args, **kwargs)
    return decorated_function


@dashboard_routes.route('/dashboard')
@login_required_sb
def dashboard():
    hoy = datetime.today()
    primer_dia_mes = datetime(hoy.year, hoy.month, 1).isoformat()
    primer_dia_anio = datetime(hoy.year, 1, 1).isoformat()

    # Productos
    productos = supabase.table("productos").select("*").execute().data
    total_productos = len(productos)
    total_unidades = sum(p['stock'] for p in productos)
    total_invertido = sum(p['stock'] * p['precio_compra'] for p in productos)
    valor_stock_venta = sum(p['stock'] * p['precio_venta'] for p in productos)
    stock_bajo = [p for p in productos if p['stock'] <= 3]

    # Ventas
    ventas_mes = supabase.table("ventas").select("*").gte("fecha", primer_dia_mes).execute().data
    facturacion_mtd = sum(v['total_cobrado'] or 0 for v in ventas_mes)

    ventas_anio = supabase.table("ventas").select("*").gte("fecha", primer_dia_anio).execute().data
    facturacion_ytd = sum(v['total_cobrado'] or 0 for v in ventas_anio)

    detalles = supabase.table("detalle_venta").select("*").execute().data
    total_facturado = sum(d['precio_cobrado'] * d['cantidad'] for d in detalles)

    # Deudas
    deudas = supabase.table("deudas").select("saldo_pendiente").execute().data
    total_deudas = sum(d['saldo_pendiente'] for d in deudas if d['saldo_pendiente'] > 0)

    return render_template(
        "index.html",
        stock_bajo=stock_bajo,
        ventas_mes=facturacion_mtd,
        total_deudas=total_deudas,
        facturacion_mtd=facturacion_mtd,
        facturacion_ytd=facturacion_ytd,
        total_productos=total_productos,
        total_unidades=total_unidades,
        total_invertido=total_invertido,
        valor_stock_venta=valor_stock_venta,
        total_facturado=total_facturado
    )
