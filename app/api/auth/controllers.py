from flask import jsonify,make_response, session

import redis,os,time
from .helpers import oauth, oauth_ok
from .services import _exchange_code_for_tokens, _require_domain, _verify_id_token


myredis = redis.from_url(os.getenv("REDIS_URL"))

def manejar_callback(request):
    state = request.args.get("state")
    code = request.args.get("code")

    value = myredis.get(f"oauth:{state}")
    if not value:
        return oauth("invalid_state")
    
    nonce_redis,ts_redis = value.decode().split(":")

    # 2. Validar estado y tiempo de expiración
    now = int(time.time())
    if (now - int(ts_redis) > 300):
        return oauth("expired_state")

    try:
        token_payload = _exchange_code_for_tokens(code)
        idt = token_payload.get("id_token")
        claims = _verify_id_token(idt)
    except Exception:
        return oauth("token_exchange_failed")
    
    # 3. Validar nonce
    if (not claims) or claims.get("nonce") != nonce_redis:
        return oauth("invalid_nonce")
    # 4. Validar email  y dominio
    email = claims.get("email")
    email_verified = claims.get("email_verified")
    if not email or not email_verified:
        return oauth("email_unverified")

    if not _require_domain(email):
        return oauth("invalid_domain")


    # 6. Upsert de usuario en BD
    from .user_service import buscar_o_crear_usuario
    user = buscar_o_crear_usuario(claims)
    
    # 7. LOG IN del usuario (crear sesión)
    session.permanent = True
    session.modified = False

    from flask_login import login_user
    login_user(user,remember=False)
    myredis.delete(f"oauth:{state}")

    return oauth_ok()