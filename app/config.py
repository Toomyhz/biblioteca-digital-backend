class Config:
    SQLARCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "BibliotecaDigital_Umce_2025."
    GOOGLE_CLIENT_ID = "1069979014769-6rp1isa3hqb50188pbjhmrd0gm3093q0.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "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"

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_ECHO = True
