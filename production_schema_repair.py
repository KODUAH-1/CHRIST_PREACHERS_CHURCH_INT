from app import create_app, db
from sqlalchemy import inspect, text

app = create_app()

with app.app_context():
    print("\n========== SAFE PRODUCTION DATABASE REPAIR ==========")

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    print("Tables found:")
    for table in tables:
        print(" -", table)

    # -------------------------------------------------
    # USERS
    # -------------------------------------------------
    if "users" not in tables:
        raise RuntimeError("users table does not exist. STOPPING.")

    inspector = inspect(db.engine)
    user_columns = [c["name"] for c in inspector.get_columns("users")]

    print("\nUSERS COLUMNS BEFORE:")
    print(user_columns)

    with db.engine.begin() as conn:

        if "id" not in user_columns:
            print("\nusers.id is missing. Repairing...")

            conn.execute(text(
                "ALTER TABLE users ADD COLUMN id INTEGER"
            ))

            conn.execute(text("""
                CREATE SEQUENCE IF NOT EXISTS users_id_seq
            """))

            conn.execute(text("""
                ALTER SEQUENCE users_id_seq
                OWNED BY users.id
            """))

            conn.execute(text("""
                ALTER TABLE users
                ALTER COLUMN id
                SET DEFAULT nextval('users_id_seq')
            """))

            max_id = conn.execute(text(
                "SELECT COALESCE(MAX(id), 0) FROM users"
            )).scalar()

            conn.execute(
                text("SELECT setval('users_id_seq', :value, false)"),
                {"value": max_id + 1}
            )

            conn.execute(text("""
                UPDATE users
                SET id = nextval('users_id_seq')
                WHERE id IS NULL
            """))

            conn.execute(text("""
                ALTER TABLE users
                ALTER COLUMN id SET NOT NULL
            """))

            conn.execute(text("""
                ALTER TABLE users
                ADD CONSTRAINT users_pkey_repaired
                PRIMARY KEY (id)
            """))

            print("users.id successfully repaired.")

        else:
            print("\nusers.id already exists. No change required.")

    # -------------------------------------------------
    # ATTENDANCE
    # -------------------------------------------------
    inspector = inspect(db.engine)

    if "attendance_records" in inspector.get_table_names():

        attendance_columns = [
            c["name"]
            for c in inspector.get_columns("attendance_records")
        ]

        print("\nATTENDANCE COLUMNS BEFORE:")
        print(attendance_columns)

        with db.engine.begin() as conn:

            if "male" not in attendance_columns:
                conn.execute(text("""
                    ALTER TABLE attendance_records
                    ADD COLUMN male INTEGER NOT NULL DEFAULT 0
                """))
                print("Added attendance_records.male")

            if "female" not in attendance_columns:
                conn.execute(text("""
                    ALTER TABLE attendance_records
                    ADD COLUMN female INTEGER NOT NULL DEFAULT 0
                """))
                print("Added attendance_records.female")

            if "attendance" not in attendance_columns:
                conn.execute(text("""
                    ALTER TABLE attendance_records
                    ADD COLUMN attendance INTEGER NOT NULL DEFAULT 0
                """))
                print("Added attendance_records.attendance")

            conn.execute(text("""
                UPDATE attendance_records
                SET attendance =
                    COALESCE(male, 0) + COALESCE(female, 0)
            """))

            print("Attendance totals synchronized.")

    # -------------------------------------------------
    # FUNDS
    # -------------------------------------------------
    inspector = inspect(db.engine)

    if "fund_records" in inspector.get_table_names():

        fund_columns = [
            c["name"]
            for c in inspector.get_columns("fund_records")
        ]

        print("\nFUND COLUMNS BEFORE:")
        print(fund_columns)

        with db.engine.begin() as conn:

            if "evangelical_fund" not in fund_columns:
                conn.execute(text("""
                    ALTER TABLE fund_records
                    ADD COLUMN evangelical_fund
                    NUMERIC(12,2) NOT NULL DEFAULT 0.00
                """))
                print("Added fund_records.evangelical_fund")

            if "national_fund" not in fund_columns:
                conn.execute(text("""
                    ALTER TABLE fund_records
                    ADD COLUMN national_fund
                    NUMERIC(12,2) NOT NULL DEFAULT 0.00
                """))
                print("Added fund_records.national_fund")

    # -------------------------------------------------
    # FINAL VERIFICATION
    # -------------------------------------------------
    inspector = inspect(db.engine)

    print("\n========== FINAL DATABASE SCHEMA ==========")

    for table in [
        "users",
        "branches",
        "attendance_records",
        "fund_records"
    ]:
        if table in inspector.get_table_names():
            columns = [
                c["name"]
                for c in inspector.get_columns(table)
            ]
            print(table, ":", columns)
        else:
            print(table, ": MISSING")

    print("\n========== ALEMBIC VERSION ==========")

    if "alembic_version" in inspector.get_table_names():
        with db.engine.connect() as conn:
            version = conn.execute(
                text("SELECT version_num FROM alembic_version")
            ).fetchall()

            print(version)
    else:
        print("alembic_version table missing")

    print("\n========== DATABASE REPAIR FINISHED ==========")
