from flask import Flask, current_app, g
import pymongo
from config import Config

from flask_wtf.csrf import CSRFProtect
import certifi




def create_app():
    # Inicializar la aplicación Flask
    app = Flask(__name__)
    
    # Configurar la aplicación con la configuración definida en Config
    app.config.from_object(Config)
    
    # Configurar la protección CSRF
    csrf = CSRFProtect(app)

    # Registrar el blueprint de notificaciones
    

    # Establecer la clave secreta para la sesión
    app.secret_key = 'M0i1Xc$GfPw3Yz@2SbQ9lKpA5rJhDtE7'

    # Configuración de la conexión a la base de datos MongoDB usando la URL
    ca = certifi.where()

    def get_db_connection():
        """Función para obtener la conexión a la base de datos MongoDB"""
        if 'db' not in g:
            client = pymongo.MongoClient(current_app.config['MONGO_URI'])
            g.db = client[current_app.config['DATABASE_NAME']]
        return g.db

    @app.teardown_appcontext
    def close_db_connection(exception):
        """Cerrar la conexión a la base de datos al finalizar la solicitud"""
        db = g.pop('db', None)
        if db is not None:
            try:
                client = db.client  # Obtener el cliente de MongoDB desde la conexión
                client.close()
            except Exception as e:
                print(f"Error al cerrar la conexión con la base de datos: {e}")

    # Adjuntar la función de obtener conexión a la base de datos a la app
    app.get_db_connection = get_db_connection

    # Registrar los Blueprints
    with app.app_context():
        # Importar las rutas (BluePrints)
        from app.routes.main import main_routes
        from app.routes.recuperacion import recuperacion_routes
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
        from app.routes.notificaciones import bp  

        # Registrar todos los blueprints
        app.register_blueprint(bp)
        app.register_blueprint(main_routes)
        app.register_blueprint(recuperacion_routes)
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
