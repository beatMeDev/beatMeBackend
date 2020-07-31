from typing import List
from urllib.parse import urlencode

import typer

from orjson import loads
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError

from app.models.db import Text
from app.services.playlists import create_playlist
from app.settings import APP_MODELS
from app.settings import SPOTIFY_ID
from app.settings import SPOTIFY_REDIRECT_URI
from app.settings import TORTOISE_CONFIG


def with_db(function):
    async def init_db(*args, **kwargs):
        try:
            await Tortoise.init(config=TORTOISE_CONFIG, modules={"models": APP_MODELS})
        except DBConnectionError:
            await Tortoise.init(
                config=TORTOISE_CONFIG, modules={"models": APP_MODELS}, _create_db=True,
            )
        await Tortoise.generate_schemas()

        return await function(*args, **kwargs)

    return init_db


@with_db
async def populate_texts():
    with open("manage/fixtures/texts.json", "r") as texts_file:
        texts: List[str] = loads(texts_file.read())

    for content in texts:
        text, created = await Text.get_or_create(content=content)

        if created:
            typer.echo(f"Added - {text.content[:50]}")
        else:
            typer.echo(f"Exists - {text.content[:50]}")


def get_spotify_access_token_url():
    login_url = f"https://accounts.spotify.com/authorize"
    scopes = "user-read-private,user-read-email"
    params = {
        "response_type": "token",
        "client_id": SPOTIFY_ID,
        "scope": scopes,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
    }
    query = urlencode(params)
    url = f"{login_url}?{query}"

    return url


@with_db
async def populate_playlists(access_token):
    #  TODO automate access token via `pyppeteer` or use database
    with open("manage/fixtures/playlists.json", "r") as playlists_file:
        spotify_urls: List[str] = loads(playlists_file.read())

    for spotify_url in spotify_urls:
        playlist = await create_playlist(link=spotify_url, access_token=access_token)
        typer.echo(f"Added - {playlist.name} - {spotify_url}")
