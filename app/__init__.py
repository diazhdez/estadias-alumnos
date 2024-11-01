from flask import Flask, g
from pymongo import MongoClient
from config import Config
import certifi


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuración de la conexión a la base de datos usando la URL
    ca = certifi.where()

    def get_db_connection():
        if 'db' not in g:
            try:
                client = MongoClient(Config.MONGO_URI, tlsCAFile=ca)
                g.db = client["Universidad_Estadias"]
            except Exception as e:
                print(f"Error de conexión con la base de datos: {e}")
                g.db = None
        return g.db

    @app.teardown_appcontext
    def close_db_connection(exception):
        db = g.pop('db', None)
        if db is not None:
            try:
                client = db.client  # Obtener el cliente de MongoDB desde la conexión
                client.close()
            except Exception as e:
                print(f"Error al cerrar la conexión con la base de datos: {e}")

    app.get_db_connection = get_db_connection

    with app.app_context():
        # Importa y registra los Blueprints
        from app.routes.main import main_routes
        from app.routes.session import session_routes
        from app.routes.alumno import alumno_routes
        from app.routes.update import update_routes
        from app.routes.view import view_routes
        from app.routes.errors import errors
        from app.routes.vinculacion import Vinculacion_routes
        from app.routes.create_vinculacion import create_vinculacion_routes

        app.register_blueprint(main_routes)
        app.register_blueprint(session_routes)
        app.register_blueprint(alumno_routes)
        app.register_blueprint(update_routes)

        app.register_blueprint(view_routes)
        app.register_blueprint(errors)
        app.register_blueprint(Vinculacion_routes)
        app.register_blueprint(create_vinculacion_routes)
    return app
