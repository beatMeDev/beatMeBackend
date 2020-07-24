"""Auth middleware"""
from typing import Any
from typing import Dict
from typing import Optional

import jwt

from fastapi.responses import ORJSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from orjson import loads  # pylint: disable-msg=E0611
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.extensions import redis_client
from app.settings import JWT_ALGORITHM
from app.settings import JWT_SECRET
from app.utils.exceptions import UnauthorizedError


class TokenAuthMiddleware(BaseHTTPMiddleware):
    """Check user credentials."""
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        authorization: str = request.headers.get("Authorization")

        if not authorization:
            return await call_next(request)

        scheme, token = get_authorization_scheme_param(authorization)  # pylint: disable=unused-variable

        if not token:
            return await call_next(request)

        request.scope.update({"token": token})

        try:
            jwt.decode(jwt=token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return ORJSONResponse(
                status_code=UnauthorizedError.status_code,
                content=UnauthorizedError.detail,
            )

        raw_token_data: bytes = await redis_client.get(token)

        if not raw_token_data:
            return ORJSONResponse(
                status_code=UnauthorizedError.status_code,
                content=UnauthorizedError.detail,
            )

        token_data: Dict[str, Any] = loads(raw_token_data)
        user_id: Optional[str] = token_data.get("user_id")

        request.scope.update({"user_id": user_id, "token_data": token_data})
        response: Response = await call_next(request)

        return response
