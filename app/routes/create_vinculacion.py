from datetime import datetime
from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
from app.functions.funciones import nocache, obtener_documentos_alumno_uta, asignar_actividades, progreso_alumno
from app.functions.utils import requiere_permisos
import bcrypt

create_vinculacion_routes = Blueprint('create_vinculacion', __name__)


@create_vinculacion_routes.route("/EduLink/Vinculación/agregar_Alumno/", methods=['POST'])
@requiere_permisos(permisos_requeridos=["create", "delete", "update", "view"], departamento_requerido="vinculacion")
def agregarAlumno():
        db = current_app.get_db_connection()
        alumnos = db["Alumnos"]
        if request.method == 'POST':
            correo = request.form['Correo']
            matricula = request.form['Matricula']
            existing_alumno = alumnos.find_one({
                '$or': [
                    {'Correo_Institucional': correo},
                    {'Matricula': matricula}
                ]
            })
            if existing_alumno:
                flash ('El correo o la matrícula ya están registrados.','warning')
                return redirect(url_for('administrarAlumno'))
            
            

            nombre = request.form['Nombre']
            apellido_Pat = request.form['Apellido_Pat']
            apellido_Mat = request.form['Apellido_Mat']
            carrera = request.form['Carrera']
            estadia = request.form['Estadia']
            periodo = request.form['idPeriodo']
            grupo = request.form['Grupo']
            telefono =request.form['Telefono']
            password = request.form['Contraseña']
            cuatrimestre = request.form['Cuatrimestre']
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Inserta el nuevo alumno en la base de datos
            nuevo_alumno_id = alumnos.insert_one({
                'Matricula': matricula,
                'Nombre': nombre,
                'Apellido_Pat': apellido_Pat,
                'Apellido_Mat': apellido_Mat,
                'Correo_Institucional': correo,
                'Contraseña': hashpass,
                'Telefono': telefono,
                'Carrera': carrera,
                'Cuatrimestre': cuatrimestre,
                'Grupo': grupo,
                "Tipo_Estadía": 'nan',
                "Estatus_Servicios": 'nan',
                "Estatus_Finanzas": 'nan',
                "Folio_Finanzas": 'nan',
                "Control_Estadía": 'nan',
                'Periodo': periodo,
                'TSU/ING': estadia,
                "formato_tres_opciones": {"estado": "activo", "archivo": None, "comentario": None},
                'permisos': ["update", "view"] # Campo de permisos para alumnos agregados a mano
            }).inserted_id
            
            flash('Alumno registrado exitosamente.', 'success')
            
            # Llamar a la función para asignar actividades al nuevo alumno
            asignar_actividades(nuevo_alumno_id)
            correo = session.get('correo')
            if correo:
                    administracion = db['administradores']
                    administracion.update_one(
                        {"correo": correo},
                        {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                            'movimientos': {
                                'tipo': 'Registro un Alumno Nuevo',
                                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                        }}
                    )
            flash('Alumno Registrado exitosamente.', 'success')
            return redirect(url_for('Vinculacion.Home'))
        
        else:
            flash('El alumno no se pudo registrar.', 'danger')
        
        return redirect(url_for('Vinculacion.Home'))