from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    perfil = db.Column(db.String(50), nullable=False, default="Vendedor")
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    familia = db.Column(db.String(100))
    talle = db.Column(db.String(20))
    color = db.Column(db.String(50))
    proveedor = db.Column(db.String(100)) 
    precio_compra = db.Column(db.Float)
    precio_venta = db.Column(db.Float)
    stock = db.Column(db.Integer)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(120))
    direccion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)  # ✅ CLIENTE ACTIVO/INACTIVO

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    total_original = db.Column(db.Float)
    total_cobrado = db.Column(db.Float)
    descuento_total = db.Column(db.Float)
    cliente = db.relationship('Cliente', backref=db.backref('ventas', lazy=True))

class DetalleVenta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    precio_cobrado = db.Column(db.Float, nullable=False)
    descuento_aplicado = db.Column(db.Float)
    venta = db.relationship('Venta', backref=db.backref('detalles', lazy=True))
    producto = db.relationship('Producto')

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    metodo = db.Column(db.String(50))
    concepto = db.Column(db.String(200))
    cliente = db.relationship('Cliente', backref=db.backref('pagos', lazy=True))

class Deuda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    saldo_pendiente = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default="pendiente")  # opciones: pendiente, parcial, saldada
    cliente = db.relationship('Cliente', backref=db.backref('deudas', lazy=True))
    venta = db.relationship('Venta', backref=db.backref('deuda', uselist=False))
