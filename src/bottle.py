from flask import Blueprint, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

bottle_bp = Blueprint("bottle", __name__, template_folder="templates")

from app import app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bottles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Bottle(db.Model):
    __tablename__ = 'bottles_table'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unpicked')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Bottle {self.id} - {self.status}>"

@bottle_bp.route("/throw", methods=["POST"])
def throw():
    content = request.form.get("content")
    if content:
        new_bottle = Bottle(content=content)
        db.session.add(new_bottle)
        db.session.commit()
    return redirect(url_for("main.index"))

@bottle_bp.route("/pick")
def pick():
    bottles = Bottle.query.filter_by(status="unpicked").all()
    if bottles:
        bottle = random.choice(bottles)
        bottle.status = "picked"
        db.session.commit()
        return render_template("pick.html", bottle=bottle)
    else:
        return render_template("pick.html", bottle=None)

@bottle_bp.route("/debug/count")
def debug_count():
    return {"bottles_count": Bottle.query.count()}

with app.app_context():
    db.create_all()
