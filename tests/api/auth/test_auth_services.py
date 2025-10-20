from unittest.mock import MagicMock, patch
from urllib.parse import urlparse, parse_qs

import importlib
from app.api.auth import services


def test_build_google_auth_url(app):
    """
    Verificar que la URL de autenticación se construya correctamente y
    que se guarde el estado en Redis.
    """
    fake_redis = MagicMock()

    # Patch para interceptar la llamada a Redis
    with patch.object(services,"get_redis", return_value=fake_redis):
        with app.test_request_context("/"):
            app.config.update({
                "GOOGLE_CLIENT_ID": "fake-client-id",
                "GOOGLE_CLIENT_SECRET": "fake-client-secret",
                "OAUTH_REDIRECT_URI": "http://localhost/callback",
                "ALLOWED_EMAIL_DOMAINS": "universidad.cl"
            })
            auth_url = services._build_google_auth_url()
            assert "accounts.google.com" in auth_url
            assert "client_id=fake-client-id" in auth_url
            fake_redis.setex.assert_called_once()

def test_exchange_code_for_tokens(app):
    fake_response = MagicMock()
    fake_response.json.return_value = {"access_token":"abc", "id_token":"xyz"}

    with app.app_context():
        app.config.update({
            "GOOGLE_CLIENT_ID":"fake",
            "GOOGLE_CLIENT_SECRET":"fake",
            "OAUTH_REDIRECT_URI":"http://localhost/callback"
        })

        with patch("app.api.auth.services.requests.post",return_value=fake_response) as mock_post:
            tokens = services._exchange_code_for_tokens("fake-code")
            assert tokens["access_token"] == "abc"
            assert tokens["id_token"] == "xyz"
            mock_post.assert_called_once()

def test_verify_id_token(app):
    fake_claims = {
        "email":"user@universidad.cl",
        "hd":"universidad.cl",
        "name":" Usuario Prueba"
    }
    with app.app_context():
        app.config.update({"GOOGLE_CLIENT_ID":"fake-client-id"})

        with patch("app.api.auth.services.id_token.verify_oauth2_token",return_value=fake_claims):
            claims = services._verify_id_token("fase-id_token")
            assert claims["email"] == "user@universidad.cl"
            assert claims["hd"] == "universidad.cl"


def test_require_domains_with_correct_domain(app):
    app.config["ALLOWED_EMAIL_DOMAINS"] = "umce.cl"
    email_input="tomas.hernandez@umce.cl"
    with app.app_context():
        email_correcto = services._require_domain(email_input)
        assert email_correcto == True

def test_require_domains_with_invalid_domain(app):
    app.config["ALLOWED_EMAIL_DOMAINS"] = "umce.cl"
    email_input="tomas.hernandez@duocuc.cl"
    with app.app_context():
        email_correcto = services._require_domain(email_input)
        assert email_correcto == False


def test_get_reddis_lazy_initialization(monkeypatch):
        # Esto restaura la función original para poder probar su lógica interna.
    importlib.reload(services)
    monkeypatch.setattr(services,"myredis",None)
    fake_redis_client = MagicMock()
    with patch("app.api.auth.services.os.getenv", return_value="redis://fakeurl") as mock_getenv,\
         patch("app.api.auth.services.redis.from_url",return_value=fake_redis_client) as mock_from_url:
        
        redis_instance_1 = services.get_redis()

        mock_getenv.assert_called_once_with("REDIS_URL")
        mock_from_url.assert_called_once_with("redis://fakeurl")
        assert redis_instance_1 == fake_redis_client

        redis_instance_2 = services.get_redis()

        # Verificar que los mocks NO fueron llamados una segunda vez.
        mock_getenv.assert_called_once()
        mock_from_url.assert_called_once()
        # Y que devuelve la misma instancia ya creada.
        assert redis_instance_2 is redis_instance_1