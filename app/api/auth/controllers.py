from flask import jsonify,make_response, session
import redis,os,time
from .helpers import oauth, oauth_ok
from .services import _exchange_code_for_tokens, _require_domain, _verify_id_token
from .user_service import buscar_o_crear_usuario
from app.extensions import redis_client
from flask_login import login_user


STATE_EXPIRATION_SECONDS = 300



def manejar_callback(request):

    state = request.args.get("state")
    code = request.args.get("code")

    # 1. Validar estado desde Redis
    redis_key = f"oauth:{state}"
    value = redis_client.get(redis_key)
    if not value:
        return oauth("invalid_state")
    
    try:
        nonce_redis,ts_redis_str = value.decode().split(":")
        ts_redis = int(ts_redis_str)

    except (ValueError, TypeError):
        return oauth("invalid_state_format")

    # 2. Validar tiempo de expiración
    if time.time() - ts_redis > STATE_EXPIRATION_SECONDS:
        return oauth("expired_state")

    # 3.Intercambiar código por tokens y verificar
    try:
        token_payload = _exchange_code_for_tokens(code)
        idt = token_payload.get("id_token")
        claims = _verify_id_token(idt)
    except Exception:
        return oauth("token_exchange_failed")
    
    # 4. Validar nonce
    if (not claims) or claims.get("nonce") != nonce_redis:
        return oauth("invalid_nonce")
    
    # 3. Validar email  y dominio
    email = claims.get("email")
    if not claims.get("email_verified") or not _require_domain(email):
        return oauth("email_unverified_or_invalid_domain")

    # 6. Upsert de usuario en BD
    user = buscar_o_crear_usuario(claims)
    if not user:
        return oauth("user_provisioning_failed")
    
    # 7. LOG IN del usuario (crear sesión)
    login_user(user,remember=False)
    session.permanent = True

    redis_client.delete(redis_key)

    return oauth_ok()