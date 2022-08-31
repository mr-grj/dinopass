FROM python:3.10-slim-bullseye AS builder

ENV APP_USER=dinopass
ENV APP_HOME=/home/$APP_USER
ENV SRC_FOLDER=$APP_HOME/backend

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_VERSION=22.1 \
    POETRY_VERSION=1.1.7 \
    POETRY_LIB_DIR="$APP_HOME/.local/bin" \
    PYSETUP_PATH="$APP_HOME/.pysetup" \
    POETRY_CACHE_DIR="$APP_HOME/.cache/poetry" \
    PYTHONPATH=$SRC_FOLDER


ENV POETRY_VENV_DIR="$PYSETUP_PATH/.venv"
ENV PATH="$POETRY_LIB_DIR:$POETRY_VENV_DIR:$PATH"


RUN useradd -ms /bin/bash $APP_USER && \
    apt-get update  -y && \
    apt-get upgrade -y && \
    apt-get install --fix-missing --no-install-recommends -y curl sudo gcc linux-libc-dev libc6-dev && \
    apt-get autoremove && \
    apt-get clean && \
    adduser $APP_USER sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers


USER $APP_USER

RUN pip install pip==$PIP_VERSION poetry==$POETRY_VERSION && \
    poetry config cache-dir $POETRY_CACHE_DIR && \
    poetry config virtualenvs.path $POETRY_VENV_DIR && \
    poetry config virtualenvs.in-project false && \
    poetry config virtualenvs.create false && \
    mkdir $SRC_FOLDER $PYSETUP_PATH


WORKDIR $SRC_FOLDER

COPY backend/poetry.lock backend/pyproject.toml ./
COPY backend/alembic.ini ./
COPY backend/migrations ./migrations

RUN poetry install --no-root --no-dev

CMD ["uvicorn", "main:app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "80"]
