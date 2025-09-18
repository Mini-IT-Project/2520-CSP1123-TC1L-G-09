from flask import Flask
import os
from login import login_bp
from forum_routes import forum_bp
from extensions import db, socketio  
from main import main_bp
from bottle_feature import bottle_bp
from profile_routes import profile_bp
from match_chat import MatchChat_bp
from admin_routes import admin_bp

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback-key')

    UPLOAD_FOLDER = os.path.join(app.root_path,"static", "uploads")  
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    db.init_app(app)
    socketio.init_app(app)

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(forum_bp, url_prefix="/forum")
    app.register_blueprint(bottle_bp, url_prefix="/bottle")
    app.register_blueprint(login_bp, url_prefix="/login")
    app.register_blueprint(profile_bp,url_prefix="/profile")
    app.register_blueprint(MatchChat_bp, url_prefix="/MatchChat")
    app.register_blueprint(admin_bp,url_prefix="/admin")

    with app.app_context():
        db.create_all()

    return app

#website address
if __name__ == "__main__":
    app = create_app()
    socketio.run(
        app,
        host='127.0.0.1',
        port=5000,
        debug=True
    )
