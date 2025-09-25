import os
from flask import Blueprint,render_template,request,redirect,url_for,flash,current_app,send_from_directory,session,jsonify
from extensions import db,socketio
from forum_models import Post, Tag, Comment, Like, Report,PostMedia,CommentLike
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from login import Users
from profile_routes import Profile_data,profile

forum_bp = Blueprint(
    "forum",
    __name__,
    template_folder="templates"
)

#File upload processing
def handle_file_upload(file):
    ALLOWED_EXT = {"png","jpg","jpeg","gif","mp4","mov"}  

    def allowed_file(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT #check the file is legal

    if not file or not allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)
    extension = filename.rsplit(".", 1)[1].lower()

    upload_dir = os.path.join(current_app.root_path, "static", "uploads") #save the file to static/uploads
    os.makedirs(upload_dir, exist_ok=True)

    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)

    return {
        "filename": filename,
        "filetype": extension,
        "media_url": f"uploads/{filename}"
    }
    
def analysis_tag(raw:str): #raw(exp:Python/WEB/....) str (indicates that is string)
    if not raw:
        return []
    raw = raw.replace(","," ").replace("#"," ")  
    tags = []
    for part in raw.split():
        cleaned = part.strip().lstrip("#")
        if cleaned:
            tags.append(cleaned)
    return tags


@forum_bp.route("/", endpoint="homepage")  #post list
def index():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home')) #check used-id 
    
    search_keyword:str=request.args.get("q","").strip()
    tag_filter:str=request.args.get("tag","").strip()
    posts_query=Post.query

    if search_keyword:
        normalized_keyword=search_keyword.lower().lstrip("#")
        search_pattern = f"%{normalized_keyword}%"
        posts_query = posts_query.filter(
            or_(
                db.func.lower(Post.title).ilike(search_pattern),
                db.func.lower(Post.content).ilike(search_pattern),
                Post.tags.any(db.func.lower(Tag.name).ilike(search_pattern))
            )
        )
    
    if tag_filter:
        normalized_tag=tag_filter.lower().lstrip("#")
        posts_query=posts_query.filter(
            Post.tags.any(db.func.lower(Tag.name)==normalized_tag)
        )

    all_posts = posts_query.order_by(Post.created_at.desc()).all()
    for p in all_posts:
        p.author_profile = Profile_data.query.filter_by(user_id=p.user_id).first()
        
    return render_template(
        "forum_home.html", 
        posts=all_posts, 
        q=search_keyword, 
        tag=tag_filter
    )

@forum_bp.route("/p/<int:post_id>")
def post_detail(post_id):
    post=Post.query.get_or_404(post_id) # Query the post from the database and return to the 404 page if not found
    author_profile = Profile_data.query.filter_by(user_id=post.user_id).first()

    for c in post.comments:
        c.profile= Profile_data.query.filter_by(user_id=c.user_id).first()
    return render_template("post_detail.html",post=post,author_profile=author_profile)

@forum_bp.route("/post/new",methods=["GET","POST"]) #Create a new post, GET displays the form, POST handles the submission
def create_post():
    if request.method=="GET":
        return render_template("create_edit_post.html",
                               mode="create",
                               post=None,
                               existing_tags="")
    
    user_id=session.get("user_id")
    if not user_id:
        flash("Please login first","error")
        return redirect(url_for("login.home"))
    
    #get form data
    title=request.form.get("title","").strip()
    content=request.form.get("content","").strip()
    tags_input=request.form.get("tags","").strip()

#validate data
    if not title or not content:
        flash("Please write your title and content","error")
        return redirect(url_for("forum.create_post"))
    
    new_post=Post(
        title=title,
        content=content,
        user_id=user_id
    )
    db.session.add(new_post)
    db.session.commit()
    
    upload_files = request.files.getlist("media")
    for file in upload_files:
        data = handle_file_upload(file)
        if data:
            new_post.media.append(PostMedia(
                filename=data["filename"],
                filetype=data["filetype"],
                media_url=data["media_url"]
            ))

    for tag in process_tags(tags_input):
        new_post.tags.append(tag)

    db.session.commit()

    socketio.emit("new_post",new_post.to_dict())

    flash("Post Uploaded!","success")
    return redirect(url_for("forum.homepage"))

def process_tags(tag_string):
    tag_objects=[]
    for tag_name in analysis_tag(tag_string):
        tag=Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag=Tag(name=tag_name)
            db.session.add(tag)
        tag_objects.append(tag)
    return tag_objects

@forum_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        post.title = request.form.get("title")
        post.content = request.form.get("content")
        tags_input = request.form.get("tags", "").strip()

        post.tags.clear()
        for tag in process_tags(tags_input):
            post.tags.append(tag)

        delete_ids = request.form.getlist("delete_media_ids")
        for media_id in delete_ids:
            media_obj = PostMedia.query.get(int(media_id))
            if media_obj and media_obj in post.media:
                file_path = os.path.join(current_app.root_path, "static", media_obj.media_url)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.session.delete(media_obj)

        upload_files = request.files.getlist("media")
        for file in upload_files:
            data = handle_file_upload(file)
            if data:
                post.media.append(PostMedia(
                    filename=data["filename"],
                    filetype=data["filetype"],
                    media_url=data["media_url"]
                ))

        db.session.commit()
        flash("POST UPDATED", "success")
        return redirect(url_for("forum.post_detail", post_id=post.id))
    
    existing_tags = " ".join([t.name for t in post.tags])
    return render_template("create_edit_post.html", post=post,existing_tags=existing_tags,mode="edit")

@forum_bp.route("/post/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    post=Post.query.get_or_404(post_id)
    user_id=session.get("user_id")
    if not user_id:
        return {"ok":False,"error":"Please login first"},403
    
    existing_like=Like.query.filter_by(post_id=post.id,user_id=user_id).first()
    if existing_like:
        return {"ok":False,"error":"Already liked"},400
    
    new_like=Like(post=post, user_id=user_id)
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
    post = Post.query.get_or_404(post_id)
    comment_content = request.form.get("body", "").strip()
    comment_author = request.form.get("author", "Anonymous").strip() or "Anonymous"

    if not comment_content:
        return jsonify({"ok": False, "error": "Please write your comment"}), 400

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Please login first"}), 403

    new_comment = Comment(
        post=post,
        body=comment_content,
        author=comment_author,
        user_id=user_id,
    )

    db.session.add(new_comment)
    db.session.commit()

    profile = Profile_data.query.filter_by(user_id=user_id).first()

    response_data = {
        "ok": True,
        "comment_id": new_comment.id,
        "body": comment_content,
        "author": profile.faculty_name if profile else comment_author,
        "avatar_type": profile.avatar_type if profile else 0,
        "created_at": new_comment.created_at.strftime("%Y-%m-%d %H:%M"),
        "is_author": (user_id == post.user_id),
        "total_comment": post.comment_count(),
        "user_id": user_id, 
    }

    socketio.emit("new_comment", {**response_data, "post_id": post_id})

    return jsonify(response_data), 200

@forum_bp.route("/comment/<int:comment_id>/like", methods=["POST"])
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    user_id = session.get("user_id")
    if not user_id:
        return {"ok": False, "error": "Please login first"}, 403

    existing_like = CommentLike.query.filter_by(comment_id=comment.id, user_id=user_id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return {"ok": True, "likes": comment.like_count(), "comment_id": comment.id, "action": "unlike"}

    new_like = CommentLike(comment=comment, user_id=user_id)
    db.session.add(new_like)
    db.session.commit()

    return {"ok": True, "likes": comment.like_count(), "comment_id": comment.id, "action": "like"}

@forum_bp.route("/report/<int:post_id>", methods=["GET", "POST"])
def report_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "GET":
        return render_template("report_post.html", post=post)

    report_reason = request.form.get("report")
    report_details = request.form.get("details", "").strip()

    if not report_reason:
        flash("Please select your reason", "error")
        return redirect(url_for("forum.report_post", post_id=post.id))

    new_report = Report(
        post=post,
        reason=report_reason,
        details=report_details
    )
    db.session.add(new_report)
    db.session.commit()

    flash("Report submitted successfully! Thank you for your feedback.", "success")
    return redirect(url_for("forum.post_detail", post_id=post.id))

@forum_bp.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = session.get("user_id")
    is_admin = session.get("is_admin", False)

    if not (is_admin or post.user_id == user_id):
        flash("You cannot delete this post", "error")
        return redirect(url_for("forum.post_detail", post_id=post.id))
    
    for media in post.media:
        file_path=os.path.join(current_app.root_path,"static",media.media_url)
        if os.path.exists(file_path):
            os.remove(file_path)

    try:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully", "success")
        return redirect(url_for("forum.homepage"))
    except Exception as e:
        db.session.rollback()
        flash("Failed to delete post", "error")
        return redirect(url_for("forum.post_detail", post_id=post.id))

