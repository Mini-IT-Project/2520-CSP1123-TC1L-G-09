from flask import Blueprint,render_template
from forum_models import User,Comment,Post

profile_bp = Blueprint("profile",
                       __name__,
                       template_folder="templates")

@profile_bp.route("/profile")
def profile():
    user = User.query.get_or_404(user.id)
    return render_template("profile.html", user=user)