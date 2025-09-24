from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash  #password is safe, even me dont know too, through hash
from sqlalchemy.exc import IntegrityError
import re

login_bp = Blueprint("login",__name__)

class Users(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String(120), unique=True, nullable=False)
    password= db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    posts = db.relationship("Post", backref="author", lazy="dynamic")
    likes = db.relationship("Like", backref="user", lazy="dynamic")
    comments = db.relationship("Comment", backref="user", lazy="dynamic")

@login_bp.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        login_email = request.form['email'] + "@student.mmu.edu.my"
        login_user= Users.query.filter_by(email=login_email).first()
        if login_user:
            login_password= request.form['password']
            if check_password_hash(login_user.password, login_password):
                session['user_id'] = login_user.id
                session['is_admin'] = bool(login_user.is_admin)
                
                if login_user.is_admin:
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('main.homepage'))
            else:
                flash("Password wrong, Please try again!", "error")
        else:
            flash("Email not found", "error")

    return render_template('login.html')


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'] + "@student.mmu.edu.my"

        if len(request.form['password'])< 8:         #check passsword strength, at least one upper, lowercase letter, and one number, and at least 8 digit
            flash("Password length should more than 8")
            return render_template("register.html")
        if not re.search(r"[A-Z]", request.form['password']):
            flash("Password should include at least one uppercase letter")
            return render_template("register.html")
        if not re.search(r"[a-z]", request.form['password']):
            flash("Password should include at least one lowercase letter")
            return render_template("register.html")
        if not re.search(r"\d", request.form['password']):
            flash("Password should include at least one number")
            return render_template("register.html")

        password = generate_password_hash(request.form['password'])

        new_user= Users(email=email, password=password)
        print(f"{new_user}, {email}, {password}")
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login.home'))
        except IntegrityError:      #if email unique crash
            db.session.rollback()
            flash("Email already exist!", "error")
        except Exception as e:       #else error
            db.session.rollback()
            flash(f":( Some unexpected error happen: {e}")

    return render_template('register.html')

@login_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login.home'))