from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from main import main_bp
from bottle_feature import bottle_bp
from extensions import db, socketio

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bottles.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio.init_app(app)

app.register_blueprint(main_bp, url_prefix="/")
app.register_blueprint(bottle_bp, url_prefix="/bottle")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app,debug=True)
