from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_socketio import join_room, emit
from extensions import db
from extensions import socketio
from login import Users
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

MALAYSIA_TZ = ZoneInfo("Asia/Kuala_Lumpur")
MatchChat_bp = Blueprint("MatchChat",__name__)

class MC_WaitingUser(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(MALAYSIA_TZ))

class Connected_users(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sid= db.Column(db.String(200), default=" ")

class Activated_rooms(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    room_name= db.Column(db.String(200), default=" ")
    user1_id= db.Column(db.Integer, db.ForeignKey('users.id'))
    user2_id= db.Column(db.Integer, db.ForeignKey('users.id'))

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

@socketio.on("connect")
def handle_connect():
    user_id = session.get("user_id")
    if user_id:
        user= Connected_users.query.filter_by(user_id=user_id).first()
        if user:
            user.sid= request.sid
            print(f"new sid, {user.sid}, {request.sid}")

            activated_rooms= Activated_rooms.query.filter((Activated_rooms.user1_id == user_id)|(Activated_rooms.user2_id == user_id)).first()
            if activated_rooms:
                join_room(activated_rooms.room_name, sid= request.sid)
                print (f"{user_id}, rejoin")
        else:
            new_user=Connected_users(user_id=user_id, sid=request.sid)
            db.session.add(new_user)
            print(f"{user_id} new connect, fisrt sid: {request.sid}")

        db.session.commit()

@socketio.on("disconnect")
def handle_disconnect():
    user=Connected_users.query.filter_by(sid=request.sid).first()
    if user:
        print(f"delete{user.user_id}from db")
        db.session.delete(user)
        db.session.commit()

@socketio.on('my event')
def handle_my_event(data):
    print(data, request.sid)

@socketio.on("match_request")
def handle_match_request():
    user_id = session.get("user_id") 

    other = MC_WaitingUser.query.filter(MC_WaitingUser.user_id != user_id).first() 
    if other: 
        room_name= f"room-{uuid.uuid4().hex}"

        my_activated_rooms= Activated_rooms.query.filter_by(room_name=room_name).first()
        if not my_activated_rooms:
            new_activated_rooms= Activated_rooms(room_name=room_name, user1_id=user_id, user2_id=other.user_id)
            db.session.add(new_activated_rooms)
            db.session.commit()

        my_new_sid=Connected_users.query.filter_by(user_id=user_id).first()
        other_new_sid=Connected_users.query.filter_by(user_id=other.user_id).first()

        join_room(room_name, sid=my_new_sid.sid)
        join_room(room_name, sid=other_new_sid.sid)
        print(f"{my_new_sid.user_id} and {other_new_sid.user_id} join {room_name}")

        db.session.delete(other)
        db.session.commit()

        emit("match success", to=room_name)
    else:
        new_user=MC_WaitingUser(user_id=user_id)
        print(f"{user_id} are waiting")
        db.session.add(new_user)
        db.session.commit()

@socketio.on("cancel_request")
def handle_cancel_request():
    user_id = session.get("user_id")

    cancel_user=MC_WaitingUser.query.filter_by(user_id=user_id).first()
    print(f"{user_id} cancel")

    db.session.delete(cancel_user)
    db.session.commit()