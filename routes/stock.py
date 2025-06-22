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
                # Leer archivo
                df = pd.read_csv(ruta) if ruta.endswith('.csv') else pd.read_excel(ruta)


                # Normalizar columnas
                df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

                columnas_obligatorias = {
                    'codigo', 'nombre', 'familia', 'talle', 'color',
                    'proveedor', 'precio_compra', 'precio_venta_contado',
                    'precio_venta_tarjeta', 'stock'
                }

                if not columnas_obligatorias.issubset(df.columns):
                    faltantes = columnas_obligatorias - set(df.columns)
                    flash(f'Columnas faltantes en el archivo: {", ".join(faltantes)}')
                    return redirect(url_for('stock_routes.stock'))

                insertados = 0
                actualizados = 0

                for _, row in df.iterrows():
                    codigo = str(row['codigo']).strip()
                    existente = supabase.table("productos").select("*").eq("codigo", codigo).maybe_single().execute().data

                    def limpiar_precio(valor):
                        return float(str(valor).replace('$', '').replace('.', '').replace(',', '.').strip())

                    data = {
                        "codigo": codigo,
                        "nombre": row['nombre'].strip(),
                        "descripcion": '',
                        "familia": row['familia'].strip(),
                        "talle": row['talle'].strip(),
                        "color": row['color'].strip(),
                        "proveedor": row['proveedor'].strip(),
                        "precio_compra": limpiar_precio(row['precio_compra']),
                        "precio_venta": limpiar_precio(row['precio_venta_contado']),
                        "stock": max(0, int(row['stock']))
                    }

                    if existente:
                        supabase.table("productos").update(data).eq("codigo", codigo).execute()
                        actualizados += 1
                    else:
                        supabase.table("productos").insert(data).execute()
                        insertados += 1

                flash(f"✔️ Stock actualizado: {insertados} insertados, {actualizados} actualizados.")
            except Exception as e:
                flash(f"❌ Error procesando archivo: {str(e)}")
        else:
            flash('⚠️ Formato de archivo no permitido.')
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
