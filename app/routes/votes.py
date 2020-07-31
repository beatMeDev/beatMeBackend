"""Votes endpoints"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from tortoise.contrib.pydantic import PydanticModel

from app.models.api.vote import VoteIn
from app.models.api.vote import VoteOut
from app.models.db import Submission
from app.models.db import Vote
from app.services.auth.base import bearer_auth


votes_router = APIRouter()  # pylint: disable-msg=C0103


@votes_router.post("/", response_model=VoteOut, summary="Make vote for submission")
async def make_vote_route(
        vote_data: VoteIn, user_id: str = Depends(bearer_auth),
) -> PydanticModel:
    """
    Make vote for a submission.

    If vote for a challenge exists, submission will be changed.
    :param vote_data: vote data(submission_id)
    :param user_id: user's id
    :return: vote
    """
    submission: Submission = await Submission.get(
        id=vote_data.submission_id
    ).prefetch_related("challenge")
    now_time: datetime = datetime.utcnow()

    if now_time < submission.challenge.challenge_end:  # type: ignore
        raise HTTPException(status_code=400, detail={"message": "Too early"})

    vote: Optional[Vote] = await Vote.filter(
        submission__challenge=submission.challenge, user_id=user_id
    ).first()

    if not vote:
        vote = await Vote.create(submission=submission, user_id=user_id)
    else:
        vote.submission = submission
        await vote.save()

    response = await VoteOut.from_tortoise_orm(vote)

    return response
