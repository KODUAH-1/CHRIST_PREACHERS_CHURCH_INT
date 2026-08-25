from datetime import datetime, date
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Branch(db.Model):
    __tablename__ = "branches"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    location = db.Column(db.String(200))
    code = db.Column(db.String(50), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    users = db.relationship(
        "User",
        back_populates="branch",
        lazy=True
    )

    fund_records = db.relationship(
        "FundRecord",
        back_populates="branch",
        lazy=True
    )

    attendance_records = db.relationship(
        "AttendanceRecord",
        back_populates="branch",
        lazy=True
    )

    def __repr__(self):
        return f"<Branch {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="branch"
    )

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey("branches.id"),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    branch = db.relationship(
        "Branch",
        back_populates="users"
    )

    fund_records = db.relationship(
        "FundRecord",
        back_populates="created_by_user",
        lazy=True
    )

    attendance_records = db.relationship(
        "AttendanceRecord",
        back_populates="created_by_user",
        lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    @property
    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username}>"


class FundRecord(db.Model):
    __tablename__ = "fund_records"

    id = db.Column(db.Integer, primary_key=True)

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey("branches.id"),
        nullable=False,
        index=True
    )

    record_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today,
        index=True
    )

    evangelical_fund = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    national_fund = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00")
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    branch = db.relationship(
        "Branch",
        back_populates="fund_records"
    )

    created_by_user = db.relationship(
        "User",
        back_populates="fund_records"
    )

    @property
    def total_fund(self):
        return (
            self.evangelical_fund +
            self.national_fund
        )

    def __repr__(self):
        return f"<FundRecord {self.record_date}>"


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey("branches.id"),
        nullable=False,
        index=True
    )

    record_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today,
        index=True
    )

    attendance = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    branch = db.relationship(
        "Branch",
        back_populates="attendance_records"
    )

    created_by_user = db.relationship(
        "User",
        back_populates="attendance_records"
    )

    def __repr__(self):
        return f"<AttendanceRecord {self.record_date}>"
