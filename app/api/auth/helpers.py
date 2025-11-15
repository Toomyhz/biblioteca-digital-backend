from flask import request, redirect,current_app

def oauth(code:str, msg:str = "", http_status:int = 400):
    FRONT_URL = current_app.config["FRONT_URL"]
    
    wants_json = "application/json" in (request.headers.get("Accept","") or "")
    if wants_json or request.args.get("format") == "json":
        return {"ok": False, "error": code, "message": msg}, http_status
    
    return redirect(f"{FRONT_URL}/login?auth_error={code}")

def oauth_ok():
    FRONT_URL = current_app.config["FRONT_URL"]
    return redirect(f"{FRONT_URL}/auth/success")