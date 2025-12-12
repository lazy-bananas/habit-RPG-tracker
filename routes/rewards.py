from flask import Blueprint, request, jsonify
from models import db, User, Reward, UserReward
from datetime import datetime

rewards_bp = Blueprint('rewards', __name__, url_prefix="/rewards")

@rewards_bp.route("/", methods=["GET"])
def list_rewards():
    rewards = Reward.query.all()
    return jsonify([{"id": r.id, "name": r.name, "cost": r.cost} for r in rewards])

@rewards_bp.route("/buy", methods=["POST"])
def buy_reward():
    data = request.get_json()
    user_id = data.get("user_id")
    reward_id = data.get("reward_id")

    user = User.query.get(user_id)
    reward = Reward.query.get(reward_id)

    if not user or not reward:
        return jsonify({"error": "Invalid user or reward"}), 404

    if user.xp < reward.cost:
        return jsonify({"error": "Not enough XP"}), 400

    user.xp -= reward.cost
    db.session.add(UserReward(user_id=user_id, reward_id=reward_id, purchased_at=datetime.utcnow()))
    db.session.commit()

    return jsonify({"message": "Reward purchased successfully", "remaining_xp": user.xp})


@rewards_bp.route("/seed", methods=["POST"])
def seed_rewards():
    default_rewards = [
        Reward(name="1 Hour Gaming Break", cost=50),
        Reward(name="Buy a coffee", cost=30),
        Reward(name="Skip One Habit", cost=100),
        Reward(name="Watch One Episode", cost=80),
        Reward(name="Take a Nap", cost=40),
        Reward(name="Fast Food", cost=30),
        Reward(name="Hang out with friends", cost=100),
        Reward(name="30 Minute social media", cost=30),
        Reward(name="30 Minute Video Game", cost=40),
    ]

    for r in default_rewards:
        db.session.add(r)

    db.session.commit()

    return jsonify({"message": "Rewards seeded!"})
