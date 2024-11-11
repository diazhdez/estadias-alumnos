from flask import Blueprint, current_app, flash, redirect, session, url_for, request
from app.functions.funciones import aceptar_documento, actualizar_estado_documento, devolver_documento, subir_documento, estado_actividad
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


@update_vinculacion_routes.route('/Catalago_De_Empresas/upload/', methods=['POST'])
def upload_file():
        db = current_app.get_db_connection()
        conexion = db["archivos_vinculacion"]
        archivo = request.files['archivo']
        descripcion = request.form["descripcion"]

        if archivo:
            if archivo.filename.endswith('.pdf') or archivo.filename.endswith('.doc') or archivo.filename.endswith('.docx') or archivo.filename.endswith('.xlsx') or archivo.filename.endswith('.xls'):
                archivo_data = archivo.read()
                archivo_nombre = archivo.filename  # Guarda el nombre del archivo
                archivo_bin = Binary(archivo_data)  # Almacena el contenido del archivo como datos binarios en la base de datos
            else:
                flash('El archivo debe ser .pdf, .doc, .docx, .xlsx, .xls','warning')
                return redirect(url_for('registerColaborador'))
        else:
            archivo_nombre = None
            archivo_bin = None
 
        conexion.insert_one({
            'nombre': archivo_nombre,  # Guarda el nombre del archivo en la base de datos
            'archivo': archivo_bin,
            'descripcion': descripcion,
        })
        flash('Archivo guardado exitosamento','success')
        return redirect(url_for('Vinculacion.archivos_vinculacion'))

@update_vinculacion_routes.route('/devolver_Documento/', methods=['POST'])
def devolver_documento_alumno():
        db = current_app.get_db_connection()
        id_alumno = request.form.get('id_alumno')
        documento_nombre = request.form.get('Nombre_documento')
        comentario = request.form['comentario']
        
        if devolver_documento(id_alumno, documento_nombre,comentario):
            correo = session.get('correo')
            if correo:
                administracion = db['administradores']
                administracion.update_one(
                    {"correo": correo}, 
                    {'$set': {'ultimo_movimiento': 'Devolvio un documento'}}
                )
            flash('Documento devuelto exitosamente.', 'success')
        else:
            flash('No se pudo devolver el documento intentelo de nuevo.', 'danger')
        
        return redirect(url_for('Vinculacion.documento_alumnos', id_alumno=id_alumno))

@update_vinculacion_routes.route('/actualizar_estado_Actividad/<id_alumno>/<documento_id>', methods=['GET', 'POST'])
def actualizar_estado_Actividad(id_alumno, documento_id):
    db = current_app.get_db_connection()
    redirect_view = request.args.get('redirect_view')
    nombre = request.args.get('nombre')
    try:
        # Intentar actualizar el estado de la actividad
        if estado_actividad(ObjectId(id_alumno), ObjectId(documento_id)):
            correo = session.get('correo')
            if correo:
                administracion = db['administradores']
                administracion.update_one(
                    {"correo": correo}, 
                    {'$set': {'ultimo_movimiento': 'Completo una actividad'}}
                )
            flash(f'Actividad de {nombre} completada exitosamente.', 'success')
        else:
            flash(f'No se pudo actualizar el estado de la Actividad.', 'danger')
    except Exception as e:
        # Manejo de errores
        flash(f'Ocurrió un error al actualizar el estado: {str(e)}', 'danger')
    
    return redirect(url_for(redirect_view,id_alumno=id_alumno))

@update_vinculacion_routes.route('/terminar_Periodo/', methods=['POST'])
def terminarPeriodo():
        db = current_app.get_db_connection()
        conexion = db['Periodos']
        periodo_id = request.form['idPeriodo']
        conexion.update_one({'_id': ObjectId(periodo_id)}, {'$set': {'Estatus': False}})
        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo}, 
                {'$set': {'ultimo_movimiento': 'Finalizo un periodo'}}
            )
        return redirect(url_for('Vinculacion.iniciarPeriodo'))


@update_vinculacion_routes.route('/devolver_Documento_uta/', methods=['POST'])#####Admin
def devolver_documento_alumno_uta():
        db = current_app.get_db_connection()
        id_alumno = request.form.get('id_alumno')
        comentario = request.form['comentario']
        alumno = db['Alumnos'].find_one({'_id':ObjectId(id_alumno)})

        if alumno:
            correo = session.get('correo')
            if correo:
                administracion = db['administradores']
                administracion.update_one(
                    {"correo": correo}, 
                    {'$set': {'ultimo_movimiento': 'Devolvio un documento'}}
                )
            db['Alumnos'].update_one(
                {'_id':ObjectId(id_alumno)},
                {
                    '$set':{
                        'formato_tres_opciones.estado':'devuelto',
                        'formato_tres_opciones.comentario':comentario
                    }
                }
            )
            flash('Documento devuellto exitosamente.', 'success')
            return redirect(url_for('Vinculacion.documento_alumnos', id_alumno=id_alumno))
        else:
            flash('Alumno no encontrado en la base de datos','danger')
        return redirect(url_for('Vinculacion.documento_alumnos', id_alumno=id_alumno))