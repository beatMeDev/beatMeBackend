"""User endpoints"""
from fastapi import APIRouter
from fastapi import Depends
from tortoise.contrib.pydantic import PydanticModel

from app.models.api.user import UserOut
from app.models.db.user import User
from app.services.auth.base import bearer_auth


router = APIRouter()  # pylint: disable-msg=C0103


@router.get("/me/", response_model=UserOut, summary="Get current user info")
async def get_me_route(user_id: str = Depends(bearer_auth)) -> PydanticModel:
    """User information"""
    user: User = await User.get(id=user_id).prefetch_related("auth_accounts")

    return await UserOut.from_tortoise_orm(user)
