import bcrypt
from flask import Blueprint, current_app, render_template, request, url_for, redirect, flash, session
from app.functions.funciones import nocache, obtener_administrador_por_correo, obtener_alumno, obtener_documentos_alumno, obtener_documentos_alumno_uta, asignar_actividades, progreso_alumno
from datetime import datetime
from bson import Binary, ObjectId
import pandas as pd
SuperAdmmin_routes = Blueprint('SuperAdmin', __name__)




@SuperAdmmin_routes.route('/add', methods=['POST'])
def add_document():
    db = current_app.get_db_connection()
    administrador = request.form['administrador']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    confirmar_contraseña = request.form['confirmar_contraseña']
    departamento = request.form['departamento']
    hashpass = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

    if contraseña != confirmar_contraseña:
        error_messaje = 'Las contraseñas no coinciden.'
        return render_template('login.html', error_messaje=error_messaje)

    new_admin = {
        'administrador': administrador,
        'correo': correo,
        'contraseña': hashpass,
        'departamento': departamento,
        'en_linea':"",
        'ultima_conexion':"",
        'ultimo_movimiento':""
        
    }
    db['administradores'].insert_one(new_admin)
    
    #Esta parte es el "ultimo movimiento"
    if 'admin_id' in session:
        db['administradores'].update_one(
            {'_id': ObjectId(session['admin_id'])},
            {'$set': {'ultimo_movimiento': 'Agregó admin'}}
        )
    
    return redirect(url_for('SuperAdmin.home'))


@SuperAdmmin_routes.route('/edit/<id>', methods=['POST'])
def edit_document(id):
    db = current_app.get_db_connection()
    administrador = request.form['administrador']
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    departamento = request.form['departamento']

    
    updated_admin = {
        'administrador': administrador,
        'correo': correo,
        'contraseña': contraseña,
        'departamento': departamento,
        
    }
    db['administradores'].update_one({'_id': ObjectId(id)}, {'$set': updated_admin})
    
    #También esto es el "ultimo movimiento"
    if 'admin_id' in session:
        db['administradores'].update_one(
            {'_id': ObjectId(session['admin_id'])},
            {'$set': {'ultimo_movimiento': 'Editó admin'}}
        )
    
    return redirect(url_for('SuperAdmin.home'))

@SuperAdmmin_routes.route('/delete/<id>')
def delete_document(id):
    db = current_app.get_db_connection()
    db['administradores'].delete_one({'_id': ObjectId(id)})
    
    #Esto igual "ultimo movimiento"
    if 'admin_id' in session:
        db['administradores'].update_one(
            {'_id': ObjectId(session['admin_id'])},
            {'$set': {'ultimo_movimiento': 'Eliminó admin'}}
        )
    
    return redirect(url_for('SuperAdmin.home'))


@SuperAdmmin_routes.route('/monitoreo')
def monitoreo():
    db = current_app.get_db_connection()
    administradores = list(db['administradores'].find({}, {
        'administrador': 1,
        'departamento': 1,
        'en_linea': 1,
        'ultima_conexion': 1,
        'ultimo_movimiento': 1  
    }))
    return render_template('SuperAdmin/monitoreo.html', administradores=administradores)

@SuperAdmmin_routes.route('/home')
def home():
    db = current_app.get_db_connection()
    administradores = list(db['administradores'].find())
    return render_template('SuperAdmin/index.html', administradores=administradores)
