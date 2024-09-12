import jwt
import datetime
from app import app
from flask import Blueprint, request, jsonify
from app.services import UserService

auth_routes = Blueprint("auth_routes", __name__)


@auth_routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data["username"] or not data["email"] or not data["password"]:
        return jsonify({"message": "Missing data"}), 400

    try:
        user = UserService.create_user(
            data["username"], data["email"], data["password"])
    except Exception as e:
        return jsonify({"message": "User already exists"})

    return jsonify(user), 201


@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    data = request.get_json()

    if not data["email"] or not data["password"]:
        return jsonify({"message": "Missing data"}), 400

    user = UserService.get_user_by_email(data["email"])

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.check_password(data["password"]):
        return jsonify({"message": "Invalid password"}), 401

    token = jwt.encode(
        {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        },
        app.config["SECRET_KEY"]
    )

    return jsonify({
        "token": token,
        "user": user
        }), 200
