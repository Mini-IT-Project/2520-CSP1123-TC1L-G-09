from flask import Blueprint,render_template,session,redirect,url_for
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
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    if not user:
        return redirect(url_for('login.home'))
        
    return render_template("profile.html", user=user)

