from flask import Blueprint, request, jsonify
from models import db, User, Habit, UserStreak, WeeklyProgress
from datetime import date, timedelta
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

habits_bp = Blueprint('habits', __name__, url_prefix="/habits")

@habits_bp.route("/", methods=["GET"])
@jwt_required()
def list_habits():
    user_id = int(get_jwt_identity())
    habits = Habit.query.filter_by(user_id=user_id, done_today = False).all()
    return jsonify([
        {"id": h.id, "user_id": h.user_id, "name": h.name, "habit_type": h.habit_type, "habit_nature": h.habit_nature,
         "xp_value": h.xp_value, "streak": h.streak, "last_done": str(h.last_done), "done_today": h.done_today}
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


def update_streak(user_id):
    user = User.query.get(user_id)
    streak = UserStreak.query.filter_by(user_id=user_id).first()

    if streak is None:
        streak = UserStreak(user_id=user_id, current_streak=0, longest_streak=0, last_completed=None)
        db.session.add(streak)
        db.session.commit()

    today = date.today()

    #if streak.last_completed == today:
        #return streak
    
    #if streak.last_completed == today - timedelta(days=1):
    streak.current_streak += 1
    #else:
        #streak.current_streak = 1

    streak.last_completed = today
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    
    db.session.commit()

    return streak


#def update_user_streak(user_id):
    user = User.query.get(user_id)
    return update_streak(user)

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
    if habit.habit_type == "good":
        user.xp += habit.xp_value
    elif habit.habit_type == "bad":
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
    #if habit.last_done == today - timedelta(days=1):
    habit.streak += 1
    #else:
        #habit.streak = 1
    habit.last_done = today
    habit.done_today = True

    # longest streak update
    habit.longest_streak = max(habit.longest_streak, habit.streak)

    # uodating weekly progress
    update_weekly_progress(user.user_id, habit)

    # level update
    user.level = calculate_level(user.xp)
    
    level_names = [
        "Dormant Beginner",
        "Reluctant Starter",
        "Awakening Novice",
        "Weary Wanderer",
        "Determined Wanderer",
        "Focused Adept",
        "Steady Attendant",
        "Resolute Attendant",
        "Disciplined Attendant",
        "Skilled Operative",
        "Advanced Operative",
        "Master Operative"
    ]

    user.level_name = level_names[min(user.level-1,11)]
    streak = update_streak(user.user_id)
    
    db.session.commit()
    return jsonify({"message": "Habit completed",
                    "xp": user.xp,
                    "level": user.level,
                    "rank": user.level_name,
                    "mana": user.mana,
                    "health": user.health,
                    "habit_streak": habit.streak,
                    "habit_longest_streak": habit.longest_streak,
                    "user_streak": streak.current_streak,
                    "user_longest_streak": streak.longest_streak
                    }), 200





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
        #if user.last_login != today:
           # user.active_days += 1
        #user.last_login = today

    for habit in habits:
        habit.done_today = False
        #if habit.last_done != today - timedelta(days=1):
           # habit.streak = 0
        #else:
          #  habit.streak += 1

    db.session.commit()
    return jsonify({"message": "Daily reset complete"})



@habits_bp.route("/<int:habit_id>", methods=["DELETE"])
@jwt_required()
def delete_habit(habit_id):
    user_id = int(get_jwt_identity())

    habit = Habit.query.get(habit_id)

    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    # Make sure user owns this habit
    if habit.user_id != user_id:
        return jsonify({"error": "You are not allowed to delete this habit"}), 403

    db.session.delete(habit)
    db.session.commit()

    return jsonify({"message": "Habit deleted successfully"}), 200


def update_weekly_progress(user_id, habit):
    today = date.today()

    # Week starts on Monday
    week_start = today - timedelta(days=today.weekday())

    record = WeeklyProgress.query.filter_by(
        user_id=user_id,
        week_start=week_start
    ).first()

    if not record:
        record = WeeklyProgress(
            user_id=user_id,
            week_start=week_start
        )
        db.session.add(record)

    record.habits_completed += 1

    if habit.habit_type == "good":
        record.good_habits += 1
        record.xp_gained += habit.xp_value
    else:
        record.bad_habits += 1
        record.xp_gained -= habit.xp_value


    db.session.commit()



@habits_bp.route("/weekly", methods=["GET"])
@jwt_required()
def get_weekly_progress():
    user_id = int(get_jwt_identity())
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    record = WeeklyProgress.query.filter_by(
        user_id=user_id,
        week_start=week_start
    ).first()

    if not record:
        return jsonify({
            "week_start": str(week_start),
            "habits_completed": 0,
            "good_habits": 0,
            "bad_habits": 0,
            "xp_gained": 0
        }), 200

    return jsonify({
        "week_start": str(record.week_start),
        "habits_completed": record.habits_completed,
        "good_habits": record.good_habits,
        "bad_habits": record.bad_habits,
        "xp_gained": record.xp_gained
    }), 200
