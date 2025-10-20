from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_session import Session
from flask_restx import Api
from flask_redis import FlaskRedis

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
server_session = Session
api_new = Api(
    version="1.0",
    title="Biblioteca Digital - API",
    description="Api para gestión y administración de la Biblioteca Digital",
    doc="/docs"
)

redis_client = FlaskRedis()