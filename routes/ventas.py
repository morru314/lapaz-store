from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from supabase_client import supabase
import os
import uuid

ventas_routes = Blueprint('ventas_routes', __name__, template_folder='../templates')

# Decorador de sesión
from functools import wraps

def login_required_sb(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("sb_token"):
            return redirect(url_for("auth_routes.login"))
        return f(*args, **kwargs)
    return decorated_function


@ventas_routes.route('/ventas')
@login_required_sb
def ventas():
    productos = supabase.table("productos").select("*").execute().data
    clientes = supabase.table("clientes").select("*").eq("activo", True).execute().data
    return render_template('ventas.html', productos=productos, clientes=clientes)


@ventas_routes.route('/ventas/registrar', methods=['POST'])
@login_required_sb
def registrar_venta():
    data = request.json

    # Cliente
    cliente_id = data.get("cliente_id")
    if not cliente_id:
        cliente_data = {
            "id": str(uuid.uuid4()),
            "nombre": data["cliente_nombre"],
            "apellido": data["cliente_apellido"],
            "telefono": data.get("cliente_telefono", ""),
            "activo": True
        }
        cliente_insert = supabase.table("clientes").insert(cliente_data).execute()
        cliente_id = cliente_data["id"]

    # Venta
    venta_data = {
        "id": str(uuid.uuid4()),
        "cliente_id": cliente_id,
        "total_original": data["total_original"],
        "total_cobrado": data["total_cobrado"],
        "descuento_total": data.get("descuento_total", 0)
    }
    supabase.table("ventas").insert(venta_data).execute()

    # Detalles
    for item in data["items"]:
        producto = supabase.table("productos").select("*").eq("id", item["producto_id"]).single().execute().data
        if not producto:
            return jsonify({"error": f"Producto con ID {item['producto_id']} no encontrado"}), 404
        if producto["stock"] < item["cantidad"]:
            return jsonify({"error": f"Stock insuficiente para {producto['nombre']}"}), 400

        # Actualizar stock
        nuevo_stock = producto["stock"] - item["cantidad"]
        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", producto["id"]).execute()

        # Insertar detalle
        detalle = {
            "id": str(uuid.uuid4()),
            "venta_id": venta_data["id"],
            "producto_id": producto["id"],
            "cantidad": item["cantidad"],
            "precio_unitario": item["precio_unitario"],
            "precio_cobrado": item["precio_cobrado"],
            "descuento_aplicado": item.get("descuento_aplicado", 0)
        }
        supabase.table("detalle_ventas").insert(detalle).execute()

    # Deuda
    if venta_data["total_cobrado"] < venta_data["total_original"]:
        deuda = {
            "id": str(uuid.uuid4()),
            "cliente_id": cliente_id,
            "venta_id": venta_data["id"],
            "saldo_pendiente": venta_data["total_original"] - venta_data["total_cobrado"],
            "estado": "parcial" if venta_data["total_cobrado"] > 0 else "pendiente"
        }
        supabase.table("deudas").insert(deuda).execute()

    # Pago
    if venta_data["total_cobrado"] > 0:
        pago = {
            "id": str(uuid.uuid4()),
            "cliente_id": cliente_id,
            "monto": venta_data["total_cobrado"],
            "metodo": data.get("metodo_pago", "Transferencia"),
            "concepto": f"Pago de venta #{venta_data['id']}"
        }
        supabase.table("pagos").insert(pago).execute()

    return jsonify({"message": "Venta registrada correctamente."})


@ventas_routes.route('/ventas/buscar_producto')
@login_required_sb
def buscar_producto():
    q = request.args.get('q', '').strip().lower()
    productos = supabase.table("productos").select("*").execute().data
    filtrados = []
    for p in productos:
        texto = f"{p['nombre']} {p['color']} {p['talle']} {p['codigo']} {p['familia']}".lower()
        if all(pal in texto for pal in q.split()):
            filtrados.append(p)
    return jsonify(filtrados[:10])


@ventas_routes.route('/ventas/buscar_cliente')
@login_required_sb
def buscar_cliente():
    q = request.args.get('q', '').strip().lower()
    clientes = supabase.table("clientes").select("*").eq("activo", True).execute().data
    filtrados = []
    for c in clientes:
        texto = f"{c['nombre']} {c['apellido']} {c['telefono']}".lower()
        if q in texto:
            filtrados.append(c)
    return jsonify(filtrados[:10])
