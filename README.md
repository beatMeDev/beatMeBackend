# Beat Me

[![Tests](https://github.com/beatMeDev/beatMeBackend/workflows/tests/badge.svg)](https://github.com/beatMeDev/beatMeBackend/actions?query=workflow%3Atests)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/beatMeDev/beatMeBackend/blob/master/LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


> Beat Me is challenges platform for music producers.

## TODO

- [x] Authentication - Facebook, Google, Spotify, VK
- [ ] Tracks
- [ ] Playlists
- [ ] Import playlists from *spotify*
- [ ] Find track on youtube
- [ ] Populate recommended playlists
- [ ] Challenges
- [ ] Participants
- [ ] Submissions
- [ ] Voting

## Installation

Use the package manager [poetry](https://python-poetry.org/) to prepare backend running.

- Install poetry: `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python`.
- Install dependencies: `poetry install`.

## Run server

- Copy `.env.example` to `.env` and fill your data.
- Check `postgres` and `redis` are working.
- Run server: `uvicorn app:application --host 0.0.0.0 --port 8000`.

## Docker

- Copy `.env.docker.example` to `.env.docker` and fill your data.
- Run `docker-compose up -d` to start services.

Application will be available on http://127.0.0.1:8000.

## Tests

Tests are work by `pytest` and use `sqlite`(`TORTOISE_TEST_DB` in settings/base.py) instead of postgres.

- To run tests exec `pytest` in project directory.
- To calculate coverage ` pytest --cov=app --cov=tests --cov-report=term-missing`.

## Dev routes

- `/swagger/` - automatic interactive API documentation.
- `/redoc/` - alternative automatic documentation.

## Project structure

```
app                     - app root directory
├── __init__.py         - contains application initialization
├── models              - application models
│   ├── __init__.py     - contains __models__ for tortoise orm models exploring
│   ├── api             - pydantic models
│   └── db              - tortoise orm models
├── routes              - api endpoints
├── services            - services with application logic
│   └── auth            - authentication services
│       └── providers   - external OAuth providers
├── settings            - applicaitons settings
└── utils               - other stuff
tests                   - tests root directory
├── services            - services tests
│   └── auth            - auth tests
└── routes              - routes tests
```
