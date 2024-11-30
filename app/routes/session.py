from datetime import datetime
from flask import Blueprint, current_app, render_template, redirect, url_for, flash, session, request
from app.functions.funciones import nocache, obtener_administrador_por_correo, obtener_usuario_por_correo
import bcrypt

session_routes = Blueprint('session', __name__)


@session_routes.route('/iniciar/', methods=['POST'])
def iniciar():
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    if db is None:
        flash('No se pudo conectar a la base de datos.', 'danger')
        return redirect(url_for('session.logout'))
    
    correo = request.form['correo']
    password = request.form['password']
    alumno = db['Alumnos'] 
    administracion = db['administradores']

    # Verificar si es un alumno
    login_alumno = alumno.find_one({'Correo_Institucional': correo})
    if login_alumno:
        if login_alumno.get('en_linea'):
            flash('El usuario ya tiene una sesión activa.', 'warning')
            return redirect(url_for('main.index'))

        if bcrypt.checkpw(password.encode('utf-8'), login_alumno['Contraseña']):
            # Autenticación exitosa
            session['correo'] = correo
            alumno.update_one(
                {"Correo_Institucional": correo},
                {'$set': {'en_linea': True, 'ultima_conexion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}
            )
            flash('Inicio de sesión exitoso como alumno.', 'success')
            return redirect(url_for('alumno.alumno_vista'))
    
    # Buscar en la colección de Administradores
    login_departamentos = administracion.find_one({'correo': correo})

    if login_departamentos:
        if login_departamentos.get('en_linea'):
            flash('El usuario ya tiene una sesión activa.', 'warning')
            return redirect(url_for('main.index'))

    if login_departamentos and bcrypt.checkpw(password.encode('utf-8'), login_departamentos['contraseña']):
        departamento = login_departamentos['departamento']
        session['correo'] = correo
        administracion.update_one({"correo":correo}, 
            {'$set':{
                'en_linea': True, 'ultima_conexion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }})
        
        if departamento == 'vinculacion':
            flash('Bienvenido de vuelta.', 'success')
            return redirect(url_for('Vinculacion.Home'))
        elif departamento == 'servicios_escolares':
            flash('Bienvenido de vuelta.', 'success')
            return redirect(url_for('Servicios.Servicios'))
        elif departamento == 'finanzas':
            flash('Bienvenido de vuelta.', 'success')
            return redirect(url_for('Finanzas.Finanzas'))
        elif departamento == 'Root':
            flash('Bienvenido de vuelta.', 'success')
            return redirect(url_for('SuperAdmin.home'))
        elif departamento == 'recursos_materiales':
            flash('Bienvenido de vuelta.', 'success')
            return redirect(url_for('Recursos.Recursos'))
        elif departamento == 'biblioteca':
            flash('Bienvenido de vuelta.', 'success')
            return redirect(url_for('Biblioteca.Biblioteca'))
        elif departamento == 'juridico':
            flash('Bienvenido de vuelta.', 'success')
            return redirect(url_for('Juridico.Juridico'))
        else:
            flash('Departamento no reconocido.', 'danger')
            return redirect(url_for('main.index'))
    # Si el inicio de sesión falla, muestra un mensaje de error
    flash('Correo o contraseña incorrectos', 'danger')
    return redirect(url_for('main.index'))



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
    db = current_app.get_db_connection() 
    correo = session.get('correo')
    admin = db['administradores'].find_one({'correo': correo})
    if admin:
        administracion = db['administradores']
        administracion.update_one(
            {"correo": correo}, 
            {'$set': {'en_linea': False}}
        )
    session.clear()  # Elimina todas las variables de sesión
    flash('Sesion cerrada con exito', 'success')
    return redirect(url_for('main.index'))  # Redirige al inicio de sesión
