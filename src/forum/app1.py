import os
from flask import Flask
from extensions import db, socketio
from forum import forum_bp

def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']= os.environ.get('SECRET_KEY' , 'dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

    db.init_app(app)
    socketio.init_app(app)

    app.register_blueprint(forum_bp, url_prefix='/forum')

    with app.app_context():
        db.create_all()

    return app

app = create_app()
if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT',5000)),
        debug=True
        )