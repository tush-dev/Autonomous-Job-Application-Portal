"""deduplicate job matches and enforce one score per resume/job/user

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
"""
from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DELETE FROM job_matches older
        USING job_matches newer
        WHERE older.resume_id = newer.resume_id
          AND older.job_id = newer.job_id
          AND older.user_id = newer.user_id
          AND older.created_at < newer.created_at
    """)
    op.create_unique_constraint(
        "uq_job_match_resume_job_user",
        "job_matches",
        ["resume_id", "job_id", "user_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_job_match_resume_job_user", "job_matches", type_="unique")
