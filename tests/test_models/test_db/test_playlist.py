"""Tests Playlist models."""
import pytest

from truth.truth import AssertThat  # type: ignore

from app.models.db import Playlist


@pytest.mark.asyncio
async def test_str(
        playlist_fixture: Playlist,
) -> None:
    """Check str of Playlist model."""
    AssertThat(str(playlist_fixture)).IsInstanceOf(str)
    AssertThat(str(playlist_fixture)).IsEqualTo(playlist_fixture.name)
