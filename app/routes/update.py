from flask import Blueprint, current_app, flash, redirect, url_for, request
from app.functions.funciones import subir_documento
from bson import Binary, ObjectId

update_routes = Blueprint('update', __name__)


@update_routes.route('/subir_Documento_uta/', methods=['POST'])  # Alumno
def subir_documento_alumno_uta():
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    id_alumno = request.form.get('id_alumno')
    alumno = db['Alumnos'].find_one({'_id': ObjectId(id_alumno)})
    archivo = request.files['archivo']
    if alumno:
        if archivo:
            if archivo.filename.endswith('.pdf'):
                archivo_data = archivo.read()
                archivo_bin = Binary(archivo_data)

                # Actualiza el documento del alumno
                db['Alumnos'].update_one(
                    {'_id': ObjectId(id_alumno)},
                    {'$set': {
                        'formato_tres_opciones.estado': 'entregado',
                        'formato_tres_opciones.archivo': archivo_bin}}
                )
                flash('Documento subido exitosamente', 'success')
            else:
                flash('El archivo debe ser .pdf', 'warning')
        else:
            flash('No se ha seleccionado ningún archivo', 'warning')
    else:
        flash('Alumno no encontrado en la base de datos', 'danger')

    return redirect(url_for('alumno.alumno_vista', id_alumno=id_alumno))


@update_routes.route('/subir_documento_alumo/<id_alumno>/<documento_nombre>', methods=['GET', 'POST'])
def subir_documento_uta(id_alumno, documento_nombre):
    if request.method == 'POST':
        archivo = request.files['archivo']
        if subir_documento(id_alumno, documento_nombre, archivo):
            flash('Documento subido exitosamente.', 'success')
        else:
            flash('No se pudo subir el documento. Inténtelo de nuevo.', 'danger')
        return redirect(url_for('alumno.alumno_vista', id_alumno=id_alumno))
    return redirect(url_for('alumno.alumno_vista', id_alumno=id_alumno))
