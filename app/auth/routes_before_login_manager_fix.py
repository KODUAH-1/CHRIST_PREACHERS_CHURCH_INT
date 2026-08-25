from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from .forms import LoginForm
from ..models import User


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:

        if current_user.is_admin:
            return redirect(
                url_for("admin.dashboard")
            )

        if current_user.branch_id:
            return redirect(
                url_for("branch.dashboard")
            )

        logout_user()

        flash(
            "Your account is not assigned to a branch.",
            "danger"
        )

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data.strip()

        user = User.query.filter_by(
            username=username
        ).first()

        if not user:

            flash(
                "Invalid username or password.",
                "danger"
            )

            return render_template(
                "auth/login.html",
                form=form
            )

        if not user.is_active:

            flash(
                "This user account is inactive.",
                "danger"
            )

            return render_template(
                "auth/login.html",
                form=form
            )

        if not user.check_password(
            form.password.data
        ):

            flash(
                "Invalid username or password.",
                "danger"
            )

            return render_template(
                "auth/login.html",
                form=form
            )

        # -------------------------------------------------
        # ADMIN LOGIN
        # -------------------------------------------------

        if user.is_admin:

            login_user(user)

            return redirect(
                url_for("admin.dashboard")
            )

        # -------------------------------------------------
        # BRANCH USER LOGIN
        # -------------------------------------------------

        if not user.branch_id:

            flash(
                "This user has not been assigned to a branch.",
                "danger"
            )

            return render_template(
                "auth/login.html",
                form=form
            )

        login_user(user)

        return redirect(
            url_for("branch.dashboard")
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

    return redirect(
        url_for("auth.login")
    )
