from flask import session, redirect, url_for, flash
from .funciones import obtener_usuario_por_correo 
from functools import wraps

def requiere_permiso(permisos_requeridos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            correo = session.get('correo')
            if not correo:
                flash('Inicia sesión para continuar', 'danger')
                return redirect(url_for('session.logout'))
                
            alumno = obtener_usuario_por_correo(correo)
            if alumno:
                permisos_usuario = alumno.get("permisos", [])
                # Verifica si el usuario tiene al menos uno de los permisos requeridos
                if any(permiso in permisos_usuario for permiso in permisos_requeridos):
                    return f(*args, **kwargs)
                else:
                    flash('No tienes permisos para acceder a esta página.', 'danger')
                    return redirect(url_for('session.logout'))
            else:
                flash('Alumno no encontrado.', 'danger')
                return redirect(url_for('session.logout'))
        return decorated_function
    return decorator
