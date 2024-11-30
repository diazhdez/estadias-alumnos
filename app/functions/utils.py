from flask import session, redirect, url_for, flash, current_app
from functools import wraps

def requiere_permisos(permisos_requeridos, departamento_requerido=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            correo = session.get('correo')
            if not correo:
                flash("Acceso denegado: Debes iniciar sesión.", "danger")
                return redirect(url_for("session.logout"))

            # Conectar a la base de datos
            db = current_app.get_db_connection()

            # Verificar si el usuario es un alumno
            usuario = db["Alumnos"].find_one({"Correo_Institucional": correo})
            if usuario:
                # Verificar permisos del alumno
                permisos_usuario = usuario.get("permisos", [])
                if all(permiso in permisos_usuario for permiso in permisos_requeridos):
                    return f(*args, **kwargs)
                else:
                    flash("Acceso denegado: No tienes permisos suficientes.", "danger")
                    return redirect(url_for("main.index"))

            # Verificar si el usuario es un administrador
            admin = db["administradores"].find_one({"correo": correo})
            if admin:
                # Verificar permisos del administrador y su departamento
                permisos_admin = admin.get("permisos", [])
                departamento_admin = admin.get("departamento")
                
                if all(permiso in permisos_admin for permiso in permisos_requeridos) and (departamento_requerido is None or departamento_admin == departamento_requerido):
                    return f(*args, **kwargs)
                else:
                    flash("Acceso denegado: No tienes permisos suficientes o perteneces a un departamento no autorizado.", "danger")
                    return redirect(url_for("main.index"))

            flash("Acceso denegado: Usuario no autorizado.", "danger")
            return redirect(url_for("main.index"))

        return wrapped
    return decorator
