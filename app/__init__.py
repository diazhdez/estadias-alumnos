from flask import Flask, current_app, g
import pymongo
from config import Config
import certifi


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuración de la conexión a la base de datos usando la URL
    ca = certifi.where()

    def get_db_connection():
        if 'db' not in g:
            client = pymongo.MongoClient(current_app.config['MONGO_URI'])
            g.db = client[current_app.config['DATABASE_NAME']]
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
        from app.routes.update_vinculacion import update_vinculacion_routes
        from app.routes.Servicios import Servicios_routes
        from app.routes.Biblioteca import Biblioteca_routes
        from app.routes.Finanzas import Finanzas_routes
        from app.routes.Juridico import Juridico_routes
        from app.routes.Recursos import Recursos_routes
        from app.routes.SuperAdmin import SuperAdmmin_routes


        app.register_blueprint(main_routes)
        app.register_blueprint(session_routes)
        app.register_blueprint(alumno_routes)
        app.register_blueprint(update_routes)
        app.register_blueprint(update_vinculacion_routes)
        app.register_blueprint(view_routes)
        app.register_blueprint(errors)
        app.register_blueprint(Vinculacion_routes)
        app.register_blueprint(create_vinculacion_routes)
        app.register_blueprint(Servicios_routes)
        app.register_blueprint(Biblioteca_routes)
        app.register_blueprint(Finanzas_routes)
        app.register_blueprint(Juridico_routes)
        app.register_blueprint(Recursos_routes)
        app.register_blueprint(SuperAdmmin_routes)
        
    return app
