from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_socketio import join_room, emit, leave_room
from extensions import db
from extensions import socketio
from login import Users
from profile_routes import Profile_data
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
            user.sid= request.sid   #every time connected, update sid, so sid is lately
            print(f"new sid, {user.sid}, {request.sid}")

            activated_rooms= Activated_rooms.query.filter((Activated_rooms.user1_id == user_id)|(Activated_rooms.user2_id == user_id)).first()
            if activated_rooms:            #if user are joining an room, but reconnect, rejoin room
                join_room(activated_rooms.room_name, sid= request.sid)
                print (f"{user_id}, rejoin")
        else:
            new_user=Connected_users(user_id=user_id, sid=request.sid)
            db.session.add(new_user)
            print(f"{user_id} new connect, fisrt sid: {request.sid}")

            activated_rooms= Activated_rooms.query.filter((Activated_rooms.user1_id == user_id)|(Activated_rooms.user2_id == user_id)).first()
            if activated_rooms:            #if user are joining an room, but reconnect, rejoin room
                join_room(activated_rooms.room_name, sid= request.sid)
                print (f"{user_id} 1, rejoin")

        db.session.commit()

@socketio.on("disconnect")
def handle_disconnect():
    user=Connected_users.query.filter_by(sid=request.sid).first()
    if user:
        print(f"delete {user.user_id} from db")
        db.session.delete(user)
        db.session.commit()

@socketio.on('my event')
def handle_my_event(data):
    print(data, request.sid)

@socketio.on("match_request")
def handle_match_request():
    user_id = session.get("user_id") 

    other = MC_WaitingUser.query.filter(MC_WaitingUser.user_id != user_id).first() 
    if other:             #if other in waiting pool, direct join with other, if no, go into waiting pool
        room_name= f"room_{uuid.uuid4().hex}"                #unique room name

        my_activated_rooms= Activated_rooms.query.filter_by(room_name=room_name).first()
        if not my_activated_rooms:
            new_activated_rooms= Activated_rooms(room_name=room_name, user1_id=user_id, user2_id=other.user_id)
            db.session.add(new_activated_rooms)
            db.session.commit()           #update activated_room to db.Model, so user can rejoin while reconnect

        my_new_sid=Connected_users.query.filter_by(user_id=user_id).first()
        other_new_sid=Connected_users.query.filter_by(user_id=other.user_id).first()      #use lately sid to join room

        if not my_new_sid or not other_new_sid:
            db.session.delete(other)
            db.session.commit()
            return

        join_room(room_name, sid=my_new_sid.sid)
        join_room(room_name, sid=other_new_sid.sid)
        print(f"{my_new_sid.user_id} and {other_new_sid.user_id} join {room_name}")

        db.session.delete(other)
        db.session.commit()

        redirect_url = url_for("MatchChat.match_success_page", room_name=room_name, _external=True)        #url show room_name, so match_success_page can get room_name variable
        emit("match_success", {"redirect_url": redirect_url, "room_name": room_name},to=room_name)
    else:
        new_user=MC_WaitingUser(user_id=user_id)      #go to waiting pool
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

@MatchChat_bp.route('/match_success')
def match_success_page():
    print("match success")
    room_name = request.args.get("room_name")     #from html get room_name

    members= Activated_rooms.query.filter_by(room_name=room_name).first()       #to show avatar
    if members:
        user1=Profile_data.query.filter_by(user_id=members.user1_id).first()
        if not user1:
            user1= Profile_data(user_id=members.user1_id)
            db.session.add(user1)
            db.session.commit()
        user2=Profile_data.query.filter_by(user_id=members.user2_id).first()
        if not user2:
            user2= Profile_data(user_id=members.user2_id)
            db.session.add(user2)
            db.session.commit()

    redirect_url = url_for("MatchChat.chat_room", room_name=room_name, _external=True)      #to redirect to chat_room

    return render_template("matchSuccess.html", user1=user1, user2=user2, redirect_url=redirect_url)

@MatchChat_bp.route('/chat_room')
def chat_room():
    room_name = request.args.get("room_name")     #from html get room_name

    members= Activated_rooms.query.filter_by(room_name=room_name).first()       #to show avatar
    if members:
        user1=Profile_data.query.filter_by(user_id=members.user1_id).first()
        user2=Profile_data.query.filter_by(user_id=members.user2_id).first()

    return render_template("chat_room.html", user1=user1, user2=user2, room_name=room_name)

@socketio.on("message")
def handle_message(data):
    room_name = data["room_name"]
    print(f"123 {room_name}")

    user_id = session.get("user_id")
    activated_rooms= Activated_rooms.query.filter((Activated_rooms.user1_id == user_id)|(Activated_rooms.user2_id == user_id)).first()
    if activated_rooms:            #if user are joining an room, but reconnect, rejoin room
        join_room(activated_rooms.room_name, sid= request.sid)
        print (f"{user_id}, rejoin")

    sender_id= data["user_id"]

    message=data["message"]
    print(message)

    emit("print_message", {"message": message, "sender_id" :sender_id}, to=room_name)

@socketio.on("you_leave_room")
def handle_you_leave_room(data):
    room_name = data.get("room_name")

    leave_room(room_name)

    emit("other_user_leave", to=room_name)

    emit("you_leave_room", room=request.sid)

@socketio.on("other_leave_room")
def handle_other_leave_room(data):
    room_name = data.get("room_name")

    leave_room(room_name)

    room = Activated_rooms.query.filter_by(room_name=room_name).first()
    if room:
        db.session.delete(room)
        db.session.commit()