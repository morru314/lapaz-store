from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from supabase_client import supabase
import pandas as pd
import os
from config import Config
from functools import wraps
from utils.auth_helpers import login_required_sb

stock_routes = Blueprint('stock_routes', __name__, template_folder='../templates')

@stock_routes.route('/stock')
@login_required_sb
def stock():
    productos = supabase.table("productos").select("*").execute().data
    total_productos = len(productos)
    total_stock = sum(p["stock"] for p in productos)
    valor_stock_compra = sum(p["stock"] * p["precio_compra"] for p in productos)
    valor_stock_venta = sum(p["stock"] * p["precio_venta"] for p in productos)

    detalles = supabase.table("detalle_venta").select("*").execute().data
    facturacion = sum(d["precio_cobrado"] * d["cantidad"] for d in detalles)

    return render_template(
        'stock.html',
        productos=productos,
        total_productos=total_productos,
        total_stock=total_stock,
        valor_stock_compra=valor_stock_compra,
        valor_stock_venta=valor_stock_venta,
        facturacion=facturacion
    )


@stock_routes.route('/stock/editar/<int:id>', methods=['GET', 'POST'], endpoint='editar_producto')
@login_required_sb
def editar_producto(id):
    if request.method == 'POST':
        supabase.table("productos").update({
            "nombre": request.form['nombre'],
            "descripcion": request.form['descripcion'],
            "familia": request.form['familia'],
            "talle": request.form['talle'],
            "color": request.form['color'],
            "proveedor": request.form['proveedor'],
            "precio_compra": float(request.form['precio_compra']),
            "precio_venta": float(request.form['precio_venta']),
            "stock": max(0, int(request.form['stock']))
        }).eq("id", id).execute()

        flash("Producto actualizado correctamente.")
        return redirect(url_for('stock_routes.stock'))

    producto = supabase.table("productos").select("*").eq("id", id).maybe_single().execute().data
    return render_template('editar_producto.html', producto=producto)


@stock_routes.route('/stock/eliminar/<int:id>', methods=['POST'])
@login_required_sb
def eliminar_producto(id):
    supabase.table("productos").delete().eq("id", id).execute()
    flash("Producto eliminado correctamente.")
    return redirect(url_for('stock_routes.stock'))


@stock_routes.route('/stock/cargar', methods=['GET', 'POST'])
@login_required_sb
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
                    codigo = row['codigo']
                    existente = supabase.table("productos").select("*").eq("codigo", codigo).maybe_single().execute().data
                    data = {
                        "codigo": codigo,
                        "nombre": row['nombre'],
                        "descripcion": '',
                        "familia": row['familia'],
                        "talle": row['talle'],
                        "color": row['color'],
                        "proveedor": row['proveedor'],
                        "precio_compra": float(str(row['precio_compra']).replace('$', '').replace('.', '').replace(',', '.').strip()),
                        "precio_venta": float(str(row['precio_venta_contado']).replace('$', '').replace('.', '').replace(',', '.').strip()),
                        "stock": max(0, int(row['stock']))
                    }
                    if existente:
                        supabase.table("productos").update(data).eq("codigo", codigo).execute()
                    else:
                        supabase.table("productos").insert(data).execute()

                flash("Stock actualizado correctamente.")
            except Exception as e:
                flash(f"Error al procesar el archivo: {e}")
        else:
            flash('Formato de archivo no permitido.')
        return redirect(url_for('stock_routes.stock'))

    return render_template('stock.html')


@stock_routes.route('/stock/upload_imagen', methods=['POST'])
@login_required_sb
def subir_imagen_producto():
    archivo = request.files['imagen']
    nombre = archivo.filename
    ruta_bucket = f"productos/{nombre}"

    try:
        supabase.storage.from_("productos").upload(ruta_bucket, archivo)
        flash("Imagen subida correctamente a Supabase Storage.")
    except Exception as e:
        flash(f"Error al subir la imagen: {e}")

    return redirect(url_for('stock_routes.stock'))
