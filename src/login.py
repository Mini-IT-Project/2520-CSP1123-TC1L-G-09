from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime

login_bp = Blueprint("login",__name__)

class users(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String(120), unique=True, nullable=False)
    password= db.Column(db.String(200), nullable=False)

@login_bp.route('/')
def home():
    return render_template('login.html')

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'] + "@student.mmu.edu.my"
        password = generate_password_hash(request.form['password'])

        new_user= users(email=email, password=password)
        print(f"{new_user}, {email}, {password}")
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login.home'))
        except IntegrityError:
            db.session.rollback()
            flash("Email already exist!", "error")
        except Exception as e:
            db.session.rollback()
            flash(f":( Some unexpected error happen: {e}")
<<<<<<< HEAD
                 
=======

>>>>>>> main
    return render_template('register.html')