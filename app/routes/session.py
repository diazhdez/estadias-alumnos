from flask import Blueprint, current_app, render_template, redirect, url_for, flash, session, request
from app.functions.funciones import nocache
import bcrypt

session_routes = Blueprint('session', __name__)


@session_routes.route('/EduLink/login/')
def login():
    return render_template('login.html')


@session_routes.route('/iniciar/', methods=['POST'])
def iniciar():
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    correo = request.form['correo']
    password = request.form['password']
    alumno = db['usuarios']

    login_alumno = alumno.find_one({'correoAlumno': correo})
    if login_alumno and bcrypt.checkpw(password.encode('utf-8'), login_alumno['contraseñaAlumno']):
        # Autenticación exitosa
        session['correo'] = correo
        flash('Inicio de sesión exitoso como alumno.', 'success')
        return redirect(url_for('alumno.alumno_vista'))

    # Si el inicio de sesión falla, muestra un mensaje de error
    flash('Correo o contraseña incorrectos', 'danger')
    return redirect(url_for('login'))


@session_routes.route('/logout')
@nocache
def logout():
    session.clear()  # Elimina todas las variables de sesión
    return redirect(url_for('main.index'))  # Redirige al inicio de sesión
