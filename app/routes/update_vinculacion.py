from flask import Blueprint, current_app, flash, redirect, session, url_for, request
from app.functions.funciones import aceptar_documento, actualizar_estado_documento, subir_documento
from bson import Binary, ObjectId

update_vinculacion_routes = Blueprint('update_vinculacion', __name__)


@update_vinculacion_routes.route('/aceptar_documento/<id_alumno>/<documento_nombre>', methods=['GET', 'POST'])
def aceptar_documento_nuevo(id_alumno, documento_nombre):
        db = current_app.get_db_connection()
        if aceptar_documento(id_alumno, documento_nombre):
            correo = session.get('correo')
            if correo:
                administracion = db['administradores']
                administracion.update_one(
                    {"correo": correo}, 
                    {'$set': {'ultimo_movimiento': 'Acepto un documento'}}
                )
            flash('Documento aceptado exitosamente.', 'success')
        else:
            flash('No se pudo aceptar el documento intentelo de nuevo.', 'danger')
        
        return redirect(url_for('Vinculacion.documento_alumnos', id_alumno=id_alumno))

@update_vinculacion_routes.route('/actualizar_estado_documento/<id_alumno>/<documento_nombre>', methods=['GET', 'POST'])
def actualizar_estado_documento_nuevo(id_alumno, documento_nombre):
        db = current_app.get_db_connection()
        if actualizar_estado_documento(id_alumno, documento_nombre):
            correo = session.get('correo')
            if correo:
                administracion = db['administradores']
                administracion.update_one(
                    {"correo": correo}, 
                    {'$set': {'ultimo_movimiento': 'Activo un documento de estadia'}}
                )
            flash('Estado del documento actualizado exitosamente.', 'success')
        else:
            flash('No se pudo actualizar el estado del documento.', 'danger')
        
        return redirect(url_for('Vinculacion.documento_alumnos', id_alumno=id_alumno))
