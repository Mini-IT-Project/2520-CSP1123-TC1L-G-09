from flask import Blueprint,render_template,session,redirect,url_for, flash,request
from extensions import db
from forum_models import Comment,Post,Like
from login import Users

profile_bp = Blueprint(
    "profile",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/forum-static"
)

class Profile_data(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    avatar_type= db.Column(db.Integer, nullable=False, default=0)
    campus_name= db.Column(db.String(200), nullable=False, default=' ')
    degree_name= db.Column(db.String(200), nullable=False, default=' ')
    faculty_name= db.Column(db.String(200), nullable=False, default=' ')

@profile_bp.route("/", methods=['GET', 'POST'])
def myProfile():
    user_id = session.get("user_id")
    print("user_id from session:", user_id)

    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    print(user)
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    myprofile_data= Profile_data.query.filter_by(user_id=user_id).first()
    if not myprofile_data:
        myprofile_data= Profile_data(user_id=user_id)
        db.session.add(myprofile_data)
        db.session.commit()
    print (myprofile_data)

    if request.method=='POST':
        myprofile_data.avatar_type = request.form.get("avatar_type")
        myprofile_data.campus_name= request.form.get("campus")
        myprofile_data.degree_name= request.form.get("degree")
        myprofile_data.faculty_name= request.form.get("faculty")

        db.session.commit()

    return render_template("myProfile.html", myprofile_data=myprofile_data, user=user)

@profile_bp.route("/history")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    myprofile_data= Profile_data.query.filter_by(user_id=user_id).first()
        
    return render_template("profile.html", myprofile_data=myprofile_data,user=user)

@profile_bp.route("/Settings")
def settings():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    user = Users.query.get(user_id) 
    if not user:
        flash("Please login in first.")
        return redirect(url_for('login.home'))
    
    return render_template("settings.html")