"""Test pre running stuff"""
import warnings

from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import AsyncGenerator
from typing import Dict
from typing import Optional
from uuid import UUID
from uuid import uuid4

import pytest

from asyncpg import ObjectInUseError
from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError

from app.models.db import AuthAccount
from app.models.db import Challenge
from app.models.db import Playlist
from app.models.db import Submission
from app.models.db import Text
from app.models.db import Track
from app.models.db import User
from app.models.db import Vote
from app.models.db.user import AuthProvider
from app.services.auth.base import bearer_auth
from app.settings import APP_MODELS
from app.settings import TORTOISE_TEST_DB
from tests.test_services.test_auth.test_base import USER_UUID


with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import imp  # pylint: disable=unused-import


@pytest.fixture(scope="function", autouse=True)
@pytest.mark.asyncio
async def test_db() -> AsyncGenerator:  # type: ignore
    """Initialize db connection before run test."""
    try:
        await Tortoise.init(db_url=TORTOISE_TEST_DB, modules={"models": APP_MODELS})
    except DBConnectionError:
        await Tortoise.init(
            db_url=TORTOISE_TEST_DB, modules={"models": APP_MODELS}, _create_db=True,
        )
    await Tortoise.generate_schemas()

    yield

    try:
        await Tortoise._drop_databases()  # pylint: disable=protected-access
    except ObjectInUseError:
        pass

    await Tortoise.close_connections()


POPULATE_TRACK_ID: str = str(uuid4())


async def bearer_auth_mock() -> str:
    """Auth method mock."""
    return str(USER_UUID)


def mock_auth(application: FastAPI) -> FastAPI:
    """Mock auth dependency and token middleware."""
    application.dependency_overrides[bearer_auth] = bearer_auth_mock

    application.user_middleware = []
    application.middleware_stack = application.build_middleware_stack()

    return application


@pytest.fixture()
@pytest.mark.asyncio
async def populate_texts() -> Text:
    """Populate text for utils routes tests."""
    text, _ = await Text.get_or_create(content="test")
    return text


test_track_info: Dict[str, Any] = {
    "id": POPULATE_TRACK_ID,
    "name": "test",
    "author_name": "test",
    "cover_url": "test",
    "preview_url": "test",
    "youtube_id": "test",
    "spotify_id": "test",
    "recommended": True,
    "meta": {},
}


async def populate_track() -> Track:
    """Populate track for routes tests."""
    track, _ = await Track.get_or_create(**test_track_info)
    return track


@pytest.fixture()
@pytest.mark.asyncio
async def track_fixture() -> Track:
    """Populate track for utils routes tests."""
    return await populate_track()


async def populate_playlist(track: Optional[Track] = None) -> Playlist:
    """Populate playlist with track for routes tests."""
    playlist, _ = await Playlist.get_or_create(
        name="test",
        url="test",
        spotify_id="test",
        recommended=True,
    )

    if not track:
        track = await populate_track()

    await playlist.tracks.add(track)

    return playlist


@pytest.fixture()
@pytest.mark.asyncio
async def playlist_fixture() -> Playlist:
    """Populate playlist with track for routes testing."""
    return await populate_playlist()


async def populate_user(user_id: Optional[UUID] = USER_UUID) -> User:
    """Populate user for routes testing."""
    # if not user_id:
    #     user_id = uuid4()

    user, _ = await User.get_or_create(id=user_id)
    await AuthAccount.get_or_create(
        _id="test",
        name="test",
        image="test",
        url="test",
        provider=AuthProvider.DEFAULT,
        access_token="test",
        refresh_token="test",
        expires=0,
        user=user,
    )
    await user.fetch_related("auth_accounts")

    return user


@pytest.fixture()
@pytest.mark.asyncio
async def user_fixture() -> User:
    """Default user tests fixture."""
    return await populate_user()


POPULATE_CHALLENGE_ID = uuid4()
POPULATE_CHALLENGE_SECRET = Challenge(id=POPULATE_CHALLENGE_ID).secret_key()
POPULATE_CHALLENGE_FOREIGN_ID = uuid4()
POPULATE_CHALLENGE_FOREIGN_SECRET = Challenge(
    id=POPULATE_CHALLENGE_FOREIGN_ID, is_public=False,
).secret_key()


async def populate_challenge(
        challenge_status: str = "process",
        is_public: bool = True,
        user_id: Optional[UUID] = USER_UUID,
        challenge_id: UUID = POPULATE_CHALLENGE_ID,
) -> Challenge:
    """Populate challenge for routes testings."""
    if not user_id:
        user_id = uuid4()

    user: User = await populate_user(user_id=user_id)
    track, _ = await Track.get_or_create(test_track_info)
    await populate_playlist()

    challenge_end = datetime.utcnow() + timedelta(days=1)
    vote_end = datetime.utcnow() + timedelta(days=2)

    if challenge_status == "vote":
        challenge_end = datetime.utcnow() - timedelta(days=1)
        vote_end = datetime.utcnow() + timedelta(days=2)

    if challenge_status == "end":
        challenge_end = datetime.utcnow() - timedelta(days=2)
        vote_end = datetime.utcnow() - timedelta(days=1)

    challenge, _ = await Challenge.get_or_create(
        id=challenge_id,
        name="test",
        challenge_end=challenge_end,
        vote_end=vote_end,
        is_public=is_public,
        owner=user,
        track=track,
    )
    await challenge.participants.add(user)

    return challenge


@pytest.fixture()
@pytest.mark.asyncio
async def challenge_process_fixture() -> Challenge:
    """
    Populate challenge with:
    - Default user
    - Is open
    - Challenge in process
    """
    return await populate_challenge()


@pytest.fixture()
@pytest.mark.asyncio
async def challenge_vote_fixture() -> Challenge:
    """
    Populate challenge with:
    - Default user
    - Is open
    - Challenge in voting
    """
    return await populate_challenge(challenge_status="vote")


@pytest.fixture()
@pytest.mark.asyncio
async def challenge_end_fixture() -> Challenge:
    """
    Populate challenge with:
    - Default user
    - Is open
    - Challenge ended
    """
    return await populate_challenge(challenge_status="end")


@pytest.fixture()
@pytest.mark.asyncio
async def challenge_private_fixture() -> Challenge:
    """
    Populate challenge with:
    - Default user
    - Is private
    - Challenge is open
    """
    return await populate_challenge(is_public=False)


@pytest.fixture()
@pytest.mark.asyncio
async def challenge_foreign_fixture() -> Challenge:
    """
    Populate challenge with:
    - Random user
    - Is private
    - Challenge is open
    """
    return await populate_challenge(
        is_public=False,
        user_id=None,
        challenge_id=POPULATE_CHALLENGE_FOREIGN_ID,
    )


POPULATE_SUBMISSION_ID = uuid4()


async def populate_submission(
        challenge: Challenge,
        submission_id: Optional[UUID] = POPULATE_SUBMISSION_ID,
) -> Submission:
    """Populate submission for routes testing."""
    if not submission_id:
        submission_id = uuid4()

    submission, _ = await Submission.get_or_create(
        id=submission_id,
        url="test",
        challenge=challenge,
        user=challenge.owner,
    )

    return submission


@pytest.fixture()
@pytest.mark.asyncio
async def submission_fixture() -> Submission:
    """
    Populate submission with:
    - Default user
    - Challenge in process
    - Challenge is open
    """
    challenge: Challenge = await populate_challenge()

    return await populate_submission(challenge=challenge)


@pytest.fixture()
@pytest.mark.asyncio
async def submission_vote_fixture() -> Submission:
    """
    Populate submission with:
    - Default user
    - Challenge is voting
    - Challenge is open
    """
    challenge: Challenge = await populate_challenge(challenge_status="vote")

    return await populate_submission(challenge=challenge)


@pytest.fixture()
@pytest.mark.asyncio
async def submission_ended_fixture() -> Submission:
    """
    Populate submission with:
    - Default user
    - Challenge is ended
    - Challenge is open
    """
    challenge: Challenge = await populate_challenge(challenge_status="end")

    return await populate_submission(challenge=challenge)


async def populate_vote(submission: Submission) -> Vote:
    """Populate vote for routes testing."""
    vote, _ = await Vote.get_or_create(
        submission=submission,
        user=submission.challenge.owner,  # type: ignore
    )
    return vote


@pytest.fixture()
@pytest.mark.asyncio
async def vote_fixture() -> Vote:
    """Vote fixture with challenge on voting."""
    challenge: Challenge = await populate_challenge(challenge_status="vote")
    submission: Submission = await populate_submission(challenge=challenge)

    return await populate_vote(submission=submission)
