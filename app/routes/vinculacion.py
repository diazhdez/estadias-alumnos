
import bcrypt
from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
from app.functions.funciones import nocache, obtener_documentos_alumno_uta, asignar_actividades, progreso_alumno
from datetime import datetime
from bson import Binary, ObjectId
import pandas as pd
Vinculacion_routes = Blueprint('Vinculacion', __name__)


@Vinculacion_routes.route("/EduLink/Vinculación/administrar_Alumnos/")
@nocache
def Home():
    if 'correo' in session:
        db = current_app.get_db_connection()
        correo_usuario = session['correo']
        administradores = db["administradores"]
        
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})  
        if administrador:     
            alumnos = db["Alumnos"]
            # Obtener la lista de Periodos
            periodos = list(db['Periodos'].find())
 
            # Convertir periodos a diccionarios con _id como clave
            periodos_dict = {str(periodo['_id']): {'Duracion': periodo['Duracion']} for periodo in periodos}
            
            # Obtener todos los alumnos
            lista_alumnos = list(alumnos.find({}))

            # Crear una lista para almacenar los alumnos con su progreso
            alumnos_con_progreso = []

            for alumno in lista_alumnos:
                periodo_info = periodos_dict.get(alumno.get('Periodo'), {'Duracion': ''})
                alumno['Duracion'] = periodo_info['Duracion']
                
                # Calcular el progreso y obtener las actividades del alumno
                progreso, actividades_alumno = progreso_alumno(alumno["_id"])

                # Añadir el progreso y las actividades al diccionario del alumno
                alumno["progreso"] = progreso
                alumno["actividades"] = actividades_alumno

                # Agregar a la lista de resultados
                alumnos_con_progreso.append(alumno)

            return render_template("vinculacion/alumnos.html", alumnos=alumnos_con_progreso, periodos=periodos)
        else:
            flash('Acceso denegado: No eres un administrador.', 'danger')
            return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))
    

@Vinculacion_routes.route("/EduLink/Vinculación/Archivos_Universidad/")
@nocache
def carga():
    if 'correo' in session:
        db = current_app.get_db_connection()
        correo_usuario = session['correo']
        administradores = db["administradores"]
        periodos=db['Periodos'].find()
        
        # Verifica si el correo está en la colección de administradores
        administrador = administradores.find_one({'correo': correo_usuario})  
        if administrador:  
            

            return render_template("vinculacion/CargaAlumnos.html", Periodos=periodos)
        else:
         flash('Acceso denegado: No eres un administrador.', 'danger')
         return redirect(url_for('session.login'))
    else:
        return redirect(url_for('session.login'))
    
@Vinculacion_routes.route('/EduLink/Vinculación/Carga_Alumnos', methods=['POST'])
def carga_alumnos():
        db = current_app.get_db_connection()
        archivo = request.files['archivo']
        alumno = db["Alumnos"]
        carga = db ["Carga_Alumnos"]
       
        Periodo = request.form.get('Periodo')
        TSU_ING = request.form.get('tsu_ing')
        fecha_carga = datetime.combine(datetime.now().date(), datetime.min.time())

        existe_carga = carga.find_one({'periodo': Periodo, 'TSU_ING': TSU_ING})
        if existe_carga:
                flash(f'Ya existe una carga de alumnos para el periodo "{Periodo}" y tipo "{TSU_ING}".', 'warning')
                return redirect(url_for('Viculacion.carga'))
        else:
            archivo_data = archivo.read()
            archivo_bin = Binary(archivo_data)
            carga.insert_one({
                    'Archivo': archivo_bin,
                    'periodo':Periodo,
                    'TSU_ING':TSU_ING,
                    'Fecha_Carga':fecha_carga  # Almacena solo la fecha (YYYY-MM-DD)
                })
        if archivo:

            if archivo.filename.endswith('.xlsx') or archivo.filename.endswith('.xls'):
                # Leer el archivo Excel y seleccionar las columnas necesarias
                alumnos = pd.read_excel(archivo, usecols=['Nombre', 'Apellido_Pat', 'Apellido_Mat', 'Matricula','Correo_Institucional','Contraseña','Telefono','Carrera','Cuatrimestre','Grupo'])
                
                # Validar que no haya datos faltantes en las columnas requeridas
                if alumnos[['Nombre', 'Apellido_Pat', 'Apellido_Mat', 'Matricula','Correo_Institucional','Contraseña','Telefono','Carrera','Cuatrimestre','Grupo']].isnull().any().any():
                    flash('El archivo contiene filas con datos faltantes. Asegúrate de que todos los campos estén completos.', 'warning')
                    return redirect(url_for('catalago'))
                
                # Encriptar contraseñas y agregar las columnas adicionales
                for index, row in alumnos.iterrows():
                    # Encriptar la contraseña
                    password = row['Contraseña']
                    if password and isinstance(password, str):
                        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                        alumnos.at[index, 'Contraseña'] = hashed_password.decode('utf-8')
                
                alumnos['Periodo'] = Periodo        
                alumnos['TSU/ING'] = TSU_ING
                
                # Convertir los datos a JSON para insertarlos en MongoDB
                data_json = alumnos.to_dict(orient='records')
                
                # Insertar los registros en la base de datos
                alumno.insert_many(data_json)
                

                # Llamar a la función para registrar actividades
                if asignar_actividades():
                    flash('Alumnos cargados exitosamente', 'success')
                else:
                    flash('Alumnos cargados, pero ocurrió un error al registrar actividades.', 'warning')
            else:
                flash('El archivo debe de ser .xlsx, .xls para poder ser compatible', 'warning')
                return redirect(url_for('Vinculacion.Home'))
        else:
            archivo = None

        return redirect(url_for('Vinculacion.Home'))