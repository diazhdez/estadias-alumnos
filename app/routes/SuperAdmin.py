import bcrypt
from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
from app.functions.funciones import nocache, obtener_administrador_por_correo, obtener_alumno, obtener_documentos_alumno, obtener_documentos_alumno_uta, asignar_actividades, progreso_alumno
from datetime import datetime
from bson import Binary, ObjectId
import pandas as pd
from app.functions.utils import requiere_permisos
SuperAdmmin_routes = Blueprint('SuperAdmin', __name__)




@SuperAdmmin_routes.route('/Edulink/SuperAdmin/add', methods=['POST'])
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete"], departamento_requerido="Root")
def add_admin():
    db = current_app.get_db_connection()
    administrador = request.form['administrador']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    confirmar_contraseña = request.form['confirmar_contraseña']
    departamento = request.form['departamento']
    permisos = request.form.getlist('permisos')
    hashpass = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

    if contraseña != confirmar_contraseña:
        flash('Contraseñas no coinciden.', 'danger')
        return redirect(url_for('SuperAdmin.home'))

    new_admin = {
        'administrador': administrador,
        'correo': correo,
        'contraseña': hashpass,
        'departamento': departamento,
        'en_linea':False,
        'ultima_conexion': None,  # Utiliza None para representar la ausencia de datos
        'movimientos': [  # Arreglo para registrar múltiples movimientos
        {
            'tipo': 'Creación de cuenta',
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ],
        'permisos' : permisos   
    }
    db['administradores'].insert_one(new_admin)
    
    #Esta parte es el "ultimo movimiento"
    correo = session.get('correo')
    if correo:
        administracion = db['administradores']
        administracion.update_one(
            {"correo": correo},
            {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                'movimientos': {
                    'tipo': 'Agrego a un administrador',
                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }}
        )
    
    return redirect(url_for('SuperAdmin.home'))


@SuperAdmmin_routes.route('/Edulink/SuperAdmin/edit/', methods=['POST'])
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete"], departamento_requerido="Root")
def edit_document():
    db = current_app.get_db_connection()
    adminId = request.form['idAdmin']
    administrador = request.form['administrador']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
   
    updated_admin = {
        'administrador': administrador,
        'correo': correo,
        'contraseña': contraseña,
        
    }
    db['administradores'].update_one({'_id': ObjectId(adminId)}, {'$set': updated_admin})
    
    #También esto es el "ultimo movimiento"
    correo = session.get('correo')
    if correo:
        administracion = db['administradores']
        administracion.update_one(
            {"correo": correo},
            {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                'movimientos': {
                    'tipo': 'Edito a un administrador',
                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }}
        )
    flash('Información del administrador editada exitosamente.', 'success')
    return redirect(url_for('SuperAdmin.home'))

@SuperAdmmin_routes.route('/Edulink/SuperAdmin/Delete',methods=['POST'])
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete"], departamento_requerido="Root")
def delete_Admin():
    db = current_app.get_db_connection()
    id = session.get('_id')
    adminId = request.form['idAdmin']
    db['administradores'].delete_one({'_id': ObjectId(adminId)})
    
    #Esto igual "ultimo movimiento"
    correo = session.get('correo')
    if correo:
        administracion = db['administradores']
        administracion.update_one(
            {"correo": correo},
            {'$push': {  # Usa $push para agregar un nuevo movimiento al arreglo
                'movimientos': {
                    'tipo': 'Elimino a un administrador',
                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }}
        )
    flash('Administrador eliminado exitosamente.', 'success')
    return redirect(url_for('SuperAdmin.home'))



@SuperAdmmin_routes.route('/Edulink/SuperAdmin/home')
@nocache
@requiere_permisos(permisos_requeridos=["create", "delete"], departamento_requerido="Root")
def home():
    db = current_app.get_db_connection()
    correo = session.get('correo')
    admin = obtener_administrador_por_correo(correo)
    administradores = list(db['administradores'].find())
    return render_template('SuperAdmin/index.html', administradores=administradores, administrador=admin)
