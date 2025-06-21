from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models.models import Deuda, Cliente, Pago
from datetime import datetime

deudas_routes = Blueprint('deudas_routes', __name__, template_folder='../templates')

# Decorador para validar login con Supabase
from functools import wraps

def login_required_sb(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("sb_token"):
            return redirect(url_for("auth_routes.login"))
        return f(*args, **kwargs)
    return decorated_function


@deudas_routes.route('/deudas')
@login_required_sb
def deudas():
    clientes = Cliente.query.all()
    deudas = Deuda.query.all()
    return render_template('deudas.html', clientes=clientes, deudas=deudas)


@deudas_routes.route('/deudas/cliente/<int:cliente_id>')
@login_required_sb
def deudas_por_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    deudas = Deuda.query.filter_by(cliente_id=cliente_id).all()
    pagos = Pago.query.filter_by(cliente_id=cliente_id).order_by(Pago.fecha.desc()).all()
    return render_template('deudas_cliente.html', cliente=cliente, deudas=deudas, pagos=pagos)


@deudas_routes.route('/deudas/pagar', methods=['POST'])
@login_required_sb
def pagar_deuda():
    cliente_id = int(request.form['cliente_id'])
    monto_pago = float(request.form['monto'])
    metodo = request.form['metodo']
    concepto = request.form.get('concepto', '')

    deudas = Deuda.query.filter_by(cliente_id=cliente_id)\
        .filter(Deuda.saldo_pendiente > 0)\
        .order_by(Deuda.id.asc()).all()

    saldo_restante = monto_pago

    for deuda in deudas:
        if saldo_restante <= 0:
            break
        aplicado = min(saldo_restante, deuda.saldo_pendiente)
        deuda.saldo_pendiente -= aplicado
        deuda.estado = "saldada" if deuda.saldo_pendiente <= 0 else "parcial"
        saldo_restante -= aplicado

    pago = Pago(
        cliente_id=cliente_id,
        monto=monto_pago,
        metodo=metodo,
        concepto=concepto,
        fecha=datetime.utcnow()
    )
    db.session.add(pago)
    db.session.commit()

    flash("Pago registrado y aplicado correctamente.")
    return redirect(url_for('deudas_routes.deudas_por_cliente', cliente_id=cliente_id))
