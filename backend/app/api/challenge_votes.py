from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import SessionLocal

from app.models.challenge import Challenge
from app.models.challenge_vote import ChallengeVote
from app.models.user import User, UserRole


router = APIRouter(
    prefix="/api/v1/challenge-votes",
    tags=["Community Impact Validation"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_role_value(user: User):
    if isinstance(user.role, UserRole):
        return user.role.value

    return str(user.role)


def get_challenge(
    challenge_id: int,
    db: Session,
):
    challenge = (
        db.query(Challenge)
        .filter(Challenge.id == challenge_id)
        .first()
    )

    if challenge is None:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found",
        )

    return challenge


# ---------------------------------------------------------
# CAST / UPDATE VOTE
# ---------------------------------------------------------

@router.post("/{challenge_id}")
def cast_vote(
    challenge_id: int,
    vote: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Allow a citizen to validate whether they are affected
    by a particular societal problem.

    A citizen can have only one vote per challenge.
    """

    role = get_role_value(current_user)

    if role != UserRole.CITIZEN.value:
        raise HTTPException(
            status_code=403,
            detail="Only citizens can validate community impact",
        )

    challenge = get_challenge(
        challenge_id,
        db,
    )

    vote = vote.strip().upper()

    if vote not in {"YES", "NO"}:
        raise HTTPException(
            status_code=400,
            detail="Vote must be YES or NO",
        )

    existing_vote = (
        db.query(ChallengeVote)
        .filter(
            ChallengeVote.challenge_id == challenge_id,
            ChallengeVote.user_id == current_user.id,
        )
        .first()
    )

    if existing_vote:
        existing_vote.vote = vote
    else:
        new_vote = ChallengeVote(
            challenge_id=challenge_id,
            user_id=current_user.id,
            vote=vote,
        )

        db.add(new_vote)

    db.commit()

    return {
        "message": "Community validation recorded successfully",
        "challenge_id": challenge_id,
        "vote": vote,
    }


# ---------------------------------------------------------
# GET COMMUNITY VALIDATION
# ---------------------------------------------------------

@router.get("/{challenge_id}")
def get_vote_results(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get community validation results for a challenge.
    """

    challenge = get_challenge(
        challenge_id,
        db,
    )

    role = get_role_value(current_user)

    allowed_roles = {
        UserRole.CITIZEN.value,
        UserRole.COMMUNITY_ORG.value,
        UserRole.HEI_ADMIN.value,
        UserRole.FACULTY.value,
        UserRole.STUDENT.value,
        UserRole.SCIENTIST.value,
        UserRole.INDUSTRY_ADMIN.value,
        UserRole.GOVERNMENT.value,
        UserRole.SUPER_ADMIN.value,
    }

    if role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view community validation",
        )

    yes_votes = (
        db.query(func.count(ChallengeVote.id))
        .filter(
            ChallengeVote.challenge_id == challenge_id,
            ChallengeVote.vote == "YES",
        )
        .scalar()
        or 0
    )

    no_votes = (
        db.query(func.count(ChallengeVote.id))
        .filter(
            ChallengeVote.challenge_id == challenge_id,
            ChallengeVote.vote == "NO",
        )
        .scalar()
        or 0
    )

    total_votes = yes_votes + no_votes

    if total_votes > 0:
        validation_score = round(
            (yes_votes / total_votes) * 100,
            2,
        )
    else:
        validation_score = 0

    user_vote = (
        db.query(ChallengeVote)
        .filter(
            ChallengeVote.challenge_id == challenge_id,
            ChallengeVote.user_id == current_user.id,
        )
        .first()
    )

    return {
        "challenge_id": challenge_id,
        "yes_votes": yes_votes,
        "no_votes": no_votes,
        "total_votes": total_votes,
        "validation_score": validation_score,
        "user_vote": user_vote.vote if user_vote else None,
    }