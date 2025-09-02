from flask.cli import FlaskGroup
from flask_migrate import Migrate
from app import create_app, db

# Crear la aplicación Flask
app = create_app()

# Registrar Migraciones
migrate = Migrate(app, db)

# Exponer CLI
cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()