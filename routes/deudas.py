from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from supabase_client import supabase
import os
import uuid
from datetime import datetime
from utils.auth_helpers import login_required_sb
from postgrest import ASC as asc

# Blueprint

deudas_routes = Blueprint('deudas_routes', __name__, template_folder='../templates')


@deudas_routes.route('/deudas')
@login_required_sb
def deudas():
    clientes = supabase.table("clientes").select("*").eq("activo", True).execute().data
    deudas = supabase.table("deudas").select("*").execute().data
    return render_template('deudas.html', clientes=clientes, deudas=deudas)


@deudas_routes.route('/deudas/cliente/<uuid:cliente_id>')
@login_required_sb
def deudas_por_cliente(cliente_id):
    cliente_id = str(cliente_id)  # si lo necesitás como string
    cliente = supabase.table("clientes").select("*").eq("id", cliente_id).single().execute().data
    deudas = supabase.table("deudas").select("*").eq("cliente_id", cliente_id).execute().data
    pagos = supabase.table("pagos").select("*").eq("cliente_id", cliente_id).order("fecha", desc=True).execute().data
    return render_template('deudas_cliente.html', cliente=cliente, deudas=deudas, pagos=pagos)


@deudas_routes.route('/deudas/pagar', methods=['POST'])
@login_required_sb
def pagar_deuda():
    cliente_id = request.form['cliente_id']
    monto_pago = float(request.form['monto'])
    metodo = request.form['metodo']
    concepto = request.form.get('concepto', '')

    deudas = supabase.table("deudas").select("*")\
        .eq("cliente_id", cliente_id)\
        .not_('saldo_pendiente', 'is', None)\
        .order("id", asc=True).execute().data

    saldo_restante = monto_pago
    updates = []

    for deuda in deudas:
        if saldo_restante <= 0:
            break
        aplicado = min(saldo_restante, deuda["saldo_pendiente"])
        nuevo_saldo = deuda["saldo_pendiente"] - aplicado
        nuevo_estado = "saldada" if nuevo_saldo <= 0 else "parcial"

        supabase.table("deudas").update({
            "saldo_pendiente": nuevo_saldo,
            "estado": nuevo_estado
        }).eq("id", deuda["id"]).execute()

        saldo_restante -= aplicado

    pago = {
        "id": str(uuid.uuid4()),
        "cliente_id": cliente_id,
        "monto": monto_pago,
        "metodo": metodo,
        "concepto": concepto,
        "fecha": datetime.utcnow().isoformat()
    }
    supabase.table("pagos").insert(pago).execute()

    flash("Pago registrado y aplicado correctamente.")
    return redirect(url_for('deudas_routes.deudas_por_cliente', cliente_id=cliente_id))
