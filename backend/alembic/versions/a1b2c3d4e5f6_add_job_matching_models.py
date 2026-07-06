"""add job_match, career_insight, learning_path

Revision ID: a1b2c3d4e5f6
Revises: 3d38516328b7
Create Date: 2026-07-06 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '3d38516328b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        'job_matches',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('resume_id', UUID(as_uuid=True), sa.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('job_id', UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('match_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('skills_matched', JSONB(), nullable=True),
        sa.Column('missing_skills', JSONB(), nullable=True),
        sa.Column('ats_compatibility', sa.Float(), nullable=True),
        sa.Column('interview_probability', sa.Float(), nullable=True),
        sa.Column('salary_fit', sa.Float(), nullable=True),
        sa.Column('experience_fit', sa.Float(), nullable=True),
        sa.Column('location_fit', sa.Float(), nullable=True),
        sa.Column('growth_potential', sa.Float(), nullable=True),
        sa.Column('learning_difficulty', sa.String(20), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('is_recommended', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'career_insights',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        sa.Column('resume_health_score', sa.Float(), nullable=True),
        sa.Column('ats_score', sa.Float(), nullable=True),
        sa.Column('technical_strength', sa.Float(), nullable=True),
        sa.Column('communication_score', sa.Float(), nullable=True),
        sa.Column('leadership_score', sa.Float(), nullable=True),
        sa.Column('project_quality', sa.Float(), nullable=True),
        sa.Column('skill_coverage', sa.Float(), nullable=True),
        sa.Column('completeness', sa.Float(), nullable=True),
        sa.Column('readability', sa.Float(), nullable=True),
        sa.Column('industry_alignment', sa.String(100), nullable=True),
        sa.Column('career_level', sa.String(50), nullable=True),
        sa.Column('suggested_skills', JSONB(), nullable=True),
        sa.Column('weak_bullet_points', JSONB(), nullable=True),
        sa.Column('missing_metrics', JSONB(), nullable=True),
        sa.Column('weak_action_verbs', JSONB(), nullable=True),
        sa.Column('formatting_suggestions', JSONB(), nullable=True),
        sa.Column('insights', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'learning_paths',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('skill_name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('difficulty', sa.String(50), nullable=True),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('resources', JSONB(), nullable=True),
        sa.Column('progress', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('estimated_hours', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('learning_paths')
    op.drop_table('career_insights')
    op.drop_table('job_matches')
