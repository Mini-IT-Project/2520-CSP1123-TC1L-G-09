import os
from flask import Blueprint,render_template,request,redirect,url_for,flash,jsonify
from extensions import db,socketio
from forum_models import Post, Tag, Comment, Like, Report
from werkzeug.utils import secure_filename
from sqlalchemy import or_

forum_bp = Blueprint(
    "forum",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/forum-static"
)

ALLOWED_EXT = {"png","jpg","jpeg","git","mp4","mov"}

def allowed_file(filename: str) -> bool:  #check the filename
    if "." not in filename:
        return False
    extension = filename.split(".")[-1].lower()
    if extension in ALLOWED_EXT:
        return True
    else:
        return False
    
def analysis_tag(raw:str):
    if not raw:
        return []
    raw = raw.replace(","," ").replace("#"," ")
    tags = []
    for part in raw.split():
        cleaned = part.strip().lstrip("#")
        if cleaned:
            tags.append(cleaned)
    return tags

@forum_bp.context_processor
def inject_globals():
    return {"MMU SOUL":"MMU WHISPER"}

@forum_bp.route("/")  #post list
def index():
    search_keyword:str=request.args.get("q","").strip()
    tag_filter:str=request.args.get("tag","").strip()
    post_query=Post.query

    if search_keyword:
        search_pattern = f"%{search_keyword}%"
        posts_query = posts_query.filter(
            or_(
                Post.title.ilike(search_pattern),
                Post.content.ilike(search_pattern)
            )
        )
    
    if tag_filter:
        posts_query = posts_query.join(Post.tags).filter(Tag.name == tag_filter)

    all_posts = posts_query.order_by(Post.created_at.desc()).all()
    return render_template(
        "index.html", 
        posts=all_posts, 
        q=search_keyword, 
        tag=tag_filter
    )




