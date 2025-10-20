# tests/test_setup.py

def test_app_configuracion(test_app):
    """Verifica que la app está configurada correctamente"""
    assert test_app.config['TESTING'] == True
    assert 'oracle' in test_app.config['SQLALCHEMY_DATABASE_URI'].lower()
    print("App configurada correctamente")


def test_db_connection(test_db):
    """Verifica conexión a Oracle"""
    from sqlalchemy import text
    result = test_db.session.execute(text("SELECT 1 FROM DUAL"))
    assert result.fetchone()[0] == 1
    print("Conexión a Oracle XE exitosa")


def test_crear_autor(test_db):
    """Verifica que podemos crear registros"""
    from app.models.autores import Autores

    autor = Autores(
        nombre_completo="Test Autor",
        nacionalidad="Chilena",
        slug_autor="test_autor"
    )
    test_db.session.add(autor)
    test_db.session.commit()

    assert autor.id_autor is not None
    print(f"Autor creado con ID: {autor.id_autor}")


def test_fixtures_funcionan(autor_fixture, carrera_fixture, libro_fixture):
    """Verifica que las fixtures funcionan"""
    assert autor_fixture.id_autor is not None
    assert carrera_fixture.id_carrera is not None
    assert libro_fixture.id_libro is not None

    print(f"Autor: {autor_fixture.nombre_completo}")
    print(f"Carrera: {carrera_fixture.nombre_carrera}")
    print(f"Libro: {libro_fixture.titulo}")


def test_api_endpoint_existe(client):
    """Verifica que los endpoints de Flask-RESTX funcionan"""
    response = client.get('/api/autores/')

    # No debe ser 404
    assert response.status_code != 404
    print(
        f"Endpoint /api/autores/ respondió con status {response.status_code}")
