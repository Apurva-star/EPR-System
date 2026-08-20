from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    @app.route("/")
    def home():
        return render_template("index.html")


    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///epr_portal.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Connect database
    db.init_app(app)

    # Import routes
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp

    # Register routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    # Create database tables
    with app.app_context():
        from app import models as app_models
        db.create_all()

    return app