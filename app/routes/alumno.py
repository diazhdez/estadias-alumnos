from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
from app.functions.funciones import nocache, obtener_documentos_alumno_uta, obtener_usuario_por_correo, progreso_alumno

alumno_routes = Blueprint('alumno', __name__)


@alumno_routes.route('/EduLink/Alumno/')
@nocache
def alumno_vista():
    correo = session.get('correo')
    if correo:
        alumno = obtener_usuario_por_correo(correo)
        if alumno:
            documentacion_alumno = obtener_documentos_alumno_uta(alumno['_id'])

            # Obtener la lista de carreras y periodos
            db = current_app.get_db_connection()
            carreras = list(db['carreras'].find())
            periodos = list(db['Periodos'].find())

            # Convertir carreras y periodos a diccionarios con _id como clave
            carreras_dict = {
                str(carrera['_id']): carrera['NombreCarrera'] for carrera in carreras
            }
            periodos_dict = {
                str(periodo['_id']): {
                    'NombrePeriodo': periodo['NombrePeriodo'],
                    'Duracion': periodo['Duracion']
                } for periodo in periodos
            }

            # Asignar el nombre de la carrera y del periodo al alumno actual
            alumno['NombreCarrera'] = carreras_dict.get(
                alumno.get('idCarrera', ''), 'Carrera no encontrada'
            )
            periodo_info = periodos_dict.get(
                alumno.get('idPeriodo', ''),  # Asegúrate de que esto se maneje correctamente
                {'NombrePeriodo': 'Periodo no encontrado', 'Duracion': ''}
            )
            alumno['NombrePeriodo'] = periodo_info['NombrePeriodo']
            alumno['Duracion'] = periodo_info['Duracion']

            # Calcular el progreso y obtener las actividades del alumno
            progreso, actividades_alumno = progreso_alumno(alumno['_id'])
            alumno["progreso"] = progreso  # Almacena el progreso directamente en el diccionario alumno
            alumno["actividades"] = actividades_alumno  # Almacena las actividades directamente en el diccionario alumno

            return render_template(
                'Alumnos/alumno_uta.html',
                alumno=alumno,
                documentos=documentacion_alumno,
                Carreras=carreras,
                Periodos=periodos
            )
        else:
            flash('No se encontró al alumno.', 'danger')
    return redirect(url_for('session.login'))



@alumno_routes.route('/EduLink/Alumno/Archivos_Universidad/')
@nocache
def catalago():
    if 'correo' in session:
        db = current_app.get_db_connection()  # Obtener la conexión a la base de datos
        conexion = db['archivos_vinculacion']
        # Convertir el cursor a una lista de documentos
        archivos = list(conexion.find())
        for archivo in archivos:
            archivo['extension'] = archivo['nombre'].split(
                '.')[-1].lower()  # Obtener la extensión de cada archivo
        return render_template("Archivos_uta.html", archivos=archivos)
    else:
        flash('Acceso denegado: Debes de inciar sesion.', 'danger')
        return redirect(url_for('session.login'))