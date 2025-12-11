from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, AvatarList, UserAvatar

avatar_bp = Blueprint("avatar", __name__, url_prefix="/avatar")


# Access list of available avatars
@avatar_bp.route("/list", methods=["GET"])
def list_avatars():
    avatars = AvatarList.query.all()
    return jsonify([
        {
            "avatar_id": a.avatar_id,
            "filename": a.filename,
            "url": f"/static/avatars/{a.filename}"
        }
        for a in avatars
    ]), 200


# User selects an avatar
@avatar_bp.route("/select", methods=["POST"])
@jwt_required()
def select_avatar():
    user_id = int(get_jwt_identity())

    data = request.get_json()
    avatar_id = data.get("avatar_id")

    if not avatar_id:
        return jsonify({"error": "avatar_id is required"}), 400

    avatar = AvatarList.query.get(avatar_id)
    if not avatar:
        return jsonify({"error": "Avatar does not exist"}), 404

    # Check if record exists
    user_avatar = UserAvatar.query.filter_by(user_id=user_id).first()

    if not user_avatar:
        user_avatar = UserAvatar(user_id=user_id, avatar_id=avatar_id)
        db.session.add(user_avatar)
    else:
        user_avatar.avatar_id = avatar_id

    db.session.commit()

    return jsonify({"message": "Avatar updated successfully"}), 200
