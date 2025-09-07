from flask import Blueprint,render_template,session,redirect,url_for, flash
from forum_models import Comment,Post,Like
from login import Users

profile_bp = Blueprint(
    "profile",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/forum-static"
)

@profile_bp.route("/")
def myProfile():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    return render_template("myProfile.html")

@profile_bp.route("/history")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
        
    return render_template("profile.html", user=user)

@profile_bp.route("/Settings")
def settings():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    return render_template("settings.html")