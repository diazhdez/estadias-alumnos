
import bcrypt
from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
from app.functions.funciones import nocache, obtener_administrador_por_correo, obtener_alumno, obtener_documentos_alumno, obtener_documentos_alumno_uta, asignar_actividades, progreso_alumno
from app.functions.utils import requiere_permisos
from datetime import datetime
from bson import Binary, ObjectId
import pandas as pd

Servicios_routes = Blueprint('Servicios', __name__)


@Servicios_routes.route("/EduLink/Servicios_Escolares/administrar_Alumnos/")
@nocache
@requiere_permisos(permisos_requeridos=["update", "view"], departamento_requerido="servicios_escolares")
def Servicios():
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

            return render_template("Servicios/servicios_escolares.html", alumnos=alumnos_con_progreso, periodos=periodos, administrador=admin)
        else:
            flash('Acceso denegado: No eres un administrador.', 'danger')
            return redirect(url_for('main.index'))
    else:
        flash('Acceso denegado: No eres un administrador.', 'danger')
        return redirect(url_for('main.index'))