"""Add children and attendance week number

Revision ID: adad3226b9a8
Revises: c6376d2e2b74
Create Date: 2026-08-25 20:02:08.027717
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adad3226b9a8'
down_revision = 'c6376d2e2b74'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns temporarily nullable so existing attendance records
    # can be safely populated before NOT NULL is enforced.
    with op.batch_alter_table('attendance_records', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('children', sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column('week_number', sa.Integer(), nullable=True)
        )

    # Preserve all existing attendance records.
    # Existing children are assumed to be zero where no children data exists.
    op.execute("""
        UPDATE attendance_records
        SET children = 0
        WHERE children IS NULL
    """)

    # Calculate week of month from the existing attendance date.
    # Days 1-7   = Week 1
    # Days 8-14  = Week 2
    # Days 15-21 = Week 3
    # Days 22-28 = Week 4
    # Days 29-31 = Week 5
    op.execute("""
        UPDATE attendance_records
        SET week_number =
            CASE
                WHEN EXTRACT(DAY FROM record_date) BETWEEN 1 AND 7 THEN 1
                WHEN EXTRACT(DAY FROM record_date) BETWEEN 8 AND 14 THEN 2
                WHEN EXTRACT(DAY FROM record_date) BETWEEN 15 AND 21 THEN 3
                WHEN EXTRACT(DAY FROM record_date) BETWEEN 22 AND 28 THEN 4
                ELSE 5
            END
        WHERE week_number IS NULL
    """)

    # Enforce the model's non-null requirements after existing data
    # has been safely populated.
    with op.batch_alter_table('attendance_records', schema=None) as batch_op:
        batch_op.alter_column(
            'children',
            existing_type=sa.Integer(),
            nullable=False
        )
        batch_op.alter_column(
            'week_number',
            existing_type=sa.Integer(),
            nullable=False
        )


def downgrade():
    with op.batch_alter_table('attendance_records', schema=None) as batch_op:
        batch_op.drop_column('week_number')
        batch_op.drop_column('children')
