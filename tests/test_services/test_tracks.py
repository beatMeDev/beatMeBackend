"""Tracks services tests."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from orjson import loads  # pylint: disable-msg=E0611
from pydantic.main import BaseModel  # pylint: disable=no-name-in-module
from truth.truth import AssertThat  # type: ignore

from app.models.db import Playlist
from app.models.db import Track
from app.services.tracks import add_tracks_to_playlist
from app.services.tracks import format_track


class MetaModel(BaseModel):  # pylint: disable=too-few-public-methods
    """Meta track data."""
    album: str
    duration: float


class TrackModel(BaseModel):  # pylint: disable=too-few-public-methods
    """Track model."""
    name: str
    author_name: str
    cover_url: str
    preview_url: Optional[str]
    spotify_id: str
    recommended: bool
    meta: MetaModel


with open("tests/fixtures/tracks.json", "r") as tracks_file:
    content: Dict[str, Any] = loads(tracks_file.read())
    RAW_TRACK: Dict[str, Any] = content["raw_track"]


def test_format_track() -> None:
    """Check formatted track has valid format"""
    formatted_track: Optional[Dict[str, Any]] = format_track(track_info=RAW_TRACK)

    AssertThat(TrackModel(**formatted_track).validate(formatted_track)).IsNotEmpty()  # type: ignore


def test_format_track_empty_track() -> None:
    """Check formatted track is None when track data is empty."""
    formatted_track: Optional[Dict[str, Any]] = format_track(track_info={})

    AssertThat(formatted_track).IsNone()


def test_format_track_empty_track_id() -> None:
    """Check formatted track is None when track id is None."""
    formatted_track: Optional[Dict[str, Any]] = format_track(track_info={"track": {"name": "test"}})

    AssertThat(formatted_track).IsNone()


@pytest.mark.asyncio
async def test_add_tracks_to_playlist() -> None:
    """Check tracks added to playlist."""
    playlist: Playlist = await Playlist.create(
        name="test", url="test", spotify_id="test", recommended=True,
    )
    raw_tracks: List[Dict[str, Any]] = [RAW_TRACK, {}]
    formatted_track: Optional[Dict[str, Any]] = format_track(RAW_TRACK)
    track_spotify_id: str = formatted_track["spotify_id"]  # type: ignore

    is_added: bool = await add_tracks_to_playlist(playlist=playlist, tracks=raw_tracks)
    track: Optional[Track] = await Track.filter(
        playlists=playlist, spotify_id=track_spotify_id
    ).first()

    AssertThat(is_added).IsTrue()
    AssertThat(track).IsNotNone()
    AssertThat(track.spotify_id).IsEqualTo(track_spotify_id)  # type: ignore
