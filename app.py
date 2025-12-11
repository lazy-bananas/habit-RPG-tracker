from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import db, TokenBlocklist
from config import Config
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request
from datetime import timedelta
from routes.auth import auth_bp
from routes.habits import habits_bp
from routes.rewards import rewards_bp
from routes.avatar import avatar_bp
import os


from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")
print("Loading from:", dotenv_path)

load_dotenv(dotenv_path)


app = Flask(__name__)
app.config.from_object(Config)

# Access token short (minutes), Refresh token long (days)
app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', timedelta(minutes=15))
app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))


db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app)

jwt = JWTManager(app)
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload.get("jti")
    if jti is None:
        return True
    exists = TokenBlocklist.query.filter_by(jti=jti).first()
    return bool(exists)  # True => token is revoked

# Custom revoked token response
@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {"msg": "Token has been revoked"}, 401



app.register_blueprint(auth_bp)
app.register_blueprint(habits_bp)
app.register_blueprint(rewards_bp)
app.register_blueprint(avatar_bp)

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
