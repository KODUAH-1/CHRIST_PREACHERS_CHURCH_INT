import os

from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    load_dotenv(override=True)

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "development-secret-key"
    )

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is missing from the .env file."
        )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Load models so Flask-Migrate can detect them.
    from . import models

    # Authentication
    from .auth.routes import auth, login_manager

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."
    login_manager.login_message_category = "warning"

    app.register_blueprint(auth)

    # Admin
    from .admin.routes import admin
    app.register_blueprint(admin)

    # Branch
    from .branch.routes import branch
    app.register_blueprint(branch)

    @app.route("/")
    def home():
        return redirect(url_for("auth.login"))

    return app
