# backend/routes/user_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User
from ..schemas import UserSchema

user_bp = Blueprint('users', __name__, url_prefix='/users')
user_schema = UserSchema() # Instance of the schema

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user_schema.dump(user)), 200

# Add other routes as needed (e.g., update user profile)