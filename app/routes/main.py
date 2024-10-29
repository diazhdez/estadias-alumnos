from flask import Blueprint, render_template
from app.functions.funciones import nocache

main_routes = Blueprint('main', __name__)


@main_routes.route('/')
@nocache
def index():
    return render_template('login.html')
