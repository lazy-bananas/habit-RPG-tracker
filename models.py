from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

db = SQLAlchemy()

# ---------------------- USER TABLE ----------------------
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    avatar = db.Column(db.String(100))

    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    level_name = db.Column(db.String(50), default="Dormant Beginner")

    mana = db.Column(db.Integer, default=50)
    max_mana = db.Column(db.Integer, default=50)

    health = db.Column(db.Integer, default=50)
    max_health = db.Column(db.Integer, default=50)

    days_alive = db.Column(db.Integer, default=0)
    last_alive = db.Column(db.Date, default=date.today())
    # Relationship with password
    password = db.relationship("Password", backref="user", uselist=False)


# ---------------------- PASSWORD TABLE ----------------------
class Password(db.Model):
    __tablename__ = 'passwords'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


# ---------------------- HABIT TABLE ----------------------
class Habit(db.Model):
    __tablename__ = 'habits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    habit_type = db.Column(db.String(10), nullable=False)  # good or bad
    habit_nature = db.Column(db.String(20), nullable=False)   # physical or mental
    xp_value = db.Column(db.Integer, default=10)
    cover_photo = db.Column(db.String(100))
    streak = db.Column(db.Integer, default=0)
    last_done = db.Column(db.Date)
    longest_streak = db.Column(db.Integer, default=0)
    done_today = db.Column(db.Boolean, default=False)


# ---------------------- REWARD TABLES ----------------------
class Reward(db.Model):
    __tablename__ = 'rewards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Integer, nullable=False)


class UserReward(db.Model):
    __tablename__ = 'user_rewards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey("rewards.id"), nullable=False)
    purchased_at = db.Column(db.DateTime)


# ---------------------- TOKEN BLOCKLIST TABLE ----------------------
class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)  # JWT ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

#----------------------- USER STREAK TABLE ----------------------
class UserStreak(db.Model):
    __tablename__ = "user_streaks"

    streak_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)

    last_completed = db.Column(db.Date, default=None)

    user = db.relationship("User", backref="streak_data", uselist=False)



#----------------------- AVATAR LIST TABLE ----------------------
class AvatarList(db.Model):
    __tablename__ = "avatar_list"

    avatar_id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)  # e.g. "warrior.png"


#----------------------- USER AVATAR TABLE ----------------------
class UserAvatar(db.Model):
    __tablename__ = "user_avatars"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    avatar_id = db.Column(db.Integer, db.ForeignKey("avatar_list.avatar_id"), nullable=False)
