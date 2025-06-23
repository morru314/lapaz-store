from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from supabase_client import supabase
import pandas as pd
import os
from config import Config
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
    valor_stock_venta = sum(p["stock"] * p["precio_venta_contado"] for p in productos)

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

@stock_routes.route('/stock/editar/<uuid:id>', methods=['GET', 'POST'], endpoint='editar_producto')
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
            "precio_venta_contado": float(request.form['precio_venta_contado']),
            "precio_venta_tarjeta": float(request.form['precio_venta_tarjeta']),
            "stock": max(0, int(request.form['stock']))
        }).eq("id", id).execute()

        flash("Producto actualizado correctamente.")
        return redirect(url_for('stock_routes.stock'))

    producto = supabase.table("productos").select("*").eq("id", id).maybe_single().execute().data
    return render_template('editar_producto.html', producto=producto)

@stock_routes.route('/stock/eliminar/<uuid:id>', methods=['POST'])
@login_required_sb
def eliminar_producto(id):
    supabase.table("productos").delete().eq("id", id).execute()
    flash("Producto eliminado correctamente.")
    return redirect(url_for('stock_routes.stock'))

@stock_routes.route('/stock/cargar', methods=['GET', 'POST'])
@login_required_sb
def cargar_stock():
    try:
        if request.method != 'POST':
            return render_template('stock.html')

        archivo = request.files.get('archivo')
        if not archivo or not archivo.filename.lower().endswith(('.csv', '.xlsx')):
            flash('⚠️ Formato de archivo no permitido.')
            return redirect(url_for('stock_routes.stock'))

        ruta = os.path.join(Config.UPLOAD_FOLDER, archivo.filename)
        archivo.save(ruta)

        # Leer el CSV con encoding adecuado
        try:
            df = pd.read_csv(ruta, sep=';', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(ruta, sep=';', encoding='latin-1')

        # Limpiar nombres de columnas
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

        # Reemplazar None y NaN con valores apropiados
        df = df.fillna('')

        columnas_obligatorias = {
            'codigo', 'nombre', 'familia', 'talle', 'color',
            'proveedor', 'precio_compra',
            'precio_venta_contado', 'precio_venta_tarjeta', 'stock'
        }
        faltantes = columnas_obligatorias - set(df.columns)
        if faltantes:
            flash(f'Columnas faltantes: {", ".join(sorted(faltantes))}')
            return redirect(url_for('stock_routes.stock'))

        def limpiar_precio(v):
            try:
                if pd.isna(v) or not str(v).strip():
                    return 0.0
                valor_str = str(v).replace('$', '').replace('.', '').replace(',', '.').strip()
                return float(valor_str) if valor_str else 0.0
            except (ValueError, TypeError):
                return 0.0

        def limpiar_texto(val):
            if pd.isna(val):
                return None
            val = str(val).strip()
            return val if val and val.lower() != 'none' else None

        def limpiar_stock(val):
            try:
                if pd.isna(val):
                    return 0
                val_str = str(val).strip()
                return int(float(val_str)) if val_str else 0
            except (ValueError, TypeError):
                return 0

        insertados = actualizados = 0
        errores = []

        # Procesar en lotes más pequeños para evitar timeouts
        batch_size = 50
        total_rows = len(df)

        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]

            for idx, row in batch.iterrows():
                try:
                    codigo = limpiar_texto(row['codigo'])
                    if not codigo:
                        raise ValueError("Código vacío o inválido")

                    data = {
                        "codigo": codigo,
                        "nombre": limpiar_texto(row['nombre']) or 'Sin nombre',
                        "descripcion": limpiar_texto(row.get('descripcion', '')),
                        "familia": limpiar_texto(row['familia']) or 'Sin categoría',
                        "talle": limpiar_texto(row['talle']) or 'Único',
                        "color": limpiar_texto(row['color']) or 'Sin especificar',
                        "proveedor": limpiar_texto(row['proveedor']) or 'Sin especificar',
                        "precio_compra": limpiar_precio(row['precio_compra']),
                        "precio_venta_contado": limpiar_precio(row['precio_venta_contado']),
                        "precio_venta_tarjeta": limpiar_precio(row['precio_venta_tarjeta']),
                        "stock": limpiar_stock(row['stock'])
                    }

                    # Consultar si existe el producto - con mejor manejo de errores
                    try:
                        response = supabase.table("productos").select("id").eq("codigo", codigo).execute()
                        existe = response.data and len(response.data) > 0
                    except Exception as query_error:
                        print(f"Error consultando producto {codigo}: {query_error}")
                        existe = False

                    # Insertar o actualizar
                    try:
                        if existe:
                            response = supabase.table("productos").update(data).eq("codigo", codigo).execute()
                            if response.data:
                                actualizados += 1
                            else:
                                raise Exception("Update no devolvió datos")
                        else:
                            response = supabase.table("productos").insert(data).execute()
                            if response.data:
                                insertados += 1
                            else:
                                raise Exception("Insert no devolvió datos")

                    except Exception as db_error:
                        print(f"Error DB para {codigo}: {db_error}")
                        errores.append({
                            "codigo": codigo,
                            "error": f"Error base de datos: {str(db_error)}"
                        })

                except Exception as fila_exc:
                    codigo_error = str(row.get('codigo', f'Fila {idx}'))
                    print(f"Error procesando fila {codigo_error}: {fila_exc}")
                    errores.append({
                        "codigo": codigo_error,
                        "error": str(fila_exc)
                    })

        # Guardar errores en la tabla de errores
        if errores:
            try:
                # Insertar errores en lotes
                errores_data = []
                for err in errores:
                    errores_data.append({
                        "codigo": err["codigo"][:50],  # Limitar longitud
                        "detalle_error": err["error"][:500]  # Limitar longitud
                    })

                # Insertar en lotes de 20
                for i in range(0, len(errores_data), 20):
                    batch_errores = errores_data[i:i+20]
                    supabase.table("errores_stock").insert(batch_errores).execute()

            except Exception as error_insert:
                print(f"Error guardando log de errores: {error_insert}")

        # Limpiar archivo temporal
        try:
            os.remove(ruta)
        except:
            pass

        # Mensaje final
        if errores:
            flash(f"⚠️ Proceso completado con errores: {insertados} insertados, {actualizados} actualizados, {len(errores)} fallidos. Revisa la tabla de errores.")
        else:
            flash(f"✔️ Stock actualizado exitosamente: {insertados} insertados, {actualizados} actualizados.")

        return redirect(url_for('stock_routes.stock'))

    except Exception as e:
        # Limpiar archivo si existe
        try:
            if 'ruta' in locals():
                os.remove(ruta)
        except:
            pass

        tb = traceback.format_exc()
        print(f"Error general en cargar_stock: {tb}")

        return (
            f"<h1>ERROR al procesar stock</h1>"
            f"<pre>{tb}</pre>",
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
