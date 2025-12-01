from dotenv import load_dotenv
import os, secrets
import redis

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    REDIRECT_URI = os.getenv("redirect_uri")
    TOKEN_URL = os.getenv("TOKEN_URL")
    PDF_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'libros_pdf')
    PORTADA_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'libros_portada')
    
    # DigitalOcean
    DO_SPACES_ENDPOINT=os.getenv("DO_SPACES_ENDPOINT")
    DO_SPACES_REGION=os.getenv("DO_SPACES_REGION")
    DO_SPACES_BUCKET=os.getenv("DO_SPACES_BUCKET")
    DO_SPACES_KEY=os.getenv("DO_SPACES_KEY")
    DO_SPACES_SECRET=os.getenv("DO_SPACES_SECRET")


class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

    # Configuración de Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
    ALLOWED_EMAIL_DOMAINS = os.getenv("ALLOWED_EMAIL_DOMAINS")

    # Configuración MySQL
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = os.getenv("MYSQL_PORT")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")

    SQLALCHEMY_DATABASE_URI_MYSQL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_MYSQL

    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,        
    "pool_recycle": 1800,         
    "pool_size": 5,              
    "max_overflow": 10,         
    }


    # Sesiones, revisar
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(os.getenv("REDIS_URL"))
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'sess:'  # opcional

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # True en producción bajo HTTPS
    PERMANENT_SESSION_LIFETIME = 7200  # Ajustado a 2 horas
    SESSION_REFRESH_EACH_REQUEST = False

    # Configuracion Redis (Se está utilizando el mismo espacio para las sesiones).
    REDIS_URL=os.getenv("REDIS_URL")

    FRONT_URL=os.getenv("FRONTEND_URL")


    
    
class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    SECRET_KEY = "clave_secreta_para_test"
    WTF_CSRF_ENABLED = False 
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False 
    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_REFRESH_EACH_REQUEST = False

    # --- 4. ARREGLO DE OAUTH (Valores Falsos) ---
    GOOGLE_CLIENT_ID = "dummy_client_id"
    GOOGLE_CLIENT_SECRET = "dummy_client_secret"
    OAUTH_REDIRECT_URI = "http://localhost:5000/callback"
    ALLOWED_EMAIL_DOMAINS = "umce.cl"

    LOGIN_DISABLED = False  
    FRONT_URL="http://localhost:5173"

