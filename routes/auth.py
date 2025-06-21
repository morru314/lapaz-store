from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from supabase_client import supabase

auth_routes = Blueprint('auth_routes', __name__, template_folder='../templates')


@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            if response.user:
                flash("Cuenta creada. Verificá tu correo.")
                return redirect(url_for('auth_routes.login'))

        except Exception as e:
            flash("Error: " + str(e))

    return render_template('register.html')


@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if result.session:
                session["sb_token"] = result.session.access_token
                session["sb_user"] = result.user.email
                flash("Sesión iniciada.")
                return redirect(url_for('dashboard_routes.dashboard'))

        except Exception as e:
            flash("Error de autenticación: " + str(e))

    return render_template('login.html')


@auth_routes.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada.")
    return redirect(url_for('auth_routes.login'))


@auth_routes.route('/perfil')
def perfil():
    if not session.get("sb_user"):
        return redirect(url_for("auth_routes.login"))

    email = session["sb_user"]
    return render_template("perfil.html", email=email)
