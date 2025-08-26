from flask import Flask
from main import main_bp
from bottle_feature import bottle_bp

app = Flask(__name__)

app.register_blueprint(main_bp, url_prefix="/")
app.register_blueprint(bottle_bp, url_prefix="/bottle")

if __name__ == "__main__":
    app.run(debug=True)
