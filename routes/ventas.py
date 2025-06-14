from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import db
from models.models import Cliente, Producto, Venta, DetalleVenta, Deuda, Pago

ventas_routes = Blueprint('ventas_routes', __name__, template_folder='../templates')

@ventas_routes.route('/ventas')
def ventas():
    productos = Producto.query.all()
    clientes = Cliente.query.all()
    return render_template('ventas.html', productos=productos, clientes=clientes)

@ventas_routes.route('/ventas/registrar', methods=['POST'])
def registrar_venta():
    data = request.json

    # Cliente
    cliente_id = data.get("cliente_id")
    if not cliente_id:
        cliente = Cliente(
            nombre=data["cliente_nombre"],
            apellido=data["cliente_apellido"],
            telefono=data.get("cliente_telefono", "")
        )
        db.session.add(cliente)
        db.session.flush()
        cliente_id = cliente.id

    # Crear venta
    venta = Venta(
        cliente_id=cliente_id,
        total_original=data["total_original"],
        total_cobrado=data["total_cobrado"],
        descuento_total=data.get("descuento_total", 0)
    )
    db.session.add(venta)
    db.session.flush()

    # Detalles
    for item in data["items"]:
        producto = Producto.query.get(item["producto_id"])
        if not producto or producto.stock < item["cantidad"]:
            return jsonify({"error": f"Stock insuficiente para {producto.nombre}"}), 400

        producto.stock -= item["cantidad"]

        detalle = DetalleVenta(
            venta_id=venta.id,
            producto_id=producto.id,
            cantidad=item["cantidad"],
            precio_unitario=item["precio_unitario"],
            precio_cobrado=item["precio_cobrado"],
            descuento_aplicado=item.get("descuento_aplicado", 0)
        )
        db.session.add(detalle)

    # Registrar deuda si corresponde
    if venta.total_cobrado < venta.total_original:
        deuda = Deuda(
            cliente_id=cliente_id,
            venta_id=venta.id,
            saldo_pendiente=venta.total_original - venta.total_cobrado,
            estado="parcial" if venta.total_cobrado > 0 else "pendiente"
        )
        db.session.add(deuda)

    # Registrar pago si se cobró algo
    metodo_pago = data.get("metodo_pago", "Transferencia")

    if venta.total_cobrado > 0:
        pago = Pago(
            cliente_id=cliente_id,
            monto=venta.total_cobrado,
            metodo=metodo_pago,
            concepto=f"Pago de venta #{venta.id}"
        )
        db.session.add(pago)

    db.session.commit()
    return jsonify({"message": "Venta registrada correctamente."})
@ventas_routes.route('/ventas/buscar_producto')
def buscar_producto():
    q = request.args.get('q', '').strip().lower()
    palabras = q.split()

    query = Producto.query

    for palabra in palabras:
        ilike = f"%{palabra}%"
        query = query.filter(
            (Producto.nombre.ilike(ilike)) |
            (Producto.color.ilike(ilike)) |
            (Producto.talle.ilike(ilike)) |
            (Producto.codigo.ilike(ilike)) |
            (Producto.familia.ilike(ilike)) 
        )

    productos = query.limit(10).all()

    return jsonify([
        {
            "id": p.id,
            "nombre": p.nombre,
            "codigo": p.codigo,
            "precio_venta": p.precio_venta,
            "talle": p.talle,
            "color": p.color,
            "stock": p.stock,
            "familia": p.familia
        } for p in productos
    ])


@ventas_routes.route('/ventas/buscar_cliente')
def buscar_cliente():
    q = request.args.get('q', '').lower()
    clientes = Cliente.query.filter(
        (Cliente.nombre.ilike(f"%{q}%")) |
        (Cliente.apellido.ilike(f"%{q}%")) |
        (Cliente.telefono.ilike(f"%{q}%"))
    ).all()
    return jsonify([{
        "id": c.id,
        "nombre": c.nombre,
        "apellido": c.apellido,
        "telefono": c.telefono
    } for c in clientes])


