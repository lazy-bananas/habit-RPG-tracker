from flask import Blueprint, request, jsonify
from models import db, User, Password
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")
bcrypt = Bcrypt()

@auth_bp.route("/", methods=["GET"])
def auth_home():
    return jsonify({"message": "Auth blueprint working!"})

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    print("signup hit:", data)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        print("Creating user...")
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.flush()  # to get user.id before commit
        print("Created user with id:", user.user_id)

        print("Creating password...")
        hash_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        print("creating password entry...")
        pw_entry = Password(user_id=user.user_id, password_hash=hash_pw)
        db.session.add(pw_entry)
        print("Committing...")
        db.session.commit()
        print("Commit successful")

        return jsonify({"message": "Signup successful", "user_id": user.user_id}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "User already exists"}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    pw_entry = Password.query.filter_by(user_id=user.user_id).first()
    if pw_entry and bcrypt.check_password_hash(pw_entry.password_hash, password):
        return jsonify({"message": "Login successful", "user_id": user.user_id}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/test-post", methods=["POST"])
def test_post():
    data = request.get_json()
    return {"received": data}, 200
