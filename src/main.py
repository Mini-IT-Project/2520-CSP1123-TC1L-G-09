from flask import Blueprint, render_template, session
from bottle_feature import Bottle

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
