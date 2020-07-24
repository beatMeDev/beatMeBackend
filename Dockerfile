FROM python:3.8.4-slim

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY poetry.lock pyproject.toml ./
RUN pip install poetry==1.0.* && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . ./
COPY .env.docker .env

CMD uvicorn --host=0.0.0.0 app:application