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
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print("SECRET_KEY →", os.getenv("SECRET_KEY"))
        print("DATABASE_URI →", os.getenv("DATABASE_URI"))
        print("JWT_SECRET_KEY →", os.getenv("JWT_SECRET_KEY"))
    with app.app_context():
        db.create_all()
    app.run(debug=True)
