from flask import Blueprint, render_template, redirect, url_for, session, flash
from extensions import db
from forum_models import Post, Report
from login import Users

admin_bp = Blueprint("admin",
                      __name__, 
                      template_folder="templates")

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login first", "error")
            return redirect(url_for("login.home"))
        user = Users.query.get(session["user_id"])
        if not user or not user.is_admin:
            flash("You are not authorized", "error")
            return redirect(url_for("forum.homepage"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template("admin_dashboard.html", posts=posts, reports=reports)

@admin_bp.route("/delete_post/<int:post_id>", methods=["POST"]) #let the admin can delete post
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully", "success")
    return redirect(url_for("admin.dashboard"))

