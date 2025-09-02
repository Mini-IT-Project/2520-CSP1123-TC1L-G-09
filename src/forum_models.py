from datetime import datetime
from extensions import db

post_tags=db.Table(
    'post_tags',
    db.Column('post_id',db.Integer,db.ForeignKey('posts.id'),primary_key=True),
    db.Column('tag_id',db.Integer,db.ForeignKey('tags.id'),primary_key=True)
)

class User(db.Model):
    __tablename__="users"
    id= db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True,nullable=False)
    def __repr__(self):
        return f"<User {self.username}>"

class Post(db.Model):
    __tablename__='posts'

    id = db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    content=db.Column(db.Text,nullable=False)
    media_url = db.Column(db.String(300), nullable=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)

    tags= db.relationship('Tag',secondary=post_tags,back_populates='posts')
    likes=db.relationship('Like',back_populates='post',cascade='all,delete-orphan')
    comments=db.relationship('Comment',back_populates='post',cascade='all,delete-orphan')
    reports=db.relationship('Report',back_populates='post',cascade='all,delete-orphan')

    def like_count(self):
        return len(self.likes)
    
    def comment_count(self):
        return len(self.comments)

    def to_dict(self):
        return{
            'id':self.id,
            'title':self.title,
            'content':(self.content[:200] .rstrip() + '...')if len(self.content)>200 else self.content,
            'media_url': self.media_url,
            'created_at':self.created_at.isoformat(),
            'updated_at':self.updated_at.isoformat() if self.updated_at else None,
            'tags':[t.name for t in self.tags],
            'likes':self.like_count(),
            'comments':self.comment_count()
        }

class Tag (db.Model):
    __tablename__='tags'

    id = db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True,index=True,nullable=False)

    posts=db.relationship('Post',secondary=post_tags,back_populates='tags')

class Like(db.Model):
    __tablename__='likes'
    id = db.Column(db.Integer,primary_key=True)
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'),nullable=False)
    post=db.relationship('Post',back_populates='likes')

class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer,primary_key=True)
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'),nullable=False)
    author=db.Column(db.String(50),default='Anon')
    body=db.Column(db.Text,nullable=False)
    create_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    post=db.relationship('Post',back_populates='comments')
    
class Report(db.Model):
    __tablename__='reports'

    id = db.Column(db.Integer,primary_key=True)
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'),nullable=False)
    reason=db.Column(db.String(300),nullable=False)
    create_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    post=db.relationship('Post',back_populates='reports')