from flask import Blueprint, request, jsonify
from models import db, User, Password, Habit, TokenBlocklist
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from datetime import date

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")
bcrypt = Bcrypt()

@auth_bp.route("/", methods=["GET"])
def auth_home():
    return jsonify({"message": "Auth blueprint working!"})


def load_default_habits(user_id):
    defaults = [
        ("Running", "good", "physical"),
        ("Meditation", "good", "mental"),
        ("Drinking Water", "good", "physical"),
        ("Bad Sleep", "bad", "physical"),
        ("Eating Junk Food", "bad", "physical"),
        ("Doomscrolling", "bad", "mental"),
    ]

    for name, t, n in defaults:
        exists = Habit.query.filter_by(user_id=user_id, name=name).first()
        if not exists:
            db.session.add(Habit(
                user_id=user_id,
                name=name,
                habit_type=t,
                habit_nature=n,
                xp_value=10
            ))

    db.session.commit()


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

        load_default_habits(user.user_id)

        return jsonify({"message": "Signup successful", "user_id": user.user_id}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "User already exists"}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    pw_entry = Password.query.filter_by(user_id=user.user_id).first()
    if not pw_entry or not bcrypt.check_password_hash(pw_entry.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
    

    today = date.today()
    if user.last_alive != today:
        # increment days_active (field named days_alive in your models)
        user.days_alive = (user.days_alive or 0) + 1
        user.last_alive = today

    db.session.commit()

    # create tokens
    access_token = create_access_token(identity=str(user.user_id), additional_claims={"username": user.username})
    refresh_token = create_refresh_token(identity=str(user.user_id))

    return jsonify({
        "message": "Login successful",
        "user_id": user.user_id,
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

# Use refresh token to get a new access token
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = int(get_jwt_identity())
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200

# Logout: revoke the refresh token (and optionally access token)
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()  # any valid token required (access or refresh)
def logout():
    jti = get_jwt().get("jti")
    if not jti:
        return jsonify({"msg": "No token jti found"}), 400
    # add JTI to blocklist
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    return jsonify({"message": "Logged out successfully"}), 200    #Tokens revoked 

# Example protected route that demonstrates persistent-check
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "xp": user.xp,
        "level": user.level,
        "level_name": user.level_name,
        "mana": user.mana,
        "health": user.health,
        "days_alive": user.days_alive,
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak
    })

@auth_bp.route("/test-post", methods=["POST"])
def test_post():
    data = request.get_json()
    return {"received": data}, 200
