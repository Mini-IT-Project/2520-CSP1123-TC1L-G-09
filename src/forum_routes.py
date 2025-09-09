import os
from flask import Blueprint,render_template,request,redirect,url_for,flash,current_app,send_from_directory
from extensions import db,socketio
from forum_models import User,Post, Tag, Comment, Like, Report
from werkzeug.utils import secure_filename
from sqlalchemy import or_

forum_bp = Blueprint(
    "forum",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/forum-static"
)

@forum_bp.route("/", endpoint="homepage")
def homepage():
    return render_template("forum_home.html")


ALLOWED_EXT = {"png","jpg","jpeg","gif","mp4","mov"}

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


@forum_bp.route("/")  #post list
def index():
    search_keyword:str=request.args.get("q","").strip()
    tag_filter:str=request.args.get("tag","").strip()
    posts_query=Post.query

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
        "forum_home.html", 
        posts=all_posts, 
        q=search_keyword, 
        tag=tag_filter
    )

@forum_bp.route("/p/<int:post_id>")
def post_detail(post_id):
    post=Post.query.get_or_404(post_id) # Query the post from the database and return to the 404 page if not found
    return render_template("post_detail.html",post=post)

@forum_bp.route("/post/new",methods=["GET","POST"]) #Create a new post, GET displays the form, POST handles the submission
def create_post():
    if request.method=="GET":
        return render_template("create_edit_post.html",
                               mode="create",
                               post=None,
                               existing_tags="")
    #get form data
    title=request.form.get("title","").strip()
    content=request.form.get("content","").strip()
    tags_input=request.form.get("tags","").strip()

#validate data
    if not title or not content:
        flash("Please write your title and content","error")
        return redirect(url_for("forum.create_post"))
    
    new_post=Post(title=title,content=content,media_url=media_url)

    media_url=handle_file_upload(request.files.get("media"))

    for tag in process_tags(tags_input):
        new_post.tags.append(tag)

    db.session.add(new_post)
    db.session.commit()

    socketio.emit("new_post",new_post.to_dict(base_url=request.host_url))

    flash("Post Uploaded!","success")
    return redirect(url_for("forum.forum_home"))

def handle_file_upload(file_object):
    if not file_object or not allowed_file(file_object.filename):
        return None
    filename=secure_filename(file_object.filename)
    upload_dir=current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir,exist_ok=True)

    file_path=os.path.join(upload_dir,filename)
    file_object.save(file_path)
    return f"/upload/{filename}"

def process_tags(tag_string):
    tag_objects=[]
    for tag_name in analysis_tag(tag_string):
        tag=Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag=Tag(name=tag_name)
            db.session.add(tag)
        tag_objects.append(tag)
    return tag_objects

@forum_bp.route("/post/edit",methods=["GET","POST"])
def edit_post(post_id):
    post=Post.query.get_or_404(post_id)
    if request.method=="GET":
        return render_template("create_edit_post.html",
                               mode="edit",
                               post=post,
                               existing_tags=" ".join(f"#{tag.name}" for tag in post.tags))                        
    
    post.title=request.form.get("title","").strip()
    post.content=request.form.get("content","").strip()
    new_tags_input=request.form.get("tags","").strip()
    post.tags.clear()
    tag_names=analysis_tag(new_tags_input)
    
    for tag_name in tag_names:
        existing_tag=Tag.query.filter_by(name=tag_name).first()
        if existing_tag:
            post.tags.append(existing_tag)
        else:
            new_tag=Tag(name=tag_name)
            db.session.add(new_tag)
            post.tags.append(new_tag)
    
    uploaded_file=request.files.get("media")
    if not uploaded_file or not allowed_file(uploaded_file.filename):
        return None
    filename=secure_filename(uploaded_file.filename)
    upload_dir=current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir,exist_ok=True)

    file_path=os.path.join(upload_dir,filename)
    uploaded_file.save(file_path)
    return f"/upload/{filename}"

@forum_bp.route("/post/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    post=Post.query.get_or_404(post_id)
    new_like=Like(post=post)
    db.session.add(new_like)
    db.session.commit()
    current_likes=post.like_count()
    socketio.emit("like_updates",{
        "post_id":post.id,
        "likes":current_likes
    })
    return {
        "ok":True,
        "message":"Like Successfully",
        "likes":current_likes,
        "post_id":post.id
    }

@forum_bp.route("/post/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):
    post=Post.query.get_or_404(post_id)
    comment_content=request.form.get("body","").strip()
    comment_author=request.form.get("author","Anonymous").strip() or "Anonymous"
    if not comment_content:
        return {"ok":False,"error":"Please write your comment"},400
    new_comment=Comment(
        post=post,
        body=comment_content,
        author=comment_author
    )
    
    db.session.add(new_comment)
    db.session.commit()
    socketio.emit("new_comment",{
        "post_id":post_id,
        "body":comment_content,
        "author":comment_author,
        "comment_id":new_comment.id,
        "total_comment":post.comment_count()
    })
    return{
        "ok":True,
        "message":"Comment Successfully!",
        "comment_id":new_comment.id,
        "total_comment":post.comment_count()
    }


@forum_bp.route("/report/<int:post_id>", methods=["GET", "POST"])
def report_post(post_id):
    post=Post.query.get_or_404(post_id)
    if request.method=="GET":
        return render_template("report_post.html",post=post)
    
    report_reason=request.form.get("report")
    if not report_reason:
        flash("Please select your reason","error")
        return(url_for("forum.report_post",post_id=post.id))
    
    new_report=Report(
        post=post,
        reason=report_reason,
    )
    db.session.add(new_report)
    db.session.commit()

    flash("Report Successfully!Thank you response!","success")
    return redirect(url_for("forum.post_detail",post_id=post.id))

@forum_bp.route("/upload/<path:filename>")
def serve_upload(filename):
    upload=current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload,filename)