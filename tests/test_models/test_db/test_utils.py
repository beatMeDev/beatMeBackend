"""Tests User models."""
import pytest

from truth.truth import AssertThat  # type: ignore

from app.models.db import Text


@pytest.mark.asyncio
async def test_str(
        populate_texts: Text,
) -> None:
    """Check str of Text model."""
    AssertThat(str(populate_texts)).IsInstanceOf(str)
    AssertThat(str(populate_texts)).IsIn(populate_texts.content)
