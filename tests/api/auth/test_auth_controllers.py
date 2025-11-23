import time
from unittest.mock import MagicMock, patch
from app.api.auth.controllers import manejar_callback, STATE_EXPIRATION_SECONDS
from flask import redirect



mock_user = MagicMock()
mock_user.id = 1
mock_user.email = "test@umce.cl"
def test_manejar_callback_exitoso(app):
    """
    Test del "camino feliz": Un usuario se autentica correctamente.
    """
    current_time = int(time.time())
    state = "test_state_123"
    nonce = "test_nonce_123"

    # Se mockean todas las dependencias externas
    with patch('app.api.auth.controllers.redis_client') as mock_redis, \
         patch('app.api.auth.controllers._exchange_code_for_tokens') as mock_exchange, \
         patch('app.api.auth.controllers._verify_id_token') as mock_verify, \
         patch('app.api.auth.controllers._require_domain', return_value=True) as mock_domain, \
         patch('app.api.auth.controllers.buscar_o_crear_usuario', return_value=mock_user) as mock_db_user, \
         patch('app.api.auth.controllers.login_user') as mock_login, \
         patch('app.api.auth.controllers.oauth_ok') as mock_oauth_ok:
        
        # 1. Configurar los mocks
        # Redis devuelve el nonce y el timestamp
        mock_redis.get.return_value= f"{nonce}:{current_time}".encode("utf-8")
        # El intercambio de código devuelve el token
        mock_exchange.return_value = {"id_token":"fake_id_token"}
        # La verificación del token devuelve los claims (datos del usuario)
        mock_verify.return_value = {"nonce":nonce, "email":"test@umce.cl", "email_verified": True}

        # 2. Ejecutar la función dentro del contexto de una petición
        with app.test_request_context(f"/callback?state={state}&code=test_code"):
            from flask import request
            manejar_callback(request)
        # 3. Verificar que todo se llamó como se esperaba
        mock_redis.get.assert_called_once_with(f"oauth:{state}")
        mock_exchange.assert_called_once_with("test_code")
        mock_verify.assert_called_once_with("fake_id_token")
        mock_domain.assert_called_once_with("test@umce.cl")
        mock_db_user.assert_called_once()
        mock_login.assert_called_once_with(mock_user, remember=False)
        mock_redis.delete.assert_called_once_with(f"oauth:{state}")
        mock_oauth_ok.assert_called_once()

def test_manejar_callback_state_invalido(app):
    """
    Test de Fallo: El "state" no se encuentra en Redis.
    """
    with patch("app.api.auth.controllers.redis_client") as mock_redis, \
        patch("app.api.auth.controllers.oauth") as mock_oauth:

        # Redis no encuentra la clave.
        mock_redis.get.return_value = None
        with app.test_request_context("/callback?state=bad_state&code=test_code"):
            from flask import request
            manejar_callback(request)
        
        # Verificar que se retorna el error correcto
        mock_oauth.assert_called_once_with("invalid_state")

def test_manejar_callback_formato_state_invalido(app,mocker):
    """
    Test de Fallo: El formato de "state" es invalido.
    """
    mock_redis = mocker.patch("app.api.auth.controllers.redis_client")
    mock_redis.get.return_value = b"valor-mal-formado"

    mock_oauth_helper = mocker.patch('app.api.auth.controllers.oauth', return_value=redirect('/login?auth_error=invalid_state_format'))

    class MockRequest:
        args = {
            "state": "un_estado_valido", "code": "un_codigo"
        }
    response = manejar_callback(MockRequest)
        
    mock_redis.get.assert_called_once_with("oauth:un_estado_valido")
    mock_oauth_helper.assert_called_once_with('invalid_state_format')

    assert response.status_code == 302
    assert 'auth_error=invalid_state_format' in response.location

def test_manejar_callback_tiempo_expirado(mocker):
    """
    Test de Fallo: El tiempo de espera fue expirado.
    """
    timestamp_antiguo = int(time.time()) - (STATE_EXPIRATION_SECONDS + 60)

    mock_redis = mocker.patch("app.api.auth.controllers.redis_client")
    valor_expirado = f"un_nonce_valido:{timestamp_antiguo}".encode()
    mock_redis.get.return_value = valor_expirado

    mock_oauth_helper = mocker.patch('app.api.auth.controllers.oauth', return_value=redirect('/login?auth_error=expired_state'))

    class MockRequest:
        args = {
            "state": "un_estado_expirado", "code": "un_codigo"
        }
    response = manejar_callback(MockRequest)
        
    mock_redis.get.assert_called_once_with("oauth:un_estado_expirado")
    mock_oauth_helper.assert_called_once_with('expired_state')

    assert response.status_code == 302
    assert 'auth_error=expired_state' in response.location

def test_manejar_callback_falla_intercambio_tokens(mocker):
    """
    Test de Fallo: Error al intercambiar tokens.
    """
    timestamp = int(time.time())
    mock_redis = mocker.patch("app.api.auth.controllers.redis_client")

    valor_valido = f"un_nonce_valido:{timestamp}".encode()
    mock_redis.get.return_value = valor_valido

    mock_exchange = mocker.patch('app.api.auth.controllers._exchange_code_for_tokens')
    mock_exchange.side_effect = Exception("Fallo de red simulado")

    mock_oauth_helper = mocker.patch('app.api.auth.controllers.oauth', return_value=redirect('/login?auth_error=token_exchange_failed'))

    class MockRequest:
        args = {
            "state": "un_estado_valido", "code": "un_codigo"
        }
    response = manejar_callback(MockRequest)

    mock_exchange.assert_called_once()

    mock_oauth_helper.assert_called_once_with('token_exchange_failed')

    assert response.status_code == 302
    assert 'auth_error=token_exchange_failed' in response.location

def test_manejar_callback_falla_validacion_nonce(mocker):
    """
    Test de Fallo: Error al validar nonce.
    """
    timestamp = int(time.time())
    nonce_guardado_en_redis = "nonce_correcto"
    mock_redis = mocker.patch("app.api.auth.controllers.redis_client")
    valor_valido = f"{nonce_guardado_en_redis}:{timestamp}".encode()
    mock_redis.get.return_value = valor_valido


    mocker.patch('app.api.auth.controllers._exchange_code_for_tokens',return_value={"id_token":"fake_token"})
    
    claims_con_nonce_incorrecto = {
        'email': 'test@umce.cl',
        'name': 'Test User',
        'nonce': 'nonce_INCORRECTO', # <-- Este es el error forzado
        'email_verified': True
    }

    mocker.patch('app.api.auth.controllers._verify_id_token',return_value=claims_con_nonce_incorrecto)

    mock_oauth_helper = mocker.patch('app.api.auth.controllers.oauth', return_value=redirect('/login?auth_error=invalid_nonce'))

    class MockRequest:
        args = {
            "state": "un_estado_valido", "code": "un_codigo"
        }
    response = manejar_callback(MockRequest)


    mock_oauth_helper.assert_called_once_with('invalid_nonce')

    assert response.status_code == 302
    assert 'auth_error=invalid_nonce' in response.location

def test_manejar_callback_con_email_no_verificado(mocker):
    timestamp = int(time.time())
    mock_redis = mocker.patch("app.api.auth.controllers.redis_client")
    valor_valido = f"test_nonce:{timestamp}".encode()
    mock_redis.get.return_value = valor_valido

    mocker.patch('app.api.auth.controllers._exchange_code_for_tokens',return_value={"id_token":"fake_token"})

    claims_no_verificados = {
        'email': 'test@umce.cl',
        'name': 'Test User',
        'nonce': 'test_nonce',
        'email_verified': False 
    }

    mocker.patch('app.api.auth.controllers._verify_id_token', return_value=claims_no_verificados)
    # 3. Mockeamos el helper de error.
    mock_oauth_helper = mocker.patch('app.api.auth.controllers.oauth', return_value=redirect('/login?auth_error=email_unverified_or_invalid_domain'))

    class MockRequest:
        args = {'state': 'test_state', 'code': 'test_code'}

    response = manejar_callback(MockRequest())

    mock_oauth_helper.assert_called_once_with('email_unverified_or_invalid_domain')
    assert response.status_code == 302
    assert 'auth_error=email_unverified_or_invalid_domain' in response.location


def test_manejar_callback_con_dominio_invalido(mocker):
    timestamp = int(time.time())
    mock_redis = mocker.patch("app.api.auth.controllers.redis_client")
    valor_valido = f"test_nonce:{timestamp}".encode()
    mock_redis.get.return_value = valor_valido

    mocker.patch('app.api.auth.controllers._exchange_code_for_tokens',return_value={"id_token":"fake_token"})

    claims_verificados = {
        'email': 'test@dominio-incorrecto.com',
        'name': 'Test User',
        'nonce': 'test_nonce',
        'email_verified': True 
    }

    mocker.patch('app.api.auth.controllers._verify_id_token', return_value=claims_verificados)


    mock_require_domain = mocker.patch('app.api.auth.controllers._require_domain', return_value=False)
    # 3. Mockeamos el helper de error.
    mock_oauth_helper = mocker.patch('app.api.auth.controllers.oauth', return_value=redirect('/login?auth_error=email_unverified_or_invalid_domain'))

    class MockRequest:
        args = {'state': 'test_state', 'code': 'test_code'}

    response = manejar_callback(MockRequest())

    # Se llamó a la función para validar dominio
    mock_require_domain.assert_called_once_with("test@dominio-incorrecto.com")

    # Se llamo al helperde error con el código correcto
    mock_oauth_helper.assert_called_once_with('email_unverified_or_invalid_domain')
    assert response.status_code == 302
    assert 'auth_error=email_unverified_or_invalid_domain' in response.location

def test_manejar_callback_con_error_crear_o_buscar_usuario(mocker):
    timestamp = int(time.time())
    mock_redis = mocker.patch("app.api.auth.controllers.redis_client")
    valor_valido = f"test_nonce:{timestamp}".encode()
    mock_redis.get.return_value = valor_valido

    mocker.patch('app.api.auth.controllers._exchange_code_for_tokens',return_value={"id_token":"fake_token"})

    claims_validos = {
        'email': 'test@umce.cl', 'name': 'Test User',
        'nonce': 'test_nonce', 'email_verified': True
    }

    mocker.patch('app.api.auth.controllers._verify_id_token', return_value=claims_validos)
    mocker.patch('app.api.auth.controllers._require_domain', return_value=True)

    mock_user_service = mocker.patch('app.api.auth.controllers.buscar_o_crear_usuario', return_value=None)
    # 3. Mockeamos el helper de error.
    mock_oauth_helper = mocker.patch('app.api.auth.controllers.oauth', return_value=redirect('/login?auth_error=user_provisioning_failed'))

    class MockRequest:
        args = {'state': 'test_state', 'code': 'test_code'}

    response = manejar_callback(MockRequest())

    # Se llamó a la función para vuscar/crear usuario
    mock_user_service.assert_called_once_with(claims_validos)
    
    # Se llamo al helperde error con el código correcto
    mock_oauth_helper.assert_called_once_with('user_provisioning_failed')
    assert response.status_code == 302
    assert 'auth_error=user_provisioning_failed' in response.location