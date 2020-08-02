"""Test challenge pydantic models."""
from datetime import datetime
from datetime import timedelta
from uuid import uuid4

from pydantic import ValidationError
from truth.truth import AssertThat  # type: ignore

from app.models.api.challenge import ChallengeIn


def test_challenge_in_vote_end() -> None:
    """Check when vote end date less than now and challenge end"""
    with AssertThat(ValidationError).IsRaised():
        ChallengeIn(
            name="test",
            challenge_end=datetime.utcnow() + timedelta(minutes=1),
            vote_end=datetime.utcnow() - timedelta(minutes=1),
            is_public=True,
            is_open=True,
            track_id=uuid4(),
        )
