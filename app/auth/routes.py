from flask import Blueprint
from flask import render_template, request, redirect, url_for,jsonify
from .controllers import login_controller

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json()
    code = data.get('code')
    if code:
        return login_controller(code)
    else:
        return jsonify({'error': 'No authorization code provided'}), 400