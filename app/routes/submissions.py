"""Submissions endpoints"""
from uuid import UUID

from fastapi import APIRouter
from tortoise.contrib.pydantic import PydanticModel

from app.models.api.submission import SubmissionOut
from app.models.api.vote import VoteCount
from app.models.db import Submission
from app.models.db import Vote


submissions_router = APIRouter()  # pylint: disable-msg=C0103


@submissions_router.get("/{submission_id}/votes/", response_model=VoteCount)
async def get_submission_votes_route(submission_id: UUID) -> VoteCount:
    """Get submission votes"""
    count: int = await Vote.filter(submission_id=submission_id).count()

    response = VoteCount(count=count)

    return response


@submissions_router.get(
    "/{submission_id}/", response_model=SubmissionOut, summary="Submission details",
)
async def get_submission_route(submission_id: UUID) -> PydanticModel:
    """Get submission by id."""
    submission: Submission = await Submission.get(id=submission_id)

    response = await SubmissionOut.from_tortoise_orm(submission)

    return response
