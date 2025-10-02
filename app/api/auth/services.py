from flask import current_app
from urllib.parse import urlencode
import os, secrets, time, requests, redis

myredis = redis.from_url(os.getenv("REDIS_URL"))


from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

def _build_google_auth_url():
    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    ts = int(time.time())

    myredis.setex(f"oauth:{state}",300,f"{nonce}:{ts}")

    params = {
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "redirect_uri": current_app.config["OAUTH_REDIRECT_URI"],
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "include_granted_scopes": "true",
        "state": state,
        "nonce": nonce,
        # Sugerencia para cuentas del dominio (solo “advice”, siempre valida server-side):
        "hd": current_app.config.get("ALLOWED_EMAIL_DOMAIN", ""),
        "prompt": "consent",  # opcional; para forzar selección/cambio de cuenta
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def _exchange_code_for_tokens(code: str):
    data = {
        "code": code,
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": current_app.config["OAUTH_REDIRECT_URI"],
        "grant_type": "authorization_code",
    }
    r = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)
    r.raise_for_status()
    return r.json()  # { access_token, id_token, refresh_token?, expires_in, ... }

def _verify_id_token(idt: str):
    # Verifica firma y audiencia del token
    req = google_requests.Request()
    claims = id_token.verify_oauth2_token(
        idt, req, audience=current_app.config["GOOGLE_CLIENT_ID"]
    )
    return claims  # dict con 'email', 'email_verified', 'name', 'picture', 'hd', 'sub', etc.

def _require_domain(email: str):
    domain = email.split("@")[-1].lower()
    allowed = current_app.config.get("ALLOWED_EMAIL_DOMAINS").lower()
    return allowed and (domain == allowed)