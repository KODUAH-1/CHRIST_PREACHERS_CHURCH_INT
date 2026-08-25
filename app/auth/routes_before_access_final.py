from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)

from .. import db
from ..models import User
from .forms import AdminSetupForm, LoginForm


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@auth.route("/setup", methods=["GET", "POST"])
def setup():
    existing_admin = User.query.filter_by(
        role="admin"
    ).first()

    if existing_admin:
        flash(
            "Administrator setup has already been completed.",
            "warning"
        )
        return redirect(url_for("auth.login"))

    form = AdminSetupForm()

    if form.validate_on_submit():
        username = form.username.data.strip()

        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:
            flash(
                "That username is already in use.",
                "danger"
            )
            return render_template(
                "auth/setup.html",
                form=form
            )

        admin = User(
            username=username,
            role="admin",
            is_active=True
        )

        admin.set_password(form.password.data)

        db.session.add(admin)
        db.session.commit()

        flash(
            "Administrator account created successfully. "
            "You can now log in.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/setup.html",
        form=form
    )


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()

        user = User.query.filter_by(
            username=username
        ).first()

        if (
            user
            and user.is_active
            and user.check_password(form.password.data)
        ):
            login_user(user)

            if user.is_admin:
                return redirect(
                    url_for("admin.dashboard")
                )

            return redirect(
                url_for("branch.dashboard")
            )

        flash(
            "Invalid username or password.",
            "danger"
        )

    return render_template(
        "auth/login.html",
        form=form
    )


@auth.route("/logout")
@login_required
def logout():
    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("auth.login"))
