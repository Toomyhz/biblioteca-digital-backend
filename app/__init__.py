from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from .config import DevelopmentConfig
from flask_cors import CORS
# Importación Blueprints
from app.auth.routes import auth_bp

db = SQLAlchemy()
app = Flask(__name__)
@app.after_request
def add_security_headers(response: Response):
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    return response
app.config.from_object(DevelopmentConfig)
app.register_blueprint(auth_bp, url_prefix='/api/auth')

CORS(app,origins=["http://localhost:5173"])