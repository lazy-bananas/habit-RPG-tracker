from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import db
from config import Config
from flask_migrate import Migrate
from routes.auth import auth_bp
from routes.habits import habits_bp
from routes.rewards import rewards_bp
import os


from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")
print("Loading from:", dotenv_path)

load_dotenv(dotenv_path)


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app)


app.register_blueprint(auth_bp)
app.register_blueprint(habits_bp)
app.register_blueprint(rewards_bp)

@app.route('/')
def home():
    return "Welcome to Habit RPG Tracker! Flask backend is running successfully."

with app.app_context():
    try:
        db.create_all()
        print("Database tables created (Render compatible).")
    except Exception as e:
        print("Error creating tables:", e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
