import os
import pandas as pd
from datetime import datetime, date
from decimal import Decimal

from app import create_app, db
from app.models import Branch, User, FundRecord, AttendanceRecord


WORKBOOK = r"F:\ADMI RECORDS.xlsx"


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def to_date(value):
    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    try:
        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date()
    except Exception:
        return None


def to_money(value):
    if pd.isna(value):
        return Decimal("0.00")

    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except Exception:
        return Decimal("0.00")


print()
print("=" * 90)
print("CHRIST PREACHERS CHURCH - IMPORT DRY RUN")
print("=" * 90)

if not os.path.exists(WORKBOOK):
    raise FileNotFoundError(WORKBOOK)

print("WORKBOOK:", WORKBOOK)
print("EXISTS: YES")

xl = pd.ExcelFile(WORKBOOK)

print()
print("SOURCE SHEETS:")
for sheet in xl.sheet_names:
    print(" -", repr(sheet))

app = create_app()

with app.app_context():

    print()
    print("=" * 90)
    print("DATABASE STATUS")
    print("=" * 90)

    branches = Branch.query.order_by(Branch.id).all()
    users = User.query.order_by(User.id).all()

    print("Branches:", len(branches))
    print("Users:", len(users))
    print("Fund records currently:", FundRecord.query.count())
    print("Attendance records currently:", AttendanceRecord.query.count())

    print()
    print("BRANCH MAP")
    print("-" * 90)

    branch_map = {}

    for branch in branches:
        print(
            "{} | {} | CODE={}".format(
                branch.id,
                branch.name,
                branch.code
            )
        )

        branch_map[branch.name.strip().upper()] = branch
        branch_map[branch.code.strip().upper()] = branch

    print()
    print("USER MAP")
    print("-" * 90)

    for user in users:
        print(
            "ID={} | USER={} | ROLE={} | BRANCH_ID={}".format(
                user.id,
                user.username,
                user.role,
                user.branch_id
            )
        )

    admin_users = [
        u for u in users
        if str(u.role).lower() == "admin"
    ]

    if not admin_users:
        raise RuntimeError(
            "No admin user exists. Import cannot safely assign created_by."
        )

    importer_user = admin_users[0]

    print()
    print(
        "IMPORT CREATOR: ID={} USER={}".format(
            importer_user.id,
            importer_user.username
        )
    )

    # ------------------------------------------------------------
    # FUND SOURCE INSPECTION
    # ------------------------------------------------------------

    print()
    print("=" * 90)
    print("FUND SOURCE SUMMARY")
    print("=" * 90)

    fund_sheets = [
        "N. FUND",
        "EV. FUND",
        "DIRECT PAYMENT",
        "MOMO PAYMENTS",
        "EVG FUND REPORT",
        "Payment analysis",
        " STATEMENT OF ACCOUNT",
        "TRANSFERS",
        "Hubtel momo transfer",
        "MOMO-SOWUTUOM",
        "B. Sheet",
        "BAPTISM",
        "RENTALS",
        "BUILDING PROJ."
    ]

    for sheet in fund_sheets:
        if sheet not in xl.sheet_names:
            print("MISSING:", repr(sheet))
            continue

        df = pd.read_excel(
            WORKBOOK,
            sheet_name=sheet,
            header=None
        )

        print(
            "{:<30} rows={} cols={}".format(
                sheet,
                df.shape[0],
                df.shape[1]
            )
        )

    # ------------------------------------------------------------
    # ATTENDANCE SOURCE
    # ------------------------------------------------------------

    print()
    print("=" * 90)
    print("ATTENDANCE SOURCE")
    print("=" * 90)

    if "ATTENDANCE  REGISTER" in xl.sheet_names:

        attendance_df = pd.read_excel(
            WORKBOOK,
            sheet_name="ATTENDANCE  REGISTER",
            header=None
        )

        print(
            "ATTENDANCE  REGISTER: rows={} cols={}".format(
                attendance_df.shape[0],
                attendance_df.shape[1]
            )
        )

        print()
        print("First non-empty rows:")

        shown = 0

        for i, row in attendance_df.iterrows():

            values = []

            for value in row.tolist():

                if pd.isna(value):
                    continue

                text = str(value).strip()

                if text:
                    values.append(text)

            if values:

                print(
                    "ROW {}: {}".format(
                        i,
                        " | ".join(values[:25])
                    )
                )

                shown += 1

                if shown >= 20:
                    break

    else:
        print("ATTENDANCE REGISTER SHEET NOT FOUND")

    # ------------------------------------------------------------
    # SPECIAL DATA WARNINGS
    # ------------------------------------------------------------

    print()
    print("=" * 90)
    print("DATA WARNINGS")
    print("=" * 90)

    if "MOMO-SOWUTUOM" in xl.sheet_names:

        df = pd.read_excel(
            WORKBOOK,
            sheet_name="MOMO-SOWUTUOM",
            header=None
        )

        for i, row in df.iterrows():

            for value in row.tolist():

                if pd.isna(value):
                    continue

                text = str(value)

                if "2004" in text:
                    print(
                        "POSSIBLE DATE ERROR: MOMO-SOWUTUOM row {} -> {}".format(
                            i,
                            text
                        )
                    )

    # ------------------------------------------------------------
    # EXISTING DATABASE SAFETY
    # ------------------------------------------------------------

    print()
    print("=" * 90)
    print("IMPORT SAFETY CHECK")
    print("=" * 90)

    fund_count = FundRecord.query.count()
    attendance_count = AttendanceRecord.query.count()

    if fund_count != 0 or attendance_count != 0:
        print(
            "WARNING: destination tables are no longer empty."
        )
        print(
            "Fund records:",
            fund_count
        )
        print(
            "Attendance records:",
            attendance_count
        )
    else:
        print(
            "SAFE: fund_records and attendance_records are empty."
        )

    print()
    print("=" * 90)
    print("DRY RUN COMPLETE - NO DATABASE RECORDS WERE CREATED")
    print("=" * 90)
