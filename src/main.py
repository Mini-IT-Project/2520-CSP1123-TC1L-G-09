from flask import Blueprint, render_template, session
from bottle_feature import Bottle
from forum_models import User 

main_bp = Blueprint("main", __name__)

#Homepage
@main_bp.route("/", endpoint="homepage")
def homepage():
    events = [
        {"title": "Orientation Week", "date": "2025-09-10", "description": "Welcome to new students!"},
        {"title": "Open Day", "date": "2025-09-20", "description": "Visit our campus."}
    ]
    announcements = [
        {"title": "Maintenance Notice", "date": "2025-09-05", "description": "System maintenance from 2-4 PM."},
        {"title": "Library Closed", "date": "2025-09-08", "description": "Library will be closed on public holiday."}
    ]

    #Drifting bottle amount
    unpicked_count = Bottle.query.filter_by(status="unpicked").count()

    return render_template(
        "homepage.html",
        events=events,
        announcements=announcements,
        unpicked_count=unpicked_count
    )

#Profile Page
@main_bp.route("/profile", endpoint="profile")
def profile():
    user = get_current_user()
    if not user:
        from flask import redirect, url_for
        return redirect(url_for('login.home'))
    return render_template("profile.html", user=user)

def get_current_user():
    user_id = session.get("user_id")  
    if user_id:
        return User.query.get(user_id)
    return None

#Match Chat Route
@main_bp.route("/match-chat", endpoint="match_chat")
def match_chat():
    return render_template("MatchChat.html")