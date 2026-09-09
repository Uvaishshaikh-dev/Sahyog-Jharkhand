"""add challenge votes

Revision ID: add_challenge_votes
Revises: c47aec1491fa
Create Date: 2026-09-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_challenge_votes"
down_revision = "f09273927bfb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "challenge_votes",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "challenge_id",
            sa.Integer(),
            sa.ForeignKey(
                "challenges.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey(
                "users.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "vote",
            sa.String(length=10),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "challenge_id",
            "user_id",
            name="uq_challenge_vote_user",
        ),
    )

    op.create_index(
        "ix_challenge_votes_id",
        "challenge_votes",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_challenge_votes_challenge_id",
        "challenge_votes",
        ["challenge_id"],
        unique=False,
    )

    op.create_index(
        "ix_challenge_votes_user_id",
        "challenge_votes",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_challenge_votes_user_id",
        table_name="challenge_votes",
    )

    op.drop_index(
        "ix_challenge_votes_challenge_id",
        table_name="challenge_votes",
    )

    op.drop_index(
        "ix_challenge_votes_id",
        table_name="challenge_votes",
    )

    op.drop_table("challenge_votes")