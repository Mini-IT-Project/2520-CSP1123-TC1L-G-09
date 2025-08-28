import os
from flask import Blueprint,render_template,request,redirect,url_for,flash,jsonify
from extensions import db,socketio
from forum_models import Post, Tag
from werkzeug.utils import secure_filename

forum_bp = Blueprint(
    "forum",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/forum-static"
)