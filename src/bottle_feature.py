from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
from extensions import db
from login import Users
import os
from werkzeug.utils import secure_filename
import random

bottle_bp = Blueprint("bottle", __name__)

# Database Model
class Bottle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)   
    file_path = db.Column(db.String(200), nullable=True)
    file_type = db.Column(db.String(200), nullable=True)
    campus = db.Column(db.String(20), nullable=False, default="cyberjaya")
    status = db.Column(db.String(20), default="unpicked")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp3", "wav", "mp4", "mov"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bottle_bp.route("/")
def DriftingBottle():
    user_id = session.get("user_id") # Get the current logged-in user's ID from session

    # If no user is logged in, show a flash message and redirect to login page
    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
     # Query the database to get the user object using the stored user_id
    user = Users.query.get(user_id) 

    # If the user does not exist (invalid user_id), redirect to login again
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home')) #Check used-id 
    
    # Count how many bottles are still unpicked (status = "unpicked")
    unpicked_count = Bottle.query.filter_by(status="unpicked").count()
    # Render the DriftingBottle.html template and pass the count of unpicked bottles
    return render_template("DriftingBottle.html", unpicked_count=unpicked_count)

@bottle_bp.route("/throw", methods=["GET", "POST"], endpoint="throw")
def throw_bottle():
    # Check if the request method is POST (user submitting a new bottle)
    if request.method == "POST":
        # Get the text content from the form
        content = request.form.get("content")

        # Get the selected campus, defaulting to "cyberjaya" if not provided
        campus = request.form.get("campus", "cyberjaya")

        # Get any uploaded file (image, audio, or video)
        file = request.files.get("file")

        # Initialize file path and type as None (in case no file is uploaded)
        file_path = None
        file_type = None

        # If there is a file and it has an allowed extension
        if file and allowed_file(file.filename):
            # Secure the filename to prevent path traversal issues
            filename = secure_filename(file.filename)

            # Get the upload folder path from app configuration
            upload_folder = current_app.config["UPLOAD_FOLDER"]   

            # Create the folder if it does not exist
            os.makedirs(upload_folder, exist_ok=True)

            # Construct the absolute path and save the uploaded file
            abs_path = os.path.join(upload_folder, filename)
            file.save(abs_path)

            # Store relative path for database storage
            file_path = f"uploads/{filename}"

            # Determine file type based on extension
            ext = filename.rsplit(".", 1)[1].lower()
            if ext in {"png", "jpg", "jpeg", "gif"}:
                file_type = "image"
            elif ext in {"mp3", "wav"}:
                file_type = "audio"
            elif ext in {"mp4", "mov"}:
                file_type = "video"

        # If there is either text content or a file, create a new Bottle object
        if content or file_path:
            bottle = Bottle(content=content, campus=campus, file_path=file_path, file_type=file_type)
            # Add the new bottle record to the database
            db.session.add(bottle)
            db.session.commit()

        # Redirect back to the same page after submission (avoids form resubmission)
        return redirect(url_for("bottle.throw"))

    # If request is GET, show the page
    # Count how many bottles are still "unpicked" (not yet retrieved by anyone)
    unpicked_count = Bottle.query.filter_by(status="unpicked").count()

    # Render the drifting bottle HTML template, passing the count of unpicked bottles
    return render_template("DriftingBottle.html", unpicked_count=unpicked_count)

@bottle_bp.route("/pick", endpoint="pick")
def pick_bottle():
    # Get the 'campus' parameter from the request URL, defaulting to "all" if not provided
    campus = request.args.get("campus", "all")

    # Start a query to select all bottles that have not been picked yet
    query = Bottle.query.filter_by(status="unpicked")
    
    # If the user specifies a campus, filter bottles by that campus
    if campus != "all":
        query = query.filter_by(campus=campus)

    # Retrieve all bottles that match the query (unpicked, and optionally by campus)
    database = query.all()

    # If there are available bottles
    if database:
        # Randomly choose one bottle from the available ones
        bottle = random.choice(database)

        # Update its status to "picked" so it won’t be available again
        bottle.status = "picked"

        # Commit the change to the database
        db.session.commit()

        # Return the bottle (this line is incomplete in your snippet, 
        # but normally you would return bottle info as JSON or HTML response)
        return render_template("pick.html", bottle=bottle)
    
    else:
        # If no bottles are available, return an appropriate message or empty response
        return render_template("pick.html", bottle=None)
