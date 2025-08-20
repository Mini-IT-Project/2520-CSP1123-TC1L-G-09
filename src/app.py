from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bottles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Bottle(db.Model):
    __tablename__ = 'bottles_table'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unpicked')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Bottle {self.id} - {self.status}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/throw', methods=['POST'])
def throw():
    content = request.form.get('content')
    if content:
        new_bottle = Bottle(content=content)
        db.session.add(new_bottle)
        db.session.commit()
    return redirect(url_for('index'))

###def pick

@app.route("/debug/count")
def debug_count():
    return {"bottles_count": Bottle.query.count()}

with app.app_context():
    db.create_all()
    print("Database created successfully!")

if __name__ == "__main__":
    app.run(debug=True)