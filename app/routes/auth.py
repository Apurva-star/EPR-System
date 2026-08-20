from flask import Blueprint, request, jsonify
from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


# Registration API
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        }), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Check required fields
    if not username or not email or not password:
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    # Check existing user
    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "Email already registered"
        }), 400

    # Create user
    new_user = User(
        username=username,
        email=email,
        password=password
    )

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": new_user.to_dict()
    }), 201


# Login API
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    # Find user by email
    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # Check password
    if user.password != password:
        return jsonify({
            "success": False,
            "message": "Invalid password"
        }), 401

    return jsonify({
        "success": True,
        "message": "Login successful",
        "username": user.username
    }), 200


# Logout API
@auth_bp.route("/logout", methods=["POST"])
def logout():

    return jsonify({
        "success": True,
        "message": "Logout successful"
    }), 200