"""Challenges endpoints"""
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from tortoise.contrib.pydantic import PydanticModel

from app.models.api.challenge import ChallengeIn, ChallengeOut, ChallengeListOut, ChallengeList
from app.models.db import Challenge
from app.services.auth.base import bearer_auth
from app.utils.db import Paginate

challenges_router = APIRouter()  # pylint: disable-msg=C0103


@challenges_router.post("/", response_model=ChallengeOut)
async def create_playlist_route(
        challenge_data: ChallengeIn,
        user_id: str = Depends(bearer_auth)
) -> PydanticModel:
    """
    Create challenge.
    :param challenge_data: challenge data
    :param user_id: current user id
    :return: response
    """
    challenge_data.challenge_end = challenge_data.challenge_end.replace(tzinfo=None)
    challenge_data.vote_end = challenge_data.vote_end.replace(tzinfo=None)
    challenge_dict: Dict[str, Any] = challenge_data.dict()
    challenge_dict["owner_id"] = user_id
    challenge: Challenge = await Challenge.create(**challenge_dict)
    await challenge.participants.add(challenge.owner)

    response: PydanticModel = await ChallengeOut.from_tortoise_orm(challenge)

    return response


@challenges_router.get("/", response_model=ChallengeListOut, summary="Return public challenges")
async def get_public_challenges_route(
        pagination: Paginate = Depends(Paginate),
) -> ChallengeListOut:
    """
    Return public challenges
    :param pagination: pagination class
    :param user_id: current user id
    :return: challenges
    """
    queryset = Challenge.filter(is_public=True)
    count, items = await pagination.paginate(
        queryset=queryset,
        serializer=ChallengeList,
    )
    response = ChallengeListOut(count=count, items=items)

    return response


@challenges_router.get("/my/", response_model=ChallengeListOut, summary="Return own challenges")
async def get_my_challenges_route(
        pagination: Paginate = Depends(Paginate),
        user_id: str = Depends(bearer_auth),
) -> ChallengeListOut:
    """
    Return user own challenges
    :param pagination: pagination class
    :param user_id: current user id
    :return: challenges
    """
    queryset = Challenge.filter(owner_id=user_id)
    count, items = await pagination.paginate(
        queryset=queryset,
        serializer=ChallengeList,
    )
    response = ChallengeListOut(count=count, items=items)

    return response


@challenges_router.get(
    "/participant/",
    response_model=ChallengeListOut,
    summary="Return participants challenges",
)
async def get_participant_challenges_route(
        pagination: Paginate = Depends(Paginate),
        user_id: str = Depends(bearer_auth),
) -> ChallengeListOut:
    """
    Return challenges where user is participant
    :param pagination: pagination class
    :param user_id: current user id
    :return: challenges
    """
    queryset = Challenge.filter(participants__id=user_id)
    count, items = await pagination.paginate(
        queryset=queryset,
        serializer=ChallengeList,
    )
    response = ChallengeListOut(count=count, items=items)

    return response


@challenges_router.get("/{challenge_id}/", response_model=ChallengeOut, summary="Return challenge")
async def get_challenge_route(
        challenge_id: UUID,
        secret: Optional[str] = None,
) -> PydanticModel:
    """
    Return challenge details
    :param challenge_id: challenge id
    :param secret: challenge access secret key
    :return: challenge info
    """
    challenge: Challenge = await Challenge.get(id=challenge_id)

    if challenge.is_public is False:
        challenge.check_secret(secret=secret)

    response = await ChallengeOut.from_tortoise_orm(challenge)

    return response
