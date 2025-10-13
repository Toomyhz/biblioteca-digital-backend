from flask import request, redirect
FRONT_URL = "http://localhost:5173"

def oauth(code:str, msg:str = "", http_status:int = 400):
    wants_json = "application/json" in (request.headers.get("Accept","") or "")
    if wants_json or request.args.get("format") == "json":
        return {"ok": False, "error": code, "message": msg}, http_status
    
    return redirect(f"{FRONT_URL}/login?auth_error={code}")

def oauth_ok():
    return redirect(f"{FRONT_URL}/auth/success")