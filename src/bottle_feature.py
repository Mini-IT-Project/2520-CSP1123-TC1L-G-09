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
    
@bottle_bp.route("/throw", methods=["POST"])
def throw():
    content = request.form.get("content")
    campus = request.form.get("campus")
    if content and campus:
        new_bottle = Bottle(content=content, campus=campus)
        db.session.add(new_bottle)
        db.session.commit()
    return redirect(url_for("main.index"))

@bottle_bp.route("/pick")
def pick():
    campus = request.args.get("campus", "all")
    query = Bottle.query.filter_by(status="unpicked")
    if campus != "all":
        query = query.filter_by(campus=campus)
    bottles = query.all()
    
    if bottles:
        bottle = random.choice(bottles)
        bottle.status = "picked"
        db.session.commit()
        return render_template("pick.html", bottle=bottle)
    else:
        return render_template("pick.html", bottle=None)
