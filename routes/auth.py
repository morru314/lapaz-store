from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models.models import User
from flask_login import current_user  # ya que usás user logueado
from werkzeug.security import generate_password_hash



auth_routes = Blueprint('auth_routes', __name__, template_folder='../templates')

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(request.args.get('next') or url_for('dashboard_routes.dashboard'))
        flash('Credenciales inválidas')
    return render_template('login.html')

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_routes.login'))


@auth_routes.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        nueva_password = request.form['nueva_password']
        confirmar_password = request.form['confirmar_password']

        if not nueva_password or not confirmar_password:
            flash("Todos los campos son obligatorios.")
        elif nueva_password != confirmar_password:
            flash("Las contraseñas no coinciden.")
        else:
            current_user.set_password(nueva_password)
            from extensions import db
            db.session.commit()
            flash("Contraseña actualizada con éxito.")

    return render_template('perfil.html', user=current_user)

