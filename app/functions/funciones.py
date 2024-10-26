from flask import current_app, flash, make_response, redirect, url_for

import functools

from bson import Binary, ObjectId


def nocache(view):
    @functools.wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache


def obtener_usuario_por_matricula(id_alumno):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    usuario = db['usuarios'].find_one({'_id': ObjectId(id_alumno)})
    return usuario


def obtener_documentos_alumno(id_alumno):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    documentos_collections = [
        'documentos_TSU', 'documentos_LIC_ING', 'documentos_foraneas', 'documentos_especiales']
    for collection in documentos_collections:
        documentos = db[collection].find_one({'id_usuario': id_alumno})
        if documentos:
            return documentos
    return None


def obtener_usuario_por_correo(correo):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    usuario = db['usuarios'].find_one({'correoAlumno': correo})
    return usuario


def obtener_documentos_alumno_uta(id_alumno):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    documentos_collections = [
        'documentos_TSU', 'documentos_LIC_ING', 'documentos_foraneas', 'documentos_especiales']
    for collection in documentos_collections:
        documentos = db[collection].find_one({'id_usuario': str(id_alumno)})
        if documentos:
            return documentos
    return None


def ver_documento_alumno_uta(id_alumno, nombre_archivo):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    documentos_collections = [
        'documentos_TSU', 'documentos_LIC_ING', 'documentos_foraneas', 'documentos_especiales']
    for collection in documentos_collections:
        try:
            documento = db[collection].find_one(
                {'id_usuario': id_alumno, f'{nombre_archivo}.archivo': {'$exists': True}})
            if documento and nombre_archivo in documento:
                return documento[nombre_archivo]['archivo']
        except Exception as e:
            print(f"Error al buscar documento en colección {collection}: {e}")
    return None


def subir_documento(id_alumno, documento_nombre, archivo):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    documentos_collections = [
        'documentos_TSU', 'documentos_LIC_ING', 'documentos_foraneas', 'documentos_especiales']
    for collection in documentos_collections:
        documento = db[collection].find_one({'id_usuario': id_alumno})
        if documento and documento_nombre in documento:
            if archivo:
                if archivo.filename.endswith('.pdf'):
                    archivo_data = archivo.read()
                    # Almacena el contenido del archivo como datos binarios en la base de datos
                    archivo_bin = Binary(archivo_data)
                else:
                    flash(
                        'El archivo debe ser .pdf, .doc, .docx, .xlsx, .xls', 'warning')
                    return redirect(url_for('alumno_vista', id_alumno=id_alumno))
            else:
                archivo_bin = None
            db[collection].update_one(
                {'id_usuario': id_alumno},
                {'$set': {f'{documento_nombre}.estado': 'entregado', f'{
                    documento_nombre}.archivo': archivo_bin, f'{documento_nombre}.comentario': None}}
            )
            return True
    return False


def actualizar_estado_documento(id_alumno, documento_nombre):
    db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
    documentos_collections = [
        'documentos_TSU', 'documentos_LIC_ING', 'documentos_foraneas', 'documentos_especiales']
    for collection in documentos_collections:
        documento = db[collection].find_one({'id_usuario': id_alumno})
        if documento and documento_nombre in documento:
            db[collection].update_one(
                {'id_usuario': id_alumno},
                {'$set': {f'{documento_nombre}.estado': 'activo'}}
            )
            return True
    return False
