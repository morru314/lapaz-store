from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models.models import Producto
import pandas as pd
import os
from config import Config

stock_routes = Blueprint('stock_routes', __name__, template_folder='../templates')

from models.models import DetalleVenta

@stock_routes.route('/stock')
@login_required
def stock():
    productos = Producto.query.all()

    total_productos = len(productos)
    total_stock = sum(p.stock for p in productos)
    valor_stock_compra = sum(p.stock * p.precio_compra for p in productos)
    valor_stock_venta = sum(p.stock * p.precio_venta for p in productos)

    detalles = DetalleVenta.query.all()
    facturacion = sum(d.precio_cobrado * d.cantidad for d in detalles)

    return render_template(
        'stock.html',
        productos=productos,
        total_productos=total_productos,
        total_stock=total_stock,
        valor_stock_compra=valor_stock_compra,
        valor_stock_venta=valor_stock_venta,
        facturacion=facturacion
    )

@stock_routes.route('/stock/editar/<int:id>', methods=['GET'])
@login_required
def mostrar_formulario_edicion(id):
    producto = Producto.query.get_or_404(id)
    return render_template('editar_producto.html', producto=producto)

@stock_routes.route('/stock/eliminar/<int:id>', methods=['GET'])
@login_required
def confirmar_eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    return render_template('confirmar_eliminar.html', producto=producto)

@stock_routes.route('/stock/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash(f'Producto "{producto.nombre}" eliminado correctamente.')
    return redirect(url_for('stock_routes.stock'))

@stock_routes.route('/stock/editar/<int:id>', methods=['POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    producto.nombre = request.form['nombre']
    producto.descripcion = request.form['descripcion']
    producto.familia = request.form['familia']
    producto.talle = request.form['talle']
    producto.color = request.form['color']
    producto.proveedor = request.form['proveedor']
    producto.precio_compra = float(request.form['precio_compra'])
    producto.precio_venta = float(request.form['precio_venta'])
    producto.stock = max(0, int(request.form['stock']))
    db.session.commit()
    flash(f'Producto {producto.nombre} actualizado correctamente.')
    return redirect(url_for('stock_routes.stock'))

@stock_routes.route('/stock/cargar', methods=['GET', 'POST'])
@login_required
def cargar_stock():
    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo and archivo.filename.endswith(('.csv', '.xlsx')):
            ruta = os.path.join(Config.UPLOAD_FOLDER, archivo.filename)
            archivo.save(ruta)

            try:
                if ruta.endswith('.csv'):
                    df = pd.read_csv(ruta, sep=';')
                else:
                    df = pd.read_excel(ruta)

                df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

                columnas_obligatorias = {
                    'codigo', 'nombre', 'familia', 'talle', 'color',
                    'proveedor', 'precio_compra', 'precio_venta_contado',
                    'precio_venta_tarjeta', 'stock'
                }

                if not columnas_obligatorias.issubset(df.columns):
                    flash('El archivo no tiene las columnas requeridas.')
                    return redirect(url_for('stock_routes.stock'))

                for _, row in df.iterrows():
                    producto = Producto.query.filter_by(codigo=row['codigo']).first()
                    if producto:
                        producto.nombre = row['nombre']
                        producto.familia = row['familia']
                        producto.talle = row['talle']
                        producto.color = row['color']
                        producto.proveedor = row['proveedor']
                        producto.precio_compra = float(str(row['precio_compra']).replace('$', '').replace('.', '').replace(',', '.').strip())
                        producto.precio_venta = float(str(row['precio_venta_contado']).replace('$', '').replace('.', '').replace(',', '.').strip())
                        producto.stock = max(0, int(row['stock']))
                    else:
                        nuevo = Producto(
                            codigo=row['codigo'],
                            nombre=row['nombre'],
                            descripcion='',
                            familia=row['familia'],
                            talle=row['talle'],
                            color=row['color'],
                            proveedor=row['proveedor'],
                            precio_compra=float(str(row['precio_compra']).replace('$', '').replace('.', '').replace(',', '.').strip()),
                            precio_venta=float(str(row['precio_venta_contado']).replace('$', '').replace('.', '').replace(',', '.').strip()),
                            stock=max(0, int(row['stock']))
                        )
                        db.session.add(nuevo)

                db.session.commit()
                flash('Stock actualizado correctamente.')
            except Exception as e:
                flash(f'Error al procesar el archivo: {e}')
        else:
            flash('Formato de archivo no permitido.')
        return redirect(url_for('stock_routes.stock'))
    else:
        return render_template('stock.html')
