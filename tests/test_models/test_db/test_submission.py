"""Tests Submission models."""
import pytest

from truth.truth import AssertThat  # type: ignore

from app.models.db import Submission


@pytest.mark.asyncio
async def test_str(
        submission_fixture: Submission,
) -> None:
    """Check str of Submission model."""
    AssertThat(str(submission_fixture)).IsInstanceOf(str)
    AssertThat(str(submission_fixture)).IsEqualTo(submission_fixture.url)
