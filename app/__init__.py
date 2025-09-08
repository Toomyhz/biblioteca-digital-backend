from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import DevelopmentConfig
from flask_cors import CORS
from flask_session import Session
import redis
from sqlalchemy import create_engine
import os
from app.extensions.login import login_manager

db = SQLAlchemy()
migrate = Migrate()
server_session = Session()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    # Asegura carpeta de sesiones (solo si filesystem)
    if app.config.get("SESSION_TYPE") == "filesystem":
        os.makedirs(app.config.get("SESSION_FILE_DIR", "./sessions"), exist_ok=True)

    # Inicializa extensión de sesiones
    server_session.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Oracle
    tns = app.config.get("TNS_ADMIN")
    if tns:
        os.environ["TNS_ADMIN"] = tns

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
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,
        expose_headers=["Content-Type", "Authorization"],
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    @app.after_request
    def add_security_headers(response: Response):
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = True 
        response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
        return response

    from app.models.usuarios import Usuarios
    from app.models.libros import Libros
    from app.models.autores import Autores
    from app.models.carreras import Carreras

    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id:str):
        return Usuarios.query.get(int(user_id))

    return app






