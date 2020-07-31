import asyncio

import typer

from manage.services import get_spotify_access_token_url
from manage.services import populate_playlists
from manage.services import populate_texts


app = typer.Typer()
loop = asyncio.get_event_loop()


@app.command(name="populate_texts", help="Populate loader texts")
def populate_texts_command():
    loop.run_until_complete(populate_texts())


@app.command(
    name="populate_playlists",
    help="Populate spotify playlists",
)
def populate_playlists_command(
        access_token: str = typer.Option(
            ...,
            prompt=f"Login to spotify and copy access token: {get_spotify_access_token_url()}",
        )
):
    loop.run_until_complete(populate_playlists(access_token))


if __name__ == "__main__":
    app()
