
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
                {'$set': {f'{documento_nombre}.estado': 'entregado', f'{documento_nombre}.archivo': archivo_bin, f'{documento_nombre}.comentario': None}}
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

def progreso_alumno(id_alumno):
    db = current_app.get_db_connection()
    Alumnos_Act = db["Alumnos_Actividades"]
    Actividades = db["Actividades"]

    # Obtener todas las actividades desde la colección `Actividades` y ordenarlas por el campo `orden`
    lista_actividades = list(Actividades.find({}).sort("orden", 1))

    # Crear un diccionario para acceder al nombre de la actividad por su ID usando el campo "Actividad"
    actividades_dict = {actividad["_id"]: actividad["Actividad"] for actividad in lista_actividades}

    # Obtener las IDs de las actividades en el orden correcto
    actividades_ordenadas = [actividad["_id"] for actividad in lista_actividades]

    # Obtener todas las actividades del alumno
    actividades_alumno = list(Alumnos_Act.find({"idAlumno": id_alumno}))

    # Crear un diccionario para mapear las actividades del alumno por su ID
    actividades_alumno_dict = {actividad["idActividad"]: actividad for actividad in actividades_alumno}

    # Lista para almacenar todas las actividades con información completa
    todas_las_actividades = []
    completadas = 0

    # Revisar todas las actividades en el orden y agregarlas con sus respectivos estados
    for actividad_id in actividades_ordenadas:
        # Nombre de la actividad
        actividad_nombre = actividades_dict.get(actividad_id, "Actividad no encontrada")

        # Verificar si el alumno ha realizado esta actividad
        if actividad_id in actividades_alumno_dict:
            actividad_alumno = actividades_alumno_dict[actividad_id]
            estatus = actividad_alumno["estatus"]
        else:
            estatus = "pendiente"

        # Añadir a la lista de actividades con nombre y estado
        todas_las_actividades.append({
            "idActividad": actividad_id,
            "nombre": actividad_nombre,
            "estatus": estatus
        })

        # Contar las completadas
        if estatus == "completado":
            completadas += 1

    # Calcular el porcentaje de progreso
    total_actividades = len(lista_actividades)
    if total_actividades > 0:
        progreso = (completadas / total_actividades) * 100
    else:
        progreso = 0

    return progreso, todas_las_actividades  # Devuelve el progreso y todas las actividades con estatus y nombres

def asignar_actividades():
    # Colecciones
        db = current_app.get_db_connection()
        Actividades = db["Actividades"]
        Alumnos_Act = db["Alumnos_Actividades"]
        Alumnos = db["Alumnos"]

        lista_actividades = list(Actividades.find().sort("Orden", 1))  # Convertir a lista para evitar múltiples consultas

        # Obtener todos los IDs de los alumnos
        id_alumnos = [alumno["_id"] for alumno in Alumnos.find({}, {"_id": 1})]

        # Crear registros en Alumnos_Actividades para cada alumno y cada actividad
        for id_alumno in id_alumnos:
            alumno_actividades = []  # Crea un arreglo para las actividades del alumno
            for actividad in lista_actividades:
                # Verificar si la actividad es la de orden 1
                estatus = "completado" if actividad["Orden"] == "1" else "no iniciado"

                alumno_actividad = {
                    "idAlumno": id_alumno,
                    "idActividad": actividad["_id"],
                    "estatus": estatus  # Establecer el estatus según el orden de la actividad
                }
                alumno_actividades.append(alumno_actividad)  # Inserta en el arreglo alumno_actividad

            # Inserta las actividades a un alumno y regresa para seguir con otro alumno
            if alumno_actividades:
                Alumnos_Act.insert_many(alumno_actividades)

        return True

def obtener_alumno(id_alumno):
    db = current_app.get_db_connection()
    usuario = db['Alumnos'].find_one({'_id': ObjectId(id_alumno)})
    return usuario