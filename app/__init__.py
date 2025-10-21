import os
from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate, login_manager, server_session, api_new, redis_client


def create_app(config_class=None, testing: bool = False):
    app = Flask(__name__)
    
    # Configuración
    if testing:
        from app.config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        config_class = config_class or os.getenv("FLASK_CONFIG", "app.config.DevelopmentConfig")
        app.config.from_object(config_class)
    
    # Inicializar extensiones
    server_session(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    api_new.init_app(app)
    redis_client.init_app(app)

    # Configuración Oracle
    tns = app.config.get("TNS_ADMIN")
    if tns:
        os.environ["TNS_ADMIN"] = tns

    # Conexión DB en desarrollo
    if not app.config.get("TESTING", False):
        with app.app_context():
            from sqlalchemy import text
            try:
                db.session.execute(text("SELECT 1 FROM dual"))
            except Exception as e:
                app.logger.error(f"Error al conectar a Oracle: {e}")
                raise
    else:
        # Crear tablas para tests automáticamente
        with app.app_context():
            db.create_all()
    
    # Registrar Namespaces
    from app.api.libros.routes import libros_sn
    from app.api.autores.routes import autores_sn
    from app.api.carreras.routes import carreras_sn
    from app.api.auth.routes import auth_ns
    from app.api.lector.routes import lector_ns
    from app.api.biblioteca.routes import biblioteca_ns

    api_new.add_namespace(libros_sn, path='/api/libros')
    api_new.add_namespace(autores_sn, path='/api/autores')
    api_new.add_namespace(carreras_sn, path='/api/carreras')
    api_new.add_namespace(auth_ns, path="/api/auth")
    api_new.add_namespace(lector_ns, path="/api/lector")
    api_new.add_namespace(biblioteca_ns, path="/api/biblioteca")

    # CORS
    CORS(
        app,
        origins=[app.config.get("FRONTEND_URL", "http://localhost:5173")],
        supports_credentials=True
    )
    
    from app.models.usuarios import Usuarios
    
    return app
