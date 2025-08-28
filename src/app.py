import os
from flask import Flask
from main import main_bp
from bottle_feature import bottle_bp
from login import login_bp
from forum_routes import forum_bp
from extensions import db, socketio  # ✅ 从 extensions 导入

def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bottles.db'
    app.config['SECRET_KEY']= os.environ.get('SECRET_KEY', 'dev-fallback-key')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")


    db.init_app(app)
    socketio.init_app(app)

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(forum_bp, url_prefix='/forum')
    app.register_blueprint(bottle_bp, url_prefix="/bottle")
    app.register_blueprint(login_bp, url_prefix="/login")

    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT',5001)),
        debug=True
        )
