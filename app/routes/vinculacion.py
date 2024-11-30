
import bcrypt
from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
from app.functions.funciones import asignar_actividades1, nocache, obtener_administrador_por_correo, obtener_alumno, obtener_documentos_alumno, obtener_documentos_alumno_uta, asignar_actividades, progreso_alumno
from app.functions.utils import requiere_permisos
from datetime import datetime
from bson import Binary, ObjectId
import pandas as pd
Vinculacion_routes = Blueprint('Vinculacion', __name__)


@Vinculacion_routes.route("/EduLink/Vinculación/administrar_Alumnos/")
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete", "update", "view"], departamento_requerido="vinculacion")
def Home():
    correo = session.get('correo')
    if 'correo' in session:
        db = current_app.get_db_connection()
        correo_usuario = session['correo']
        administradores = db["administradores"]
        admin = obtener_administrador_por_correo(correo)
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})
        if administrador:
            alumnos = db["Alumnos"]
            # Obtener la lista de Periodos
            periodos = list(db['Periodos'].find())

            # Convertir periodos a diccionarios con _id como clave
            periodos_dict = {str(periodo['_id']): {
                'Duracion': periodo['Duracion']} for periodo in periodos}

            # Obtener todos los alumnos
            lista_alumnos = list(alumnos.find({}))

            # Crear una lista para almacenar los alumnos con su progreso
            alumnos_con_progreso = []

            for alumno in lista_alumnos:
                periodo_info = periodos_dict.get(
                    alumno.get('Periodo'), {'Duracion': ''})
                alumno['Duracion'] = periodo_info['Duracion']

                # Calcular el progreso y obtener las actividades del alumno
                progreso, actividades_alumno = progreso_alumno(alumno["_id"])

                # Añadir el progreso y las actividades al diccionario del alumno
                alumno["progreso"] = progreso
                alumno["actividades"] = actividades_alumno

                # Agregar a la lista de resultados
                alumnos_con_progreso.append(alumno)

            return render_template("vinculacion/alumnos.html", alumnos=alumnos_con_progreso, periodos=periodos, administrador=admin)
        else:
            flash('Acceso denegado: No eres un administrador.', 'danger')
            return redirect(url_for('main.index'))
    else:
        flash('Acceso denegado: No eres un administrador.', 'danger')
        return redirect(url_for('main.index'))


@Vinculacion_routes.route("/EduLink/Vinculación/DocumentoAlumno/")
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete", "update", "view"], departamento_requerido="vinculacion")
def documento_alumnos():
    correo = session.get('correo')
    if 'correo' in session:
        db = current_app.get_db_connection()
        admin = obtener_administrador_por_correo(correo)
        correo_usuario = session['correo']
        administradores = db["administradores"]
        administrador = administradores.find_one({'correo': correo_usuario})

        if administrador:
            # Obtener id_alumno desde request.form o request.args
            id_alumno = request.form.get(
                'id_alumno') or request.args.get('id_alumno')

            if not id_alumno:
                flash('ID de alumno no proporcionado.', 'danger')
                return redirect(url_for('Vinculacion.Home'))

            alumno = obtener_alumno(id_alumno)

            if alumno:
                documentos = obtener_documentos_alumno(id_alumno)

                periodos = list(db['Periodos'].find())
                periodos_dict = {str(periodo['_id']): {
                    'Duracion': periodo['Duracion']} for periodo in periodos}
                periodo_info = periodos_dict.get(
                    alumno.get('Periodo'), {'Duracion': ''})

                alumno['Duracion'] = periodo_info['Duracion']
                progreso, actividades_alumno = progreso_alumno(alumno["_id"])
                alumno["progreso"] = progreso
                alumno["actividades"] = actividades_alumno

                return render_template('vinculacion/AlumnosDocumentos.html', alumno=alumno, documentos=documentos, periodos=periodos, administrador=admin)
            else:
                flash('Alumno no encontrado.', 'danger')
                return redirect(url_for('Vinculacion.Home'))
        else:
            flash('Acceso denegado: No eres un administrador.', 'danger')
            return redirect(url_for('main.index'))
    else:
        flash('Acceso denegado: No eres un administrador.', 'danger')
        return redirect(url_for('main.index'))


@Vinculacion_routes.route("/EduLink/Vinculación/Carga/")
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete", "update", "view"], departamento_requerido="vinculacion")
def carga():
    correo = session.get('correo')
    if 'correo' in session:
        db = current_app.get_db_connection()
        admin = obtener_administrador_por_correo(correo)
        correo_usuario = session['correo']
        administradores = db["administradores"]
        periodos = db['Periodos'].find()

        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})
        if administrador:

            return render_template("vinculacion/CargaAlumnos.html", Periodos=periodos, administrador=admin)
        else:
            flash('Acceso denegado: No eres un administrador.', 'danger')
            return redirect(url_for('main.index'))
    else:
        flash('Acceso denegado: No eres un administrador.', 'danger')
        return redirect(url_for('main.index'))


@Vinculacion_routes.route('/EduLink/Vinculación/Carga_Alumnos', methods=['POST'])
@requiere_permisos(permisos_requeridos=["create", "delete", "update", "view"], departamento_requerido="vinculacion")
def carga_alumnos():
    db = current_app.get_db_connection()
    archivo = request.files['archivo']
    alumno = db["Alumnos"]
    carga = db["Carga_Alumnos"]

    Periodo = request.form.get('Periodo')
    TSU_ING = request.form.get('tsu_ing')
    fecha_carga = datetime.combine(datetime.now().date(), datetime.min.time())

    if archivo:
        if archivo.filename.endswith('.xlsx') or archivo.filename.endswith('.xls'):
            try:
                # Leer el archivo Excel y seleccionar las columnas necesarias
                alumnos = pd.read_excel(archivo, usecols=['Matricula', 'Apellido_Pat', 'Apellido_Mat', 'Nombre',
                                                          'Correo_Institucional', 'Contraseña', 'Telefono',
                                                          'Carrera', 'Cuatrimestre', 'Grupo', 'Tipo_estadía'])

                # Validar que no haya datos faltantes en las columnas requeridas
                if alumnos[['Matricula', 'Apellido_Pat', 'Apellido_Mat', 'Nombre',
                            'Correo_Institucional', 'Contraseña', 'Telefono',
                            'Carrera', 'Cuatrimestre', 'Grupo']].isnull().any().any():
                    flash(
                        'El archivo contiene filas con datos faltantes. Asegúrate de que todos los campos estén completos.', 'warning')
                    return redirect(url_for('catalago'))

                # Verificar si ya existe una carga
                existe_carga = carga.find_one(
                    {'periodo': Periodo, 'TSU_ING': TSU_ING})
                if existe_carga:
                    flash(f'Ya existe una carga de alumnos para el periodo "{Periodo}" y tipo "{TSU_ING}".', 'warning')
                    return redirect(url_for('Vinculacion.carga'))

                # Almacenar el archivo en binario
                archivo_data = archivo.read()
                archivo_bin = Binary(archivo_data)
                carga.insert_one({
                    'Archivo': archivo_bin,
                    'periodo': Periodo,
                    'TSU_ING': TSU_ING,
                    # Almacena solo la fecha (YYYY-MM-DD)
                    'Fecha_Carga': fecha_carga
                })

                # Encriptar contraseñas y agregar columnas adicionales
                for index, row in alumnos.iterrows():
                    password = row['Contraseña']
                    if password and isinstance(password, str):
                        # Hashear la contraseña y almacenarla como bytes
                        hashed_password = bcrypt.hashpw(
                            password.encode('utf-8'), bcrypt.gensalt())
                        # Almacena como bytes
                        alumnos.at[index, 'Contraseña'] = hashed_password

                alumnos['Periodo'] = Periodo
                alumnos['TSU/ING'] = TSU_ING
                alumnos['formato_tres_opciones'] = alumnos.apply(
                    lambda x: {"estado": "activo", "archivo": None, "comentario": None}, axis=1)
                alumnos['permisos'] = alumnos.apply(
                    lambda x: ["update", "view"], axis=1)
                alumnos['en_linea']="False"
                alumnos['ultima_conexion']= None

                # Convertir los datos a JSON para insertarlos en MongoDB
                data_json = alumnos.to_dict(orient='records')

                # Insertar los registros en la base de datos
                alumno.insert_many(data_json)

                correo = session.get('correo')
                if correo:
                    administracion = db['administradores']
                    administracion.update_one(
                        {"correo": correo},
                        {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                            'movimientos': {
                                'tipo': 'hizo la carga de alumno',
                                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                        }}
                    )

                # Llamar a la función para registrar actividades
                if asignar_actividades1():
                    flash('Alumnos cargados exitosamente', 'success')
                else:
                    flash(
                        'Alumnos cargados, pero ocurrió un error al registrar actividades.', 'warning')

            except Exception as e:
                flash(f'Ocurrió un error: {str(e)}', 'danger')
                return redirect(url_for('Vinculacion.Home'))

        else:
            flash(
                'El archivo debe de ser .xlsx o .xls para poder ser compatible', 'warning')
            return redirect(url_for('Vinculacion.Home'))

    return redirect(url_for('Vinculacion.Home'))


@Vinculacion_routes.route('/aceptar_documento_uta/', methods=['GET', 'POST'])
@requiere_permisos(permisos_requeridos=["create", "delete", "update", "view"], departamento_requerido="vinculacion")
def aceptar_documento_nuevo_uta():
    db = current_app.get_db_connection()
    id_alumno = request.form.get('id_alumno')
    Tipo_estadía = request.form.get('tipo_estadia')
    estadia_Alumno = request.form.get('estadia_Alumno')
    nombre = request.form.get('nombre')

    # Verifica si el ID del alumno y el tipo de estadía están presentes
    if not id_alumno or not Tipo_estadía:
        flash('Información incompleta para aceptar el documento.', 'danger')
        return redirect(url_for('Vinculacion.Home'))

    # Intenta encontrar el alumno en la base de datos
    alumno = db['Alumnos'].find_one({'_id': ObjectId(id_alumno)})
    if not alumno:
        flash('Alumno no encontrado en la base de datos', 'danger')
        return redirect(url_for('Vinculacion.Home'))

    if Tipo_estadía == 'documentos_Especiales':
        documentos_Especiales_data = {
            "id_usuario": id_alumno,
            "vigencia_del_imss": {"estado": "activo", "archivo": None, "comentario": None},
            "kardex": {"estado": "activo", "archivo": None, "comentario": None},
            "formato_autorizacion_estadías": {"estado": "desactivado", "archivo": None, "comentario": None},
            "oficio_tutor_autorizando_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
            "registro_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
            "cronograma_de_actividades": {"estado": "desactivado", "archivo": None, "comentario": None},
            "1er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "2do_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "3er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_liberación_de_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_liberación_de_memoria": {"estado": "desactivado", "archivo": None, "comentario": None}
        }

        db['Alumnos'].update_one(
            {'_id': ObjectId(id_alumno)},
            {
                '$set': {
                    'formato_tres_opciones.estado': 'aceptado',
                    'Tipo_estadía': Tipo_estadía
                }
            }
        )

        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo},
                {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                    'movimientos': {
                        'tipo': f'Asignó un tipo de estadía a {nombre}',
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }}
            )

        db['documentos_especiales'].insert_one(documentos_Especiales_data)
        flash(f'Se le asignó la estadía Especial a {nombre} exitosamente', 'success')
        return redirect(url_for('Vinculacion.documento_alumnos', id_alumno=id_alumno))

    elif Tipo_estadía == 'documentos_Foraneas':
        documentos_Foraneas_data = {
            "id_usuario": id_alumno,
            "vigencia_del_imss": {"estado": "activo", "archivo": None, "comentario": None},
            "kardex": {"estado": "activo", "archivo": None, "comentario": None},
            "formato_autorizacion_estadías": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_de_buena_conducta": {"estado": "desactivado", "archivo": None, "comentario": None},
            "kardex_actualizado": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_compromiso_firmada": {"estado": "desactivado", "archivo": None, "comentario": None},
            "acuse_solicitud_de_espacio": {"estado": "desactivado", "archivo": None, "comentario": None},
            "acuse_carta_presentación": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_aceptación": {"estado": "desactivado", "archivo": None, "comentario": None},
            "registro_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
            "cronograma_de_actividades": {"estado": "desactivado", "archivo": None, "comentario": None},
            "1er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "2do_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "3er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "evaluación de estadía por empresa": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_liberación_de_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_liberación_de_memoria": {"estado": "desactivado", "archivo": None, "comentario": None}
        }

        # Actualizar el estado del alumno y el tipo de estadía
        db['Alumnos'].update_one(
            {'_id': ObjectId(id_alumno)},
            {
                '$set': {
                    'formato_tres_opciones.estado': 'aceptado',
                    'Tipo_estadía': Tipo_estadía
                }
            }
        )

        
        # Insertar los documentos especiales para el alumno
        db['documentos_foraneas'].insert_one(documentos_Foraneas_data)

        # Asignar las actividades foráneas al alumno
        actividades_foraneas = db['Actividades'].find({"Tipo": "Foranea"})
        alumno_actividades = []
        for actividad in actividades_foraneas:
            alumno_actividad = {
                "idAlumno": ObjectId(id_alumno),
                "idActividad": actividad["_id"],
                "estatus": "no iniciado"
            }
            alumno_actividades.append(alumno_actividad)

        # Insertar las asignaciones de actividades
        if alumno_actividades:
            db['Alumnos_Actividades'].insert_many(alumno_actividades)

        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo},
                {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                    'movimientos': {
                        'tipo': f'Asignó un tipo de estadía a {nombre}',
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }}
            )

        flash(f'Se le asignó la estadía Foránea a {nombre} exitosamente', 'success')
        return redirect(url_for('Vinculacion.documento_alumnos', id_alumno=id_alumno))

    elif estadia_Alumno == 'TSU' and Tipo_estadía == 'documentosTSU':
        documentosTSU_data = {
            "id_usuario": id_alumno,
            "vigencia_del_imss": {"estado": "activo", "archivo": None, "comentario": None},
            "kardex": {"estado": "activo", "archivo": None, "comentario": None},
            "formato_autorizacion_estadías": {"estado": "desactivado", "archivo": None, "comentario": None},
            "copia_carnet": {"estado": "desactivado", "archivo": None, "comentario": None},
            "vigencia_seguro_social": {"estado": "desactivado", "archivo": None, "comentario": None},
            "acuse_solicitud_de_espacio": {"estado": "desactivado", "archivo": None, "comentario": None},
            "acuse_carta_presentación": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_aceptación": {"estado": "desactivado", "archivo": None, "comentario": None},
            "registro_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
            "cronograma_de_actividades": {"estado": "desactivado", "archivo": None, "comentario": None},
            "1er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "2do_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "3er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "evaluación_de_estadía_por_empresa": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_de_liberación_por_empresa": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_liberación_de_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_liberación_de_memoria": {"estado": "desactivado", "archivo": None, "comentario": None}
        }

        db['Alumnos'].update_one(
            {'_id': ObjectId(id_alumno)},
            {
                '$set': {
                    'formato_tres_opciones.estado': 'aceptado',
                    'Tipo_estadía': "TSU"
                }
            }
        )

        correo = session.get('correo')
        if correo:
                    administracion = db['administradores']
                    administracion.update_one(
                        {"correo": correo}, 
                        {'$set': {'ultimo_movimiento': 'asigno un tipo de estadia a {nombre} '}}
                    )

        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo},
                {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                    'movimientos': {
                        'tipo': f'Asignó un tipo de estadía a {nombre}',
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }}
            )

        db['documentos_TSU'].insert_one(documentosTSU_data)
        flash(f'Se le asignó la estadía Normal en TSU a {nombre} exitosamente', 'success')
        return redirect(url_for('Vinculacion.documento_alumnos', id_alumno=id_alumno))

    else:
        documentosLIC_ING_data = {
            "id_usuario": id_alumno,
            "vigencia_del_imss": {"estado": "activo", "archivo": None, "comentario": None},
            "kardex": {"estado": "activo", "archivo": None, "comentario": None},
            "formato_autorizacion_estadías": {"estado": "desactivado", "archivo": None, "comentario": None},
            "acuse_solicitud_de_espacio": {"estado": "desactivado", "archivo": None, "comentario": None},
            "acuse_carta_presentación": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_aceptación": {"estado": "desactivado", "archivo": None, "comentario": None},
            "registro_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
            "cronograma_de_actividades": {"estado": "desactivado", "archivo": None, "comentario": None},
            "1er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "2do_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "3er_informe": {"estado": "desactivado", "archivo": None, "comentario": None},
            "evaluación_de_estadía_por_empresa": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta de liberación por empresa": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_liberación_de_estadía": {"estado": "desactivado", "archivo": None, "comentario": None},
            "carta_liberación_de_memoria": {"estado": "desactivado", "archivo": None, "comentario": None}
        }

        db['Alumnos'].update_one(
            {'_id': ObjectId(id_alumno)},
            {
                '$set': {
                    'formato_tres_opciones.estado': 'aceptado',
                    'Tipo_estadía': 'LIC.ING.'
                }
            }
        )

        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo},
                {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                    'movimientos': {
                        'tipo': f'Asignó un tipo de estadía a {nombre}',
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }}
            )

        db['documentos_LIC_ING'].insert_one(documentosLIC_ING_data)
        flash(f'Se le asignó la estadía Normal en LIC.ING. a {nombre} exitosamente', 'success')
        return redirect(url_for('Vinculacion.documento_alumnos', id_alumno=id_alumno))


@Vinculacion_routes.route("/EduLink/Vinculación/Archivos_Universidad/")
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete", "update", "view"], departamento_requerido="vinculacion")
def archivos_vinculacion():
    correo = session.get('correo')
    db = current_app.get_db_connection()
    admin = obtener_administrador_por_correo(correo)
    if 'correo' in session:
        correo_usuario = session['correo']
        administradores = db["administradores"]


        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})
        if administrador:
            conexion = db['archivos_vinculacion']
            # Convertir el cursor a una lista de documentos
            archivos = list(conexion.find())
            for archivo in archivos:
                archivo['extension'] = archivo['nombre'].split(
                    '.')[-1].lower()  # Obtener la extensión de cada archivo
            return render_template("vinculacion/Archivos_vinculacion.html", archivos=archivos, administrador=admin)
        else:
            flash('Acceso denegado: No eres un administrador.', 'danger')
            return redirect(url_for('smain.index'))
    else:
        flash('Acceso denegado: No eres un administrador.', 'danger')
        return redirect(url_for('main.index'))


@Vinculacion_routes.route("/EduLink/Vinculación/Periodos/")
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete", "update", "view"], departamento_requerido="vinculacion")
def iniciarPeriodo():
    correo = session.get('correo')
    db = current_app.get_db_connection()
    if 'correo' in session:
        correo_usuario = session['correo']
        administradores = db["administradores"]
        admin = obtener_administrador_por_correo(correo)
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})

        if administrador:
            conexion = db["Periodos"]
            Periodos = list(conexion.find({'Estatus': True}))
            return render_template("Vinculacion/iniciarPeriodo.html", Periodos=Periodos, administrador=admin)
        else:
            flash('Acceso denegado: No eres un administrador.', 'danger')
            return redirect(url_for('main.index'))
    else:
        flash('Acceso denegado: No eres un administrador.', 'danger')
        return redirect(url_for('main.index'))


@Vinculacion_routes.route("/agregar_Priodo/", methods=['POST'])
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete", "update", "view"], departamento_requerido="vinculacion")
def agregarPeriodo():
    db = current_app.get_db_connection()
    conexion = db["Periodos"]
    nombre_periodo = request.form["N_periodo"]
    duración = request.form["periodo"]
    Status = True
    estatus_existente = conexion.count_documents({'Estatus': Status})

    if estatus_existente < 2:
        correo = session.get('correo')
        if correo:
            administracion = db['administradores']
            administracion.update_one(
                {"correo": correo},
                {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                    'movimientos': {
                        'tipo': 'Inicio un periodo nuevo',
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }}
            )
        conexion.insert_one({
            'NombrePeriodo': nombre_periodo,
            'Duracion': duración,
            'Estatus': Status
        })
        flash('Periodo creado correctamente', 'success')
        return redirect(url_for("Vinculacion.iniciarPeriodo"))
    else:

        flash('Ya existe un periodo activo', 'danger')
        return redirect(url_for("Vinculacion.iniciarPeriodo"))
