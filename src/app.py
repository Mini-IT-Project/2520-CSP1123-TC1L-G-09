from flask import Flask
from main import main_bp
from bottle_feature import bottle_bp
from extensions import db, socketio  
import os

app = Flask(__name__)

#database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bottles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#upload file
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

app.register_blueprint(main_bp, url_prefix="/")
app.register_blueprint(bottle_bp, url_prefix="/bottle")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
