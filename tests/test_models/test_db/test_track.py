"""Tests Track models."""
import pytest

from truth.truth import AssertThat  # type: ignore

from app.models.db import Track


@pytest.mark.asyncio
async def test_str(
        track_fixture: Track,
) -> None:
    """Check str of Track model."""
    AssertThat(str(track_fixture)).IsInstanceOf(str)
    AssertThat(track_fixture.name).IsIn(str(track_fixture))
    AssertThat(track_fixture.author_name).IsIn(str(track_fixture))
