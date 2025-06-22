from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from supabase_client import supabase
import pandas as pd
import os
from config import Config
from functools import wraps
from utils.auth_helpers import login_required_sb
import traceback

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


import traceback

@stock_routes.route('/stock/cargar', methods=['GET', 'POST'])
@login_required_sb
def cargar_stock():
    try:
        # — Si viene GET, mostramos la página —
        if request.method != 'POST':
            return render_template('stock.html')

        # — Validación inicial del archivo —
        archivo = request.files.get('archivo')
        if not archivo or not archivo.filename.lower().endswith(('.csv', '.xlsx')):
            flash('⚠️ Formato de archivo no permitido.')
            return redirect(url_for('stock_routes.stock'))

        # — Guardar el archivo en servidor —
        ruta = os.path.join(Config.UPLOAD_FOLDER, archivo.filename)
        archivo.save(ruta)

        # — Leer CSV con separador ";" —
        df = pd.read_csv(ruta, sep=';')
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

        # — Verificar columnas obligatorias —
        columnas_obligatorias = {
            'codigo', 'nombre', 'familia', 'talle', 'color',
            'proveedor', 'precio_compra',
            'precio_venta_contado', 'precio_venta_tarjeta', 'stock'
        }
        faltantes = columnas_obligatorias - set(df.columns)
        if faltantes:
            flash(f'Columnas faltantes en el archivo: {", ".join(sorted(faltantes))}')
            return redirect(url_for('stock_routes.stock'))

        # — Preparar contadores y lista de errores —
        insertados = actualizados = 0
        errores = []

        def limpiar_precio(v):
            return float(str(v).replace('$', '').replace('.', '').replace(',', '.').strip())

        # — Procesar cada fila —
        for _, row in df.iterrows():
            try:
                data = {
                    "codigo": str(row['codigo']).strip(),
                    "nombre": str(row['nombre']).strip(),
                    "descripcion": '',
                    "familia": str(row['familia']).strip(),
                    "talle": str(row['talle']).strip(),
                    "color": str(row['color']).strip(),
                    "proveedor": str(row['proveedor']).strip(),
                    "precio_compra": limpiar_precio(row['precio_compra']),
                    "precio_venta_contado": limpiar_precio(row['precio_venta_contado']),
                    "precio_venta_tarjeta": limpiar_precio(row['precio_venta_tarjeta']),
                    "stock": max(0, int(row['stock']))
                }

                # — Chequear existencia por código —
                existe = supabase.table("productos") \
                                 .select("id") \
                                 .eq("codigo", data["codigo"]) \
                                 .maybe_single() \
                                 .execute().data

                if existe:
                    supabase.table("productos").update(data).eq("codigo", data["codigo"]).execute()
                    actualizados += 1
                else:
                    supabase.table("productos").insert(data).execute()
                    insertados += 1

            except Exception as fila_exc:
                errores.append({
                    "codigo": row.get('codigo', ''),
                    "error": str(fila_exc)
                })

        # — Registrar errores en Supabase (si hay) —
        if errores:
            for err in errores:
                supabase.table("errores_stock").insert({
                    "codigo": err["codigo"],
                    "detalle_error": err["error"]
                }).execute()
            flash(f"⚠️ Terminó con errores: {insertados} insertados, {actualizados} actualizados, {len(errores)} fallidos.")
        else:
            flash(f"✔️ Stock actualizado: {insertados} insertados, {actualizados} actualizados.")

        return redirect(url_for('stock_routes.stock'))

    except Exception as e:
        tb = traceback.format_exc()
        return (
            "<h1>ERROR al procesar stock</h1>"
            "<pre style='white-space: pre-wrap; background:#222; color:#eee; padding:1em;'>"
            f"{tb}"
            "</pre>",
            500
        )

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
