from flask import Blueprint, request, jsonify
from models import db, User, Habit
from datetime import date, timedelta
from flask import request

habits_bp = Blueprint('habits', __name__, url_prefix="/habits")

@habits_bp.route("/", methods=["GET"])
def list_habits():
    habits = Habit.query.all()
    return jsonify([
        {"id": h.id, "user_id": h.user_id, "name": h.name, "habit_type": h.habit_type, "habit_nature": h.habit_nature,
         "xp_value": h.xp_value, "streak": h.streak, "last_done": str(h.last_done)}
        for h in habits
    ])

@habits_bp.route("/", methods=["POST"])
def create_habit():
    data = request.get_json()
    user_id = data.get("user_id")
    name = data.get("name")
    habit_type = data.get("habit_type")  # 'good' or 'bad'
    habit_nature = data.get("habit_nature")
    xp_value = data.get("xp_value", 10)
    cover_photo = data.get("cover_photo")

    if not all([user_id, name, habit_type, habit_nature ]):
        return jsonify({"error": "Missing fields"}), 400
    
    habit = Habit(user_id=user_id, name=name, habit_type=habit_type, habit_nature=habit_nature,xp_value=xp_value, cover_photo=cover_photo)
    db.session.add(habit)
    db.session.commit()
    return jsonify({"message": "Habit created", "habit_id": habit.id, "user_id": habit.user_id}), 201


def calculate_level(xp):
    level = 1
    while xp >= 50 * (level ** 2):
        level += 1
    return level


@habits_bp.route("/<int:habit_id>/done", methods=["POST"])
def mark_done(habit_id):
    habit = Habit.query.get(habit_id)
    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    user = User.query.get(habit.user_id)
    today = date.today()

    if habit.done_today:
        return jsonify({"message": "Habit already done today"}), 400

    # XP logic
    if habit.type == "good":
        user.xp += habit.xp_value
    elif habit.type == "bad":
        user.xp -= habit.xp_value
        user.xp = max(user.xp, 0)  # prevent negative XP


    # mana / health system
    if habit.habit_nature=="mental":
        user.mana -= 10 if habit.habit_type == "good" else 15
        user.mana = max(user.mana, 0)
    else:
        user.health -= 10 if habit.habit_type == "good" else 15
        user.health = max(user.health, 0)

    # streak update
    if habit.last_done == today - timedelta(days=1):
        habit.streak += 1
    else:
        habit.streak = 1
    habit.last_done = today
    habit.done_today = True

    # longest streak update
    habit.longest_streak = max(habit.longest_streak, habit.streak)



    # level update
    user.level = calculate_level(user.xp)
    
    level_names = [
        "Unrepentant Slacker",
        "Persistent Slacker",
        "Recovering Slacker",
        "Depressed Drone",
        "Demoralised Drone",
        "Dead-Eye Drone",
        "Bored Attendant",
        "Resigned Attendant",
        "Obedient Attendant",
        "Competent Operative",
        "Engaged Operative",
        "Committed Operative"
    ]

    user.level_name = level_names[min(user.level-1,11)]
    db.session.commit()
    return jsonify({"message": "Habit completed",
                    "xp": user.xp,
                    "level": user.level,
                    "rank": user.level_name,
                    "mana": user.mana,
                    "health": user.health,
                    "streak": habit.streak,
                    "longest_streak": habit.longest_streak}), 200





@habits_bp.route("/daily_reset", methods=["POST"])
def daily_reset():
    today = date.today()

    users = User.query.all()
    habits = Habit.query.all()

    for user in users:
        # Daily energy refill (based on level)
        user.max_mana = 100 + (user.level - 1) * 10
        user.max_health = 100 + (user.level - 1) * 10

        user.mana = user.max_mana
        user.health = user.max_health

        # Count active days
        if user.last_login != today:
            user.active_days += 1
        user.last_login = today

    for habit in habits:
        habit.done_today = False
        if habit.last_done != today - timedelta(days=1):
            habit.streak = 0

    db.session.commit()
    return jsonify({"message": "Daily reset complete"})
