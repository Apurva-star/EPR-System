from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder="../templates")
    @app.route("/")
    def home():
        return render_template("index.html")


    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///epr_portal.db?timeout=30"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Connect database
    db.init_app(app)

    # Import routes
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    from app.routes.sales import sales_bp

    # Register routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(sales_bp)

    # Create database tables
    with app.app_context():
        from app import models as app_models
        from app.models import Category

        db.create_all()

        if Category.query.count() == 0:
            categories = [
                Category(category_name="Rigid"),
                Category(category_name="Flexible"),
                Category(category_name="MLP"),
                Category(category_name="Bio")
            ]

            db.session.add_all(categories)
            db.session.commit()

    return app