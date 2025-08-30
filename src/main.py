from flask import Blueprint, render_template    

main_bp = Blueprint("main", __name__)

events = [
    {"title":"Orientation Week 2025","date":"2025-09-05","description":"Welcome to MMMU!"}
]

announcements = [
    {"title":"New Shuttle Bus Route","date":"2025-09-03","description":"New route added from Cyberjaya to Putrajaya Sentral!"}
]

@main_bp.route("/")
def homepage():
    return render_template("homepage.html",events=events, announcements=announcements)
