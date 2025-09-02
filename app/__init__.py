from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import DevelopmentConfig
from flask_cors import CORS
from flask_session import Session
import redis
from sqlalchemy import create_engine
import os

db = SQLAlchemy()
migrate = Migrate()
session = Session()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    tns = app.config.get("TNS_ADMIN")
    if tns:
        os.environ["TNS_ADMIN"] = tns

    db.init_app(app)
    migrate.init_app(app, db)

    # Importación Blueprints
    from app.api.auth.routes import auth_bp
    from app.books.routes import book_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(book_bp, url_prefix='/api/books')
    
    CORS(app,origins=["http://localhost:5173"],supports_credentials=True)

    @app.after_request
    def add_security_headers(response: Response):
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = True 
        response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
        return response

    from app.models.user import User
    from app.models.role import Role
    from app.models.book import Book

    return app






