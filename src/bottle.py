from flask import Blueprint, render_template, request, redirect, url_for

bottle_bp = Blueprint("bottle", __name__)

#Store drifting bottle
bottles = []

@bottle_bp.route("/throw", methods=["POST"])
def throw_bottle():
    message = request.form.get("message")
    if message:
        bottles.append(message)
    return redirect(url_for("main.index"))

@bottle_bp.route("/pick")
def pick_bottle():
    if bottles:
        picked = bottles.pop(0)   
        return render_template("pick.html", message=picked)
    return render_template("pick.html", message="There is nothing...")