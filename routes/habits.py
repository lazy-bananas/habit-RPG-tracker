from flask import Blueprint, request, jsonify
from models import db, User, Habit
from datetime import date, timedelta
from flask import request

habits_bp = Blueprint('habits', __name__, url_prefix="/habits")

@habits_bp.route("/", methods=["GET"])
def list_habits():
    habits = Habit.query.all()
    return jsonify([
        {"id": h.id, "user_id": h.user_id, "name": h.name, "type": h.type,
         "xp_value": h.xp_value, "streak": h.streak, "last_done": str(h.last_done)}
        for h in habits
    ])

@habits_bp.route("/", methods=["POST"])
def create_habit():
    data = request.get_json()
    user_id = data.get("user_id")
    name = data.get("name")
    type_ = data.get("type")  # 'good' or 'bad'
    xp_value = data.get("xp_value", 10)
    cover_photo = data.get("cover_photo")

    if not all([user_id, name, type_]):
        return jsonify({"error": "Missing fields"}), 400
    
    habit = Habit(user_id=user_id, name=name, type=type_, xp_value=xp_value, cover_photo=cover_photo)
    db.session.add(habit)
    db.session.commit()
    return jsonify({"message": "Habit created", "habit_id": habit.id, "user_id": habit.user_id}), 201


@habits_bp.route("/<int:habit_id>/done", methods=["POST"])
def mark_done(habit_id):
    habit = Habit.query.get(habit_id)
    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    user = User.query.get(habit.user_id)
    today = date.today()

    # XP logic
    if habit.type == "good":
        user.xp += habit.xp_value
    elif habit.type == "bad":
        user.xp -= habit.xp_value
        user.xp = max(user.xp, 0)  # prevent negative XP

    # streak update
    if habit.last_done == today - timedelta(days=1):
        habit.streak += 1
    else:
        habit.streak = 1
    habit.last_done = today

    # level update
    user.level = user.xp // 100 + 1

    db.session.commit()
    return jsonify({"message": "Updated XP and streak", "new_xp": user.xp, "level": user.level})
