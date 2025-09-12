from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from login import Users

MatchChat_bp = Blueprint("MatchChat",__name__)

@MatchChat_bp.route('/')
def home():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home')) #check used-id 
    
    return render_template("MatchChat.html")