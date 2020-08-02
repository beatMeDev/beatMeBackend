"""Tests User models."""
import pytest

from truth.truth import AssertThat  # type: ignore

from app.models.db import User


@pytest.mark.asyncio
async def test_str(
        user_fixture: User,
) -> None:
    """Check str of User model."""
    AssertThat(str(user_fixture)).IsInstanceOf(str)
    AssertThat(str(user_fixture)).IsEqualTo(user_fixture.name())
