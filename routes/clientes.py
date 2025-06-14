from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import db
from models.models import Cliente

clientes_routes = Blueprint('clientes_routes', __name__, template_folder='../templates')

from models.models import Cliente, Venta, Deuda  # ya lo usás

@clientes_routes.route('/clientes')
def clientes():
    clientes = Cliente.query.filter_by(activo=True).all()
    clientes_data = []
    for c in clientes:
        total_compras = sum(v.total_original for v in c.ventas)
        total_deuda = sum(d.saldo_pendiente for d in c.deudas if d.estado != "saldada")
        clientes_data.append({
            "cliente": c,
            "compras": total_compras,
            "deuda": total_deuda
        })
    return render_template('clientes.html', clientes_data=clientes_data)

@clientes_routes.route('/clientes/nuevo', methods=['POST'])
def nuevo_cliente():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    email = request.form['email']
    direccion = request.form['direccion']

    existing = Cliente.query.filter_by(telefono=telefono).first()
    if existing:
        flash("Ya existe un cliente con ese número de teléfono.")
        return redirect(url_for('clientes_routes.clientes'))

    nuevo = Cliente(nombre=nombre, apellido=apellido, telefono=telefono, email=email, direccion=direccion)
    db.session.add(nuevo)
    db.session.commit()
    flash("Cliente agregado correctamente.")
    return redirect(url_for('clientes_routes.clientes'))
@clientes_routes.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])

def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.apellido = request.form['apellido']
        cliente.telefono = request.form['telefono']
        cliente.email = request.form['email']
        cliente.direccion = request.form['direccion']
        db.session.commit()
        flash("Cliente actualizado correctamente.")
        return redirect(url_for('clientes_routes.clientes'))
    return render_template('clientes.html', cliente_editar=cliente, editar=True)

@clientes_routes.route('/clientes/eliminar/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)

    if not cliente.activo:
        flash("El cliente ya está inactivo.")
        return redirect(url_for('clientes_routes.clientes'))

    cliente.activo = False  # 👈 MARCAR COMO INACTIVO
    db.session.commit()
    flash("Cliente marcado como inactivo.")
    return redirect(url_for('clientes_routes.clientes'))

@clientes_routes.route('/clientes/buscar')
def buscar_cliente():
    q = request.args.get('q', '').lower()
    resultados = Cliente.query.filter(
        (Cliente.nombre.ilike(f"%{q}%")) | (Cliente.apellido.ilike(f"%{q}%")) | (Cliente.telefono.ilike(f"%{q}%"))
    ).limit(10).all()
    return jsonify([{"id": c.id, "nombre": c.nombre, "apellido": c.apellido, "telefono": c.telefono} for c in resultados])
