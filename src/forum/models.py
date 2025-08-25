from datetime import datetime
from extensions import db

post_tags=db.Table(
    'post_tags',
    db.Column('post_id',db.Integer,db.ForeignKey('posts.id'),primary_key=True),
    db.Column('tag_id',db.Integer,db.ForeignKey('tags.id'),primary_key=True)
)

class Post(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(200),nullable=False)
    content = db.Column(db.Text,nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at=db.Column(db.Datetimr, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags= db.relationship('Tag', secondary=post_tags, back_populates='posts')
    reports=db.relationship('Report',back_populates='post',cascade='all,delete-orphan')

    def to_dict(self):
        return{
            'id':self.id,
            'title':self.title,
            'content':(self.content[:200] .rstrip() + '...')if len(self.content)>200 else self.content,
            'created_at':self.created_at.isoformat(),
            'updated_at':self.updated_at.isoformat() if self.updated_at else None,
            'tags':[t.name for t in self.tags]
        }