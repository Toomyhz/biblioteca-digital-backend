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


class ProductionConfig(Config):
    DEBUG = False
    # Aquí puedes agregar configuraciones específicas para producción
    # Por ejemplo, configuración de base de datos diferente, etc.
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'sessions')
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'sess:'  # opcional

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = True  # Asegúrate de usar HTTPS en producción
    PERMANENT_SESSION_LIFETIME = 7200  # Ajustado a 2 horas


class DevelopmentConfig(Config):
    DEBUG = True

    # Configuración de Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
    ALLOWED_EMAIL_DOMAINS = os.getenv("ALLOWED_EMAIL_DOMAINS")

    #Ruta Wallet
    TNS_ADMIN = os.getenv("TNS_ADMIN")

    # Alias de la base de datos
    DB_ALIAS = os.getenv("DB_ALIAS")

    # Usuario y contraseña oracle
    USER_ORACLE = os.getenv("USER_ORACLE")
    PW_ORACLE = os.getenv("PW_ORACLE")

    WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

    SQLALCHEMY_DATABASE_URI = (
    f"oracle+oracledb://{USER_ORACLE}:{PW_ORACLE}@{DB_ALIAS}"
    f"?config_dir={TNS_ADMIN}&wallet_location={TNS_ADMIN}"
    + (f"&wallet_password={WALLET_PASSWORD}" if WALLET_PASSWORD else "")
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,       # Verifica la conexión antes de usarla
    "pool_recycle": 1800,        # Recicla conexiones cada 30 min (ajústalo al timeout de Oracle)
    "pool_size": 5,              # Número de conexiones activas
    "max_overflow": 10,          # Conexiones extra si hay carga alta
}
    # Sesiones, revisar
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(os.getenv("REDIS_URL"))
    # SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'sessions')
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'sess:'  # opcional

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # True en producción bajo HTTPS
    PERMANENT_SESSION_LIFETIME = 7200  # Ajustado a 2 horas

    
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_ECHO = True

