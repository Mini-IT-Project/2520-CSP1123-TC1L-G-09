from flask import Blueprint, render_template, request

login_bp = Blueprint('login',__name__)

@login_bp.route('/')
def home():
    return render_template('login.html')

@login_bp.route('/register')
def register():
    return render_template('register.html')