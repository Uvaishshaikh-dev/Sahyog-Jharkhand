from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChallengeVote(Base):
    __tablename__ = "challenge_votes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # YES = citizen is affected
    # NO = citizen is not affected
    vote: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    challenge = relationship(
        "Challenge",
        back_populates="votes",
    )

    user = relationship("User")

    # One citizen can vote only once per challenge
    __table_args__ = (
        UniqueConstraint(
            "challenge_id",
            "user_id",
            name="uq_challenge_vote_user",
        ),
    )