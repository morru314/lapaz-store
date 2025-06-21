from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from supabase_client import supabase
from functools import wraps
from utils.auth_helpers import login_required_sb


clientes_routes = Blueprint('clientes_routes', __name__, template_folder='../templates')


@clientes_routes.route('/clientes')
@login_required_sb
def clientes():
    res = supabase.table("clientes").select("*").eq("activo", True).execute()
    clientes = res.data

    # Extra: calcular totales desde otra tabla
    ventas = supabase.table("ventas").select("*").execute().data
    deudas = supabase.table("deudas").select("*").execute().data

    clientes_data = []
    for c in clientes:
        total_compras = sum(v["total_original"] for v in ventas if v["cliente_id"] == c["id"])
        total_deuda = sum(d["saldo_pendiente"] for d in deudas if d["cliente_id"] == c["id"] and d["estado"] != "saldada")
        clientes_data.append({
            "cliente": c,
            "compras": total_compras,
            "deuda": total_deuda
        })

    return render_template('clientes.html', clientes_data=clientes_data)


@clientes_routes.route('/clientes/nuevo', methods=['POST'])
@login_required_sb
def nuevo_cliente():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    email = request.form['email']
    direccion = request.form['direccion']

    # Ver si ya existe
    existing = supabase.table("clientes").select("*").eq("telefono", telefono).maybe_single().execute().data
    if existing:
        flash("Ya existe un cliente con ese número de teléfono.")
        return redirect(url_for('clientes_routes.clientes'))

    supabase.table("clientes").insert({
        "nombre": nombre,
        "apellido": apellido,
        "telefono": telefono,
        "email": email,
        "direccion": direccion,
        "activo": True
    }).execute()

    flash("Cliente agregado correctamente.")
    return redirect(url_for('clientes_routes.clientes'))


@clientes_routes.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required_sb
def editar_cliente(id):
    if request.method == 'POST':
        supabase.table("clientes").update({
            "nombre": request.form['nombre'],
            "apellido": request.form['apellido'],
            "telefono": request.form['telefono'],
            "email": request.form['email'],
            "direccion": request.form['direccion']
        }).eq("id", id).execute()

        flash("Cliente actualizado correctamente.")
        return redirect(url_for('clientes_routes.clientes'))

    cliente = supabase.table("clientes").select("*").eq("id", id).maybe_single().execute().data
    return render_template('clientes.html', cliente_editar=cliente, editar=True)


@clientes_routes.route('/clientes/eliminar/<int:id>', methods=['POST'])
@login_required_sb
def eliminar_cliente(id):
    cliente = supabase.table("clientes").select("activo").eq("id", id).maybe_single().execute().data
    if not cliente or not cliente.get("activo"):
        flash("El cliente ya está inactivo.")
        return redirect(url_for('clientes_routes.clientes'))

    supabase.table("clientes").update({"activo": False}).eq("id", id).execute()
    flash("Cliente marcado como inactivo.")
    return redirect(url_for('clientes_routes.clientes'))


@clientes_routes.route('/clientes/buscar')
@login_required_sb
def buscar_cliente():
    q = request.args.get('q', '').lower()
    resultados = supabase.table("clientes").select("*").execute().data

    filtrados = [c for c in resultados if q in c["nombre"].lower() or q in c["apellido"].lower() or q in c["telefono"].lower()]
    return jsonify([{
        "id": c["id"],
        "nombre": c["nombre"],
        "apellido": c["apellido"],
        "telefono": c["telefono"]
    } for c in filtrados])
