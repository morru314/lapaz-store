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

            if response and response.user:
                flash("Cuenta creada. Verificá tu correo.")
                return redirect(url_for('auth_routes.login'))
            else:
                flash("Error: No se pudo crear la cuenta.")

        except Exception as e:
            flash(f"Error: {str(e)}")

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
                user_metadata = result.user.user_metadata or {}
                session["sb_user"] = {
                "id": result.user.id,
                "email": result.user.email,
                "username": user_metadata.get("username", ""),
                "full_name": user_metadata.get("full_name", "")
}

                flash("Sesión iniciada.")
                return redirect(url_for('dashboard_routes.dashboard'))
            else:
                flash("Error de autenticación: credenciales inválidas.")

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

    user = session.get("sb_user")
    return render_template("perfil.html", user=user)

