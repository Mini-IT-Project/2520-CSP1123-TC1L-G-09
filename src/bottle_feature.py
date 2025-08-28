from flask import Blueprint, render_template, request, redirect, url_for, current_app
from extensions import db
import os
from werkzeug.utils import secure_filename
import random

bottle_bp = Blueprint("bottle", __name__)

# Database Model
class Bottle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)   
    file_path = db.Column(db.String(200), nullable=True)
    file_type = db.Column(db.String(20), nullable=True)
    campus = db.Column(db.String(50), nullable=False, default="cyberjaya")
    status = db.Column(db.String(20), default="unpicked")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp3", "wav", "mp4", "mov"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bottle_bp.route("/throw", methods=["POST"], endpoint="throw")
def throw_bottle():
    content = request.form.get("content")
    campus = request.form.get("campus", "cyberjaya")
    file = request.files.get("file")

    file_path = None
    file_type = None

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config["UPLOAD_FOLDER"]   
        os.makedirs(upload_folder, exist_ok=True)

        abs_path = os.path.join(upload_folder, filename)
        file.save(abs_path)

        file_path = f"uploads/{filename}"

        ext = filename.rsplit(".", 1)[1].lower()
        if ext in {"png", "jpg", "jpeg", "gif"}:
            file_type = "image"
        elif ext in {"mp3", "wav"}:
            file_type = "audio"
        elif ext in {"mp4", "mov"}:
            file_type = "video"

    if content or file_path:
        bottle = Bottle(content=content, campus=campus, file_path=file_path, file_type=file_type)
        db.session.add(bottle)
        db.session.commit()

    return redirect(url_for("main.index"))

@bottle_bp.route("/pick", endpoint="pick")
def pick_bottle():
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
