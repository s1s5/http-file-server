FROM python:3.10-slim AS base

FROM base AS builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="$PATH:/root/.poetry/bin:/runtime/bin" \
    PYTHONPATH="$PYTHONPATH:/runtime/lib/python3.10/site-packages" \
    POETRY_VERSION=1.1.5

RUN python -c "import urllib.request; urllib.request.urlretrieve('https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py', '/tmp/get-poetry.py')" && python /tmp/get-poetry.py

WORKDIR /opt

COPY pyproject.toml poetry.lock ./
RUN pip install cleo tomlkit poetry.core requests cachecontrol cachy html5lib pkginfo virtualenv lockfile
RUN poetry export --dev --without-hashes --no-interaction --no-ansi -f requirements.txt -o requirements.txt
RUN pip install --prefix=/runtime --force-reinstall -r requirements.txt

FROM base as runtime

WORKDIR /usr/src/app
RUN groupadd -g 1000 app && \
    useradd -d /usr/src/app -s /bin/bash -u 1000 -g 1000 app

COPY --from=builder /runtime /usr/local
COPY server.py ./server.py

USER app
CMD gunicorn server:app -b 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker  --max-requests 1000
