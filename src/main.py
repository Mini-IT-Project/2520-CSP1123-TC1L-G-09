from flask import Blueprint, render_template
from bottle import Bottle   
from bottle import db       

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    unpicked_count = Bottle.query.filter_by(status="unpicked").count()
    return render_template("index.html", unpicked_count=unpicked_count)
