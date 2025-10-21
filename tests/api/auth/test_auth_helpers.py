from app.api.auth.helpers import oauth, oauth_ok

def test_oauth_redirect_by_default(app):
    """
    Verifica que la función oauth redirige a la URL del frontend por defecto cuando no se solitica una respuesta JSON.
    """
    error_code = "test_error_code"
    with app.test_request_context(f"/?error={error_code}"):
        response = oauth(error_code)
        assert response.status_code == 302
        assert response.location == f"http://localhost:5173/login?auth_error={error_code}"

def test_oauth_returns_json(app):
    """
    Verifica que la fución oauth devuelve un objeto JSON cuando el header "Accept" es "application/json".
    """
    error_code = "json_error"
    error_msg = "Este es unb mensaje de error"
    http_status = 401

    headers = {"Accept":"application/json"}
    with app.test_request_context("/", headers=headers):
        json_response, status_code = oauth(error_code,msg=error_msg,http_status=http_status)
        
        assert status_code == http_status
        expected_json = {"ok":False,"error":error_code,"message":error_msg}
        assert json_response == expected_json
    
def test_oauth_ok_redirects_to_success(app):
    """
    Verifica que la función oauth_ok siempre redirige a la página de éxito
    """
    with app.test_request_context("/"):
        response = oauth_ok()

        assert response.status_code == 302
        assert response.location == "http://localhost:5173/auth/success"