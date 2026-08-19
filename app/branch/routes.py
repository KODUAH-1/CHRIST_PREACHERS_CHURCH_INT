from datetime import date

from flask import (
    Blueprint,
    render_template
)

from flask_login import (
    login_required,
    current_user
)

from sqlalchemy import func

from .. import db

from ..models import (
    Branch,
    FundRecord,
    AttendanceRecord
)


branch = Blueprint(
    "branch",
    __name__,
    url_prefix="/branch"
)


@branch.route("/dashboard")
@login_required
def dashboard():

    # -------------------------------------------------
    # ADMIN USERS MUST USE ADMIN DASHBOARD
    # -------------------------------------------------

    if current_user.is_admin:

        return (
            "Administrators must use the administrator dashboard.",
            403
        )


    # -------------------------------------------------
    # BRANCH USER MUST HAVE AN ASSIGNED BRANCH
    # -------------------------------------------------

    if not current_user.branch_id:

        return (
            "No branch is assigned to this user.",
            403
        )


    # -------------------------------------------------
    # LOAD ONLY THE USER'S ASSIGNED BRANCH
    # -------------------------------------------------

    branch_obj = db.session.get(
        Branch,
        current_user.branch_id
    )


    if branch_obj is None:

        return (
            "Assigned branch was not found.",
            404
        )


    # -------------------------------------------------
    # INACTIVE BRANCHES CANNOT BE ACCESSED
    # -------------------------------------------------

    if not branch_obj.is_active:

        return (
            "This branch is currently inactive.",
            403
        )


    today = date.today()


    # -------------------------------------------------
    # TODAY'S FUNDS
    # ONLY THIS USER'S BRANCH
    # -------------------------------------------------

    today_fund = (
        FundRecord.query
        .filter(
            FundRecord.branch_id == branch_obj.id,
            FundRecord.record_date == today
        )
        .all()
    )


    today_evangelical = sum(
        (record.evangelical_fund or 0)
        for record in today_fund
    )


    today_national = sum(
        (record.national_fund or 0)
        for record in today_fund
    )


    today_total_fund = (
        today_evangelical +
        today_national
    )


    # -------------------------------------------------
    # TODAY'S ATTENDANCE
    # ONLY THIS USER'S BRANCH
    # -------------------------------------------------

    today_attendance = (
        db.session.query(
            func.coalesce(
                func.sum(
                    AttendanceRecord.attendance
                ),
                0
            )
        )
        .filter(
            AttendanceRecord.branch_id == branch_obj.id,
            AttendanceRecord.record_date == today
        )
        .scalar()
    )


    # -------------------------------------------------
    # CURRENT MONTH
    # -------------------------------------------------

    month_start = today.replace(
        day=1
    )


    monthly_funds = (
        db.session.query(
            func.coalesce(
                func.sum(
                    FundRecord.evangelical_fund
                ),
                0
            ),
            func.coalesce(
                func.sum(
                    FundRecord.national_fund
                ),
                0
            )
        )
        .filter(
            FundRecord.branch_id == branch_obj.id,
            FundRecord.record_date >= month_start,
            FundRecord.record_date <= today
        )
        .first()
    )


    monthly_evangelical = (
        monthly_funds[0] or 0
    )


    monthly_national = (
        monthly_funds[1] or 0
    )


    monthly_total_fund = (
        monthly_evangelical +
        monthly_national
    )


    monthly_attendance = (
        db.session.query(
            func.coalesce(
                func.sum(
                    AttendanceRecord.attendance
                ),
                0
            )
        )
        .filter(
            AttendanceRecord.branch_id == branch_obj.id,
            AttendanceRecord.record_date >= month_start,
            AttendanceRecord.record_date <= today
        )
        .scalar()
    )


    # -------------------------------------------------
    # RECENT FUNDS
    # ONLY THIS BRANCH
    # -------------------------------------------------

    recent_funds = (
        FundRecord.query
        .filter(
            FundRecord.branch_id == branch_obj.id
        )
        .order_by(
            FundRecord.record_date.desc(),
            FundRecord.id.desc()
        )
        .limit(10)
        .all()
    )


    # -------------------------------------------------
    # RECENT ATTENDANCE
    # ONLY THIS BRANCH
    # -------------------------------------------------

    recent_attendance = (
        AttendanceRecord.query
        .filter(
            AttendanceRecord.branch_id == branch_obj.id
        )
        .order_by(
            AttendanceRecord.record_date.desc(),
            AttendanceRecord.id.desc()
        )
        .limit(10)
        .all()
    )


    return render_template(
        "branch/dashboard.html",

        branch=branch_obj,

        today=today,

        today_evangelical=today_evangelical,

        today_national=today_national,

        today_total_fund=today_total_fund,

        today_attendance=today_attendance,

        monthly_evangelical=monthly_evangelical,

        monthly_national=monthly_national,

        monthly_total_fund=monthly_total_fund,

        monthly_attendance=monthly_attendance,

        recent_funds=recent_funds,

        recent_attendance=recent_attendance
    )
