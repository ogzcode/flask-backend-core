from flask import request, jsonify, g
from functools import wraps
import jwt
from app import app
from app.models import User
from app.services.user_services import UserServices


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = UserServices.get_user_by_id(data["id"])

        except Exception as e:
            print(e)
            return jsonify({"error": "Token is invalid"}), 401
        
        g.current_user = current_user

        return f(*args, **kwargs)
    
    return decorated