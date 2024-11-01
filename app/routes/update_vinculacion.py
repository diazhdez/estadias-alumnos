from flask import Blueprint, current_app, flash, redirect, session, url_for, request
from app.functions.funciones import subir_documento
from bson import Binary, ObjectId

update_vinculacion_routes = Blueprint('update_vinculacion', __name__)

