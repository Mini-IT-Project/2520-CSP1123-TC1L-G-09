from flask import Blueprint, render_template, request, redirect, url_for

bottle_bp = Blueprint("bottle", __name__)

#Store drifting bottle
bottles = []

class Bottle(db.Model):
    __tablename__ = 'bottles_table'
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text,nullable=False)
    campus = db.Column(db.String(50),nullable=False,default=cyberjaya)
    status = db.Column(db.String(20),default='unpicked')
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self):
        return f"Bottle{self.id} - {self.status} - {self.campus}"
    
@bottle_bp.route("/throw", methods=["POST"],endpoint="throw")
def throw_bottle():
    message = request.form.get("message")
    if message:
        bottles.append(message)
    return redirect(url_for("main.index"))

@bottle_bp.route("/pick",endpoint="pick")
def pick_bottle():
    if bottles:
        picked = bottles.pop(0)   
        return render_template("pick.html", message=picked)
    return render_template("pick.html", message="There is nothing...")
