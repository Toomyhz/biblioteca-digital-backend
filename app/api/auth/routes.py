from flask import (Blueprint, 
                   request, 
                   redirect, 
                   session)
from app.api.auth.helpers import oauth
from .controllers import manejar_callback

from flask_login import (
    logout_user, 
    current_user, 
    login_required)

from app.api.auth.services import (
    _build_google_auth_url,
)
    
from flask_restx import Namespace, Resource

auth_ns = Namespace("auth",description="Autenticación de Usuarios y Sesiones")

@auth_ns.route("/me/")
class CurrentUser(Resource):
    @auth_ns.doc("get_current_user")
    def get(self):
        '''Obtiene la información del usuario actualmente logueado'''
        if not current_user.is_authenticated:
            return {"is_authenticated":False,"user":None},200
        
        return{
            "is_authenticated": True,
            "user": {
                "id": current_user.id_usuario,
                "correo_institucional": current_user.correo_institucional,
                "nombre_usuario": current_user.nombre_usuario,
                "foto_perfil": current_user.foto_perfil,
                "rol": current_user.rol
                }
        }, 200

@auth_ns.route("/me/admin/")
class AdminCheck(Resource):
    @auth_ns.doc("check_is_admin")
    def get(self):
        '''Verifica si el usuario actual es administrador'''
        return {
            "is_authenticated": current_user.is_authenticated,
            "is_admin": current_user.is_authenticated and current_user.rol == "admin"
        }, 200

@auth_ns.route("/logout/")
class Logout(Resource):
    @auth_ns.doc("logout_user")
    def post(self):
        '''Cierra la sesión del usuario'''
        if not current_user.is_authenticated:
            return{"message": "No hay sesión activa para cerrar"}, 401

        logout_user()
        session.clear()
        return {"message": "Sesión cerrada correctamente"}, 200

@auth_ns.route("/login/")
class Login(Resource):
    @auth_ns.doc(False)
    def get(self):
        '''Redirige al proveedor de OAuth para iniciar sesión'''
        return redirect(_build_google_auth_url())

@auth_ns.route("/callback/")
class Callback(Resource):
    @auth_ns.doc(False)
    def get(self):
        '''Callback del proveedor OAuth después del login'''
        error = request.args.get("error")
        if error:
            return oauth(error)
        return manejar_callback(request)