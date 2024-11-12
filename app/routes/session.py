from flask import Blueprint, current_app, render_template, redirect, url_for, flash, session, request
from app.functions.funciones import nocache, obtener_administrador_por_correo, obtener_usuario_por_correo
import bcrypt

session_routes = Blueprint('session', __name__)


@session_routes.route('/iniciar/', methods=['POST'])
def iniciar():
    session.clear()
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    correo = request.form['correo']
    password = request.form['password']
    alumno = db['Alumnos']
    administracion = db['administradores']

    login_alumno = alumno.find_one({'Correo_Institucional': correo})
    if login_alumno and bcrypt.checkpw(password.encode('utf-8'), login_alumno['Contraseña']):
        # Autenticación exitosa
        session['correo'] = correo
        flash('Inicio de sesión exitoso como alumno.', 'success')
        return redirect(url_for('alumno.alumno_vista'))
    
    # Buscar en la colección de Administradores
    login_departamentos = administracion.find_one({'correo': correo})
    if login_departamentos and bcrypt.checkpw(password.encode('utf-8'), login_departamentos['contraseña']):
        departamento = login_departamentos['departamento']
        session['correo'] = correo
        
        if departamento == 'vinculacion':
            return redirect(url_for('Vinculacion.Home'))
        elif departamento == 'servicios_escolares':
            return redirect(url_for('Servicios.Servicios'))
        elif departamento == 'finanzas':
            return redirect(url_for('Finanzas.Finanzas'))
        elif departamento == 'Root':
            return redirect(url_for('SuperAdmin.home'))
        else:
            flash('Departamento no reconocido.', 'danger')
            return redirect(url_for('main.index'))

    # Si el inicio de sesión falla, muestra un mensaje de error
    flash('Correo o contraseña incorrectos', 'danger')
    return redirect(url_for('session.logout'))


@session_routes.route('/base_alumno')
def vista_alumno():
    correo = session.get('correo')
    alumno = obtener_usuario_por_correo(correo)
    return render_template('base_alumnos.html', alumno=alumno)
    
@session_routes.route('/base')
def vista_administracion():
    correo = session.get('correo')
    admin = obtener_administrador_por_correo(correo)
    return render_template('base.html', administrador=admin)

@session_routes.route('/logout')
@nocache
def logout():
    session.clear()  # Elimina todas las variables de sesión
    return redirect(url_for('main.index'))  # Redirige al inicio de sesión
