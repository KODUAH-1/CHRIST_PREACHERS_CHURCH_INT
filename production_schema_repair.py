from app import create_app, db
from sqlalchemy import inspect, text

app = create_app()

with app.app_context():
    print("\n========== FINAL PRODUCTION SCHEMA REPAIR ==========")

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    print("Existing tables:")
    for table in tables:
        print(" -", table)

    # =========================================================
    # BRANCHES: reconcile old production schema with new model
    # =========================================================
    if "branches" not in tables:
        raise RuntimeError("branches table is missing. STOPPING.")

    inspector = inspect(db.engine)
    branch_columns = [c["name"] for c in inspector.get_columns("branches")]

    print("\nBRANCH COLUMNS BEFORE:")
    print(branch_columns)

    with db.engine.begin() as conn:

        if "name" not in branch_columns:
            conn.execute(text("""
                ALTER TABLE branches
                ADD COLUMN name VARCHAR(150)
            """))
            print("Added branches.name")

        if "code" not in branch_columns:
            conn.execute(text("""
                ALTER TABLE branches
                ADD COLUMN code VARCHAR(50)
            """))
            print("Added branches.code")

        if "is_active" not in branch_columns:
            conn.execute(text("""
                ALTER TABLE branches
                ADD COLUMN is_active BOOLEAN
            """))
            print("Added branches.is_active")

        if "branch_name" in branch_columns:
            conn.execute(text("""
                UPDATE branches
                SET name = COALESCE(name, branch_name)
                WHERE name IS NULL
            """))

        if "branch_code" in branch_columns:
            conn.execute(text("""
                UPDATE branches
                SET code = COALESCE(code, branch_code)
                WHERE code IS NULL
            """))

        if "status" in branch_columns:
            conn.execute(text("""
                UPDATE branches
                SET is_active =
                    CASE
                        WHEN LOWER(CAST(status AS TEXT)) IN
                            ('active', '1', 'true', 'yes')
                        THEN TRUE
                        ELSE FALSE
                    END
                WHERE is_active IS NULL
            """))

        conn.execute(text("""
            UPDATE branches
            SET is_active = TRUE
            WHERE is_active IS NULL
        """))

        conn.execute(text("""
            UPDATE branches
            SET name = COALESCE(name, 'Unnamed Branch')
            WHERE name IS NULL
        """))

        conn.execute(text("""
            UPDATE branches
            SET code = COALESCE(code, 'BR-' || id::TEXT)
            WHERE code IS NULL
        """))

    # =========================================================
    # USERS: reconcile old production schema with new model
    # =========================================================
    inspector = inspect(db.engine)
    user_columns = [c["name"] for c in inspector.get_columns("users")]

    print("\nUSER COLUMNS BEFORE:")
    print(user_columns)

    with db.engine.begin() as conn:

        if "password_hash" not in user_columns:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN password_hash VARCHAR(255)
            """))
            print("Added users.password_hash")

        if "branch_id" not in user_columns:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN branch_id INTEGER
            """))
            print("Added users.branch_id")

        if "is_active" not in user_columns:
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN is_active BOOLEAN
            """))
            print("Added users.is_active")

        # Preserve existing password hashes.
        if "pw_hash" in user_columns:
            conn.execute(text("""
                UPDATE users
                SET password_hash = pw_hash
                WHERE password_hash IS NULL
                  AND pw_hash IS NOT NULL
            """))

        # Map the old branch field to the new branch_id.
        if "branch" in user_columns:
            conn.execute(text("""
                UPDATE users u
                SET branch_id = b.id
                FROM branches b
                WHERE u.branch_id IS NULL
                  AND (
                      CAST(u.branch AS TEXT) = CAST(b.id AS TEXT)
                      OR CAST(u.branch AS TEXT) = CAST(b.code AS TEXT)
                      OR LOWER(TRIM(CAST(u.branch AS TEXT))) =
                         LOWER(TRIM(CAST(b.name AS TEXT)))
                  )
            """))

            # Try the original production branch_code as well.
            conn.execute(text("""
                UPDATE users u
                SET branch_id = b.id
                FROM branches b
                WHERE u.branch_id IS NULL
                  AND EXISTS (
                      SELECT 1
                      FROM information_schema.columns
                      WHERE table_name = 'branches'
                        AND column_name = 'branch_code'
                  )
                  AND CAST(u.branch AS TEXT) = CAST(b.branch_code AS TEXT)
            """))

        # Preserve existing account status.
        if "status" in user_columns:
            conn.execute(text("""
                UPDATE users
                SET is_active =
                    CASE
                        WHEN LOWER(CAST(status AS TEXT)) IN
                            ('active', '1', 'true', 'yes')
                        THEN TRUE
                        ELSE FALSE
                    END
                WHERE is_active IS NULL
            """))

        conn.execute(text("""
            UPDATE users
            SET is_active = TRUE
            WHERE is_active IS NULL
        """))

    # =========================================================
    # Ensure missing application tables are created.
    # Existing tables are NOT dropped.
    # =========================================================
    print("\n========== CREATING MISSING APPLICATION TABLES ==========")

    db.create_all()

    # =========================================================
    # Final inspection
    # =========================================================
    inspector = inspect(db.engine)

    print("\n========== FINAL USERS SCHEMA ==========")
    print([
        c["name"]
        for c in inspector.get_columns("users")
    ])

    print("\n========== FINAL BRANCHES SCHEMA ==========")
    print([
        c["name"]
        for c in inspector.get_columns("branches")
    ])

    for table in ["attendance_records", "fund_records"]:
        if table in inspector.get_table_names():
            print(f"\n========== {table.upper()} SCHEMA ==========")
            print([
                c["name"]
                for c in inspector.get_columns(table)
            ])
        else:
            print(f"\n{table}: STILL MISSING")

    # =========================================================
    # Verification counts
    # =========================================================
    with db.engine.connect() as conn:
        users = conn.execute(
            text("SELECT COUNT(*) FROM users")
        ).scalar()

        password_ready = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM users
                WHERE password_hash IS NOT NULL
            """)
        ).scalar()

        branch_ready = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM users
                WHERE branch_id IS NOT NULL
            """)
        ).scalar()

        branches = conn.execute(
            text("SELECT COUNT(*) FROM branches")
        ).scalar()

        print("\n========== DATA VERIFICATION ==========")
        print("Users:", users)
        print("Users with password_hash:", password_ready)
        print("Users with branch_id:", branch_ready)
        print("Branches:", branches)

    print("\n========== PRODUCTION REPAIR COMPLETE ==========")
