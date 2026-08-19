from flask import Flask, request, jsonify

app = Flask(__name__)

# Temporary storage for users
users = []


# Home API
@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to EPR System API"
    })


# Registration API
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # Check if any field is missing
    if not username or not email or not password:
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    # Check if email already exists
    for user in users:
        if user["email"] == email:
            return jsonify({
                "success": False,
                "message": "Email already registered"
            }), 400

    # Store user
    users.append({
        "username": username,
        "email": email,
        "password": password
    })

    return jsonify({
        "success": True,
        "message": "Registration successful"
    }), 201


# Login API
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    # Check user
    for user in users:
        if user["email"] == email and user["password"] == password:
            return jsonify({
                "success": True,
                "message": "Login successful",
                "username": user["username"]
            }), 200

    return jsonify({
        "success": False,
        "message": "Invalid email or password"
    }), 401


if __name__ == "__main__":
    app.run(debug=True)