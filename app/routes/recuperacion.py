from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import secrets
import smtplib
from urllib import request
import bcrypt
from bson import Binary, ObjectId
from flask import Blueprint, current_app, render_template, redirect, url_for, flash, session, request
from itsdangerous import URLSafeTimedSerializer

from app.functions.funciones import nocache, obtener_usuario_por_correo
from app.functions.utils import requiere_permisos


recuperacion_routes = Blueprint('recuperacion', __name__)

# Configuración del correo con smtplib
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL = 'contact.quarium@gmail.com'
PASSWORD = 'otjt nkts nczg qcxw'

serializer = URLSafeTimedSerializer("secreto_super_seguro")  # Genera tokens seguros

@recuperacion_routes.route("/recuperar_contraseña/", methods=["POST"])
def recuperar():
    db = current_app.get_db_connection()
    email = request.form['email'].strip().lower()
    usuario = db["Alumnos"]
    email_encontrado = usuario.find_one({"Correo_Institucional": email})

    if email_encontrado:
        token = secrets.token_hex(16)  # Token aleatorio seguro
        db['recuperaciones'].insert_one({
            "usuario_email": email,
            "token": token,
            "expira": datetime.now().timestamp() + 3600  # Expira en 1 hora
        })
        enlace = url_for("recuperacion.restablecer", token=token, _external=True)

        # Cargar el contenido del archivo HTML
        template_file = os.path.join('app', 'templates', 'correo_aceptacion.html')
        with open(template_file, 'r') as file:
            html_content = file.read()

        # Reemplazar el enlace en el contenido HTML
        html_content = html_content.replace("{{ enlace }}", enlace)

        # Crear el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL
        mensaje['To'] = email
        mensaje['Subject'] = 'Recuperación de contraseña'

        # Adjuntar el contenido HTML al mensaje
        mensaje.attach(MIMEText(html_content, 'html'))

        try:
            # Enviar el correo usando smtplib
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL, PASSWORD)
                server.sendmail(EMAIL, email, mensaje.as_string())
                flash(f'Correo enviado correctamente a {email}', 'success')

            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'Error al enviar el correo: {str(e)}', 'danger')
            return redirect(url_for('main.index'))

    else:
        flash('El correo no está registrado', 'danger')
        return redirect(url_for('main.index'))


# Ruta para el restablecimiento (solo ejemplo)
@recuperacion_routes.route("/restablecer/<token>", methods=["GET", "POST"])
@nocache
def restablecer(token):
    db = current_app.get_db_connection()

    email_user = db['recuperaciones']
    email_data = email_user.find_one({"token": token})
    usuario_cambiar = email_data.get("usuario_email")
    usuario = obtener_usuario_por_correo(usuario_cambiar)
    
    if usuario:
        
        # Verificar si el token ha expirado
        if email_data['expira'] < datetime.now().timestamp():
            flash('El enlace ha expirado o es inválido.', 'danger')
            return redirect(url_for('main.index'))  # O redirigir a otra página de error

        if request.method == "POST":
            nueva_contraseña = request.form["nueva_contraseña"]
            hashpass = bcrypt.hashpw(nueva_contraseña.encode('utf-8'), bcrypt.gensalt())
            # Actualizar la contraseña del usuario
            db['Alumnos'].update_one(
                {'_id': ObjectId(usuario['_id'])},  # Filtro
                {'$set': {'Contraseña': hashpass}}  # Actualización
            )
            flash('Contraseña actualizada con éxito', 'success')
            print("Hash de la nueva contraseña:", ObjectId(usuario['_id']))
            print("Hash de la nueva contraseña:", hashpass)
            return redirect(url_for('main.index'))

        else:
            return render_template("cambio_psswd.html", token=token)

    else:
        flash('El enlace es inválido o ha expirado.', 'danger')
        return redirect(url_for('main.index'))
