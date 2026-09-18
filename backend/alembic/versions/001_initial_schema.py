"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-16 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. Job Preferences
    op.create_table(
        'job_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('keywords', sa.JSON(), nullable=False),
        sa.Column('locations', sa.JSON(), nullable=False),
        sa.Column('employment_types', sa.JSON(), nullable=False),
        sa.Column('work_modes', sa.JSON(), nullable=False),
        sa.Column('min_salary', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('max_salary', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_job_preferences_id'), 'job_preferences', ['id'], unique=False)

    # 3. Sources
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('base_url', sa.String(length=500), nullable=False),
        sa.Column('source_type', sa.Enum('HTML', 'API', 'BROWSER', name='sourcetype'), nullable=False),
        sa.Column('scraper_type', sa.String(length=100), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('rate_limit_delay', sa.Numeric(precision=5, scale=2), nullable=False, server_default='1.5'),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sources_enabled'), 'sources', ['enabled'], unique=False)
    op.create_index(op.f('ix_sources_id'), 'sources', ['id'], unique=False)
    op.create_index(op.f('ix_sources_name'), 'sources', ['name'], unique=True)

    # 4. Scraper Runs
    op.create_table(
        'scraper_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'SUCCESS', 'FAILED', name='scraperrunstatus'), nullable=False),
        sa.Column('pages_fetched', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duplicates_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraper_runs_id'), 'scraper_runs', ['id'], unique=False)
    op.create_index(op.f('ix_scraper_runs_source_id'), 'scraper_runs', ['source_id'], unique=False)
    op.create_index(op.f('ix_scraper_runs_status'), 'scraper_runs', ['status'], unique=False)

    # 5. Jobs
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('canonical_url', sa.String(length=1000), nullable=False),
        sa.Column('employment_type', sa.Enum('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP', 'TEMPORARY', 'OTHER', name='employmenttype'), nullable=False),
        sa.Column('work_mode', sa.Enum('REMOTE', 'HYBRID', 'ON_SITE', 'UNSPECIFIED', name='workmode'), nullable=False),
        sa.Column('salary_min', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('salary_max', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('dedupe_hash', sa.String(length=64), nullable=False),
        sa.Column('raw_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dedupe_hash'),
        sa.UniqueConstraint('source_id', 'external_id', name='uq_source_external_id')
    )
    op.create_index(op.f('ix_jobs_canonical_url'), 'jobs', ['canonical_url'], unique=False)
    op.create_index(op.f('ix_jobs_company'), 'jobs', ['company'], unique=False)
    op.create_index(op.f('ix_jobs_dedupe_hash'), 'jobs', ['dedupe_hash'], unique=True)
    op.create_index(op.f('ix_jobs_employment_type'), 'jobs', ['employment_type'], unique=False)
    op.create_index(op.f('ix_jobs_external_id'), 'jobs', ['external_id'], unique=False)
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)
    op.create_index(op.f('ix_jobs_is_active'), 'jobs', ['is_active'], unique=False)
    op.create_index(op.f('ix_jobs_location'), 'jobs', ['location'], unique=False)
    op.create_index(op.f('ix_jobs_posted_at'), 'jobs', ['posted_at'], unique=False)
    op.create_index(op.f('ix_jobs_source_id'), 'jobs', ['source_id'], unique=False)
    op.create_index(op.f('ix_jobs_title'), 'jobs', ['title'], unique=False)
    op.create_index(op.f('ix_jobs_work_mode'), 'jobs', ['work_mode'], unique=False)
    op.create_index('idx_jobs_company_title', 'jobs', ['company', 'title'], unique=False)
    op.create_index('idx_jobs_posted_active', 'jobs', ['posted_at', 'is_active'], unique=False)

    # 6. Saved Jobs
    op.create_table(
        'saved_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('saved_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_user_saved_job')
    )
    op.create_index(op.f('ix_saved_jobs_id'), 'saved_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_saved_jobs_job_id'), 'saved_jobs', ['job_id'], unique=False)
    op.create_index(op.f('ix_saved_jobs_user_id'), 'saved_jobs', ['user_id'], unique=False)

    # 7. Job Applications
    op.create_table(
        'job_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('INTERESTED', 'APPLIED', 'INTERVIEW', 'REJECTED', 'OFFER', 'WITHDRAWN', name='applicationstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_user_job_application')
    )
    op.create_index(op.f('ix_job_applications_id'), 'job_applications', ['id'], unique=False)
    op.create_index(op.f('ix_job_applications_job_id'), 'job_applications', ['job_id'], unique=False)
    op.create_index(op.f('ix_job_applications_status'), 'job_applications', ['status'], unique=False)
    op.create_index(op.f('ix_job_applications_user_id'), 'job_applications', ['user_id'], unique=False)

    # 8. Notification Configs
    op.create_table(
        'notification_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('webhook_secret', sa.String(length=255), nullable=True),
        sa.Column('min_match_score', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_notification_configs_id'), 'notification_configs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('notification_configs')
    op.drop_table('job_applications')
    op.drop_table('saved_jobs')
    op.drop_table('jobs')
    op.drop_table('scraper_runs')
    op.drop_table('sources')
    op.drop_table('job_preferences')
    op.drop_table('users')
