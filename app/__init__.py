from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_cors import CORS
from flask_session import Session
from sqlalchemy import create_engine
import os
from app.extensions.login import login_manager

db = SQLAlchemy()
migrate = Migrate()
server_session = Session()

config_name = os.getenv("FLASK_ENV", "development")

if config_name == "production":
    from app.config import ProductionConfig
    ConfigClass = ProductionConfig
elif config_name == "testing":
    from app.config import TestingConfig
    ConfigClass = TestingConfig
else:
    from app.config import DevelopmentConfig
    ConfigClass = DevelopmentConfig

def create_app():
    app = Flask(__name__)
    app.config.from_object(ConfigClass)

    # Inicializa extensión de sesiones
    server_session.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Oracle
    tns = app.config.get("TNS_ADMIN")
    if tns:
        os.environ["TNS_ADMIN"] = tns

    # Verificación de DB al iniciar
    from sqlalchemy import text
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1 FROM dual"))
            app.logger.info("Conexión a Oracle verificada")
        except Exception as e:
            app.logger.error(f"Error al conectar a Oracle: {e}")
            raise

    # Importación Blueprints
    from app.api.libros.routes import libro_bp
    from app.api.autores.routes import autor_bp
    from app.api.auth.routes import auth_bp
    from app.api.carreras.routes import carrera_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(libro_bp, url_prefix='/api/libros')
    app.register_blueprint(autor_bp, url_prefix='/api/autores')
    app.register_blueprint(carrera_bp, url_prefix='/api/carreras')
    
    # CORS
    CORS(
    app,
    origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    supports_credentials=True
)

    from app.models.usuarios import Usuarios
    from app.models.libros import Libros
    from app.models.autores import Autores
    from app.models.carreras import Carreras

    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id:str):
        return Usuarios.query.get(int(user_id))
    

    return app






