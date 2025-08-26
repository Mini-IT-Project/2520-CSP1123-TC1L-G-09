from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from extensions import db, socketio

db = SQLAlchemy()
socketio = SocketIO(async_code="eventlet", cors_allowed_origins="*")
