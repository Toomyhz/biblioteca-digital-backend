from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("redirect_uri")
    TOKEN_URL = os.getenv("TOKEN_URL")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'libros_pdf')

class DevelopmentConfig(Config):
    DEBUG = True

    # Configuración de Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")

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




class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_ECHO = True

