from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from extensions import socketio
from login import Users
from datetime import datetime
from zoneinfo import ZoneInfo

MALAYSIA_TZ = ZoneInfo("Asia/Kuala_Lumpur")
MatchChat_bp = Blueprint("MatchChat",__name__)

class MC_WaitingUser(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(MALAYSIA_TZ))

@MatchChat_bp.route('/')
def home():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home')) #check used-id 
    
    return render_template("MatchChat.html")

@socketio.on('my event')
def handle_my_event(data):
    print(data, request.sid)

@socketio.on("match_request")
def handle_match_request():
    user_id = session.get("user_id")

    other = MC_WaitingUser.query.filter(MC_WaitingUser.user_id != user_id).first()
    if other:
        room

        db.session.delete(other)
        db.session.commit()
    else:
        new_user=MC_WaitingUser(user_id=user_id)
        db.session.add(new_user)
        db.session.commit()