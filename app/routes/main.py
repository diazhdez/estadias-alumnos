from datetime import datetime

from bson import ObjectId
from flask import Blueprint, Request, current_app, jsonify, redirect, render_template, request, session, url_for
from app.functions.funciones import nocache

main_routes = Blueprint('main', __name__)


@main_routes.route('/')
@nocache
def index():
    return render_template('login.html')

from flask import flash

@main_routes.route("/aceptar_terminos", methods=["POST"])
def aceptar_terminos():
    db = current_app.get_db_connection()
    redirect_view = request.args.get('redirect_view')
    usuario_id = request.form.get("usuario_id")
    id = ObjectId(usuario_id)
    
    if not usuario_id:
        flash("Usuario no autenticado", "error")
        return jsonify({"mensaje": "Usuario no autenticado"}), 401  # Solo devuelve un mensaje y un código de error
    
    if not db["aceptacion_terminos"].find_one({"usuario_id": id}):
        db["aceptacion_terminos"].insert_one({
            "usuario_id": id,
            "fecha_aceptacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        flash("Términos y condiciones aceptados exitosamente.", "success")
        return redirect(url_for(redirect_view))
    else:
        flash("Ya habías aceptado los términos anteriormente.", "info")
        return redirect(url_for(redirect_view))

@main_routes.route("/cambio/")
def combio_psswd():
    return render_template("cambio_psswd.html")