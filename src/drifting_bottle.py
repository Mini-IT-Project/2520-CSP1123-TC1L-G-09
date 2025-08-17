from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from datatime import datetime

drifting_bottle = Flask(__name__)

app.config['SQLALCHEMY_DATABSE_URI']='sqlite///bottles.db'
app.config['SQLALCHEMY_TRACK-MODIFICATIONS']=  False

db = SQLAlchemy(app)

class Bottle(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text,nullable=False)
    status = db.Column(db.String(20),default='unpicked')
    created_at = db.Column(db.DateTime,default=datatime.utcnow)

    def __repr__(self):
        return f'<Bottle {self.id}-{{self.status}>}'

@app.route('/')
def index():
    return render_template('index.html')

with app.app_context():
    db.create_all()
    print("Database created successfully!")

if __name__ == "__main__":
    app.run(debug=True)