from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db  

bottle_bp = Blueprint("bottle", __name__)

class Bottle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)

@bottle_bp.route("/throw", methods=["POST"], endpoint="throw")
def throw_bottle():
    msg = request.form.get("message")
    if msg:
        bottle = Bottle(message=msg)
        db.session.add(bottle)
        db.session.commit()
    return redirect(url_for("main.index"))

@bottle_bp.route("/pick", endpoint="pick")
def pick_bottle():
    bottle = Bottle.query.first()
    if bottle:
        msg = bottle.message
        db.session.delete(bottle)
        db.session.commit()
        return render_template("pick.html", message=msg)
    return render_template("pick.html", message="There is nothing...")
