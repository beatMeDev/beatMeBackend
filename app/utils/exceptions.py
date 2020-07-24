from fastapi import HTTPException
from pydantic import BaseModel


class ExceptionModel(BaseModel):
    error: str = "InternalError"
    message: str = "internal error"


BadRequestError = HTTPException(
    status_code=400, detail={"error": "BadRequest", "message": "Params are wrong"}
)
UnauthorizedError = HTTPException(
    status_code=401, detail={"error": "Unauthorized", "message": "Session is wrong"}
)
PermissionsDeniedError = HTTPException(
    status_code=403,
    detail={"error": "PermissionsDenied", "message": "You have no enough rights"},
)
NotFoundError = HTTPException(
    status_code=404, detail={"error": "NotFound", "message": "Item is not exists"}
)
UnsupportedProviderError = HTTPException(
    status_code=400,
    detail={"error": "UnsupportedProvider", "message": "Provider is not supported yet"},
)
