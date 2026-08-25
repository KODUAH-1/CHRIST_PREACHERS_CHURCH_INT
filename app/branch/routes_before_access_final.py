from datetime import date, datetime

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

    # Administrators must use the admin dashboard.
    if current_user.is_admin:
        return "Branch dashboard is for branch users.", 403

    # A branch user must belong to a branch.
    if not current_user.branch_id:
        return "No branch is assigned to this user.", 403

    branch_obj = db.session.get(
        Branch,
        current_user.branch_id
    )

    if branch_obj is None:
        return "Branch not found.", 404

    if not branch_obj.is_active:
        return "This branch is currently inactive.", 403

    today = date.today()

    # Today's fund records.
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

    # Today's attendance.
    today_attendance = (
        db.session.query(
            func.coalesce(
                func.sum(AttendanceRecord.attendance),
                0
            )
        )
        .filter(
            AttendanceRecord.branch_id == branch_obj.id,
            AttendanceRecord.record_date == today
        )
        .scalar()
    )

    # Current month.
    month_start = today.replace(day=1)

    monthly_funds = (
        db.session.query(
            func.coalesce(
                func.sum(FundRecord.evangelical_fund),
                0
            ),
            func.coalesce(
                func.sum(FundRecord.national_fund),
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

    monthly_evangelical = monthly_funds[0] or 0
    monthly_national = monthly_funds[1] or 0

    monthly_total_fund = (
        monthly_evangelical +
        monthly_national
    )

    monthly_attendance = (
        db.session.query(
            func.coalesce(
                func.sum(AttendanceRecord.attendance),
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

    # Recent records belonging ONLY to this branch.
    recent_funds = (
        FundRecord.query
        .filter_by(
            branch_id=branch_obj.id
        )
        .order_by(
            FundRecord.record_date.desc(),
            FundRecord.id.desc()
        )
        .limit(10)
        .all()
    )

    recent_attendance = (
        AttendanceRecord.query
        .filter_by(
            branch_id=branch_obj.id
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
