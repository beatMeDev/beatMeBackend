# Beat Me

[![Tests](https://github.com/beatMeDev/beatMeBackend/workflows/tests/badge.svg)](https://github.com/beatMeDev/beatMeBackend/actions?query=workflow%3Atests)
[![Styles](https://github.com/beatMeDev/beatMeBackend/workflows/styles/badge.svg)](https://github.com/beatMeDev/beatMeBackend/actions?query=workflow%3Astyles)
[![codecov](https://codecov.io/gh/beatMeDev/beatMeBackend/branch/master/graph/badge.svg)](https://codecov.io/gh/beatMeDev/beatMeBackend)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/beatMeDev/beatMeBackend/blob/master/LICENSE)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


> Beat Me is challenges platform for music producers.

## TODO

- [x] Authentication - Facebook, Google, Spotify, VK
- [x] Challenges
- [x] Playlists
- [x] Import playlists from *spotify*
- [x] Tracks
- [x] Participants
- [x] Submissions
- [x] Voting
- [x] Populate recommended playlists
- [ ] Challenge statistics/scoreboard
- [ ] Search track on youtube
- [ ] 100% coverage

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

## Manage commands
To run manage command: `python manage/main.py {command}`

- `populate_texts` - populate texts for frontend loader from `texts.json`
- `populate_playlists` - populate *spotify* playlists from `playlists.json`

> Don't forget to set PYTHONPATH to the project

## Project structure

```
app                         - app root directory
├── main.py                 - contains application factory
├── models                  - application models
│         ├── api                 - pydantic models
│         └── db                  - tortoise orm models
│         └── __init__.py   - contains __models__ for tortoise orm models exploring
├── routes                  - api endpoints
├── services                - services with application logic
│         └── auth                - authentication services
│             └── providers       - external OAuth providers
├── settings                - applicaitons settings
└── utils                   - other stuff
tests                       - tests root directory
manage                      - application management
└── fixtures                - json fixtures storage
```
