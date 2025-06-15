from flask import Blueprint, render_template
from flask_login import login_required
from models.models import Producto, Venta, Deuda, DetalleVenta
from datetime import datetime
from extensions import db

dashboard_routes = Blueprint('dashboard_routes', __name__, template_folder='../templates')

@dashboard_routes.route('/dashboard')
@login_required
def dashboard():
    hoy = datetime.today()
    primer_dia_mes = datetime(hoy.year, hoy.month, 1)
    primer_dia_anio = datetime(hoy.year, 1, 1)

    # Productos
    productos = Producto.query.all()
    total_productos = len(productos)
    total_unidades = sum(p.stock for p in productos)
    total_invertido = sum(p.stock * p.precio_compra for p in productos)
    valor_stock_venta = sum(p.stock * p.precio_venta for p in productos)
    stock_bajo = Producto.query.filter(Producto.stock <= 3).all()

    # Ventas
    ventas_mes = Venta.query.filter(Venta.fecha >= primer_dia_mes).all()
    facturacion_mtd = sum(v.total_cobrado or 0 for v in ventas_mes)

    ventas_anio = Venta.query.filter(Venta.fecha >= primer_dia_anio).all()
    facturacion_ytd = sum(v.total_cobrado or 0 for v in ventas_anio)

    detalles = DetalleVenta.query.all()
    total_facturado = sum(d.precio_cobrado * d.cantidad for d in detalles)

    # Deudas
    total_deudas = db.session.query(db.func.sum(Deuda.saldo_pendiente))\
        .filter(Deuda.saldo_pendiente > 0).scalar() or 0

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
