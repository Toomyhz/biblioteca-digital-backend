from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import DevelopmentConfig
from flask_cors import CORS


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)

    # Importación Blueprints
    from app.auth.routes import auth_bp
    from app.api.libros.routes import libro_bp
    from app.api.autores.routes import autor_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(libro_bp, url_prefix='/api/libros')
    app.register_blueprint(autor_bp, url_prefix='/api/autores')
    
    CORS(app,origins=["http://localhost:5173"],supports_credentials=True)

    @app.after_request
    def add_security_headers(response: Response):
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = True 
        response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
        return response

    from app.models.usuarios import Usuarios
    from app.models.roles import Rol
    from app.models.carreras import Carreras
    from app.models.autores import Autores
    from app.models.libros import Libro

    return app






