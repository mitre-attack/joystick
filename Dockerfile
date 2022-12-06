# syntax=docker/dockerfile:1

FROM python:3.7-slim

# OCI labels
LABEL "org.opencontainers.image.title"="MITRE Joystick"
LABEL "org.opencontainers.image.url"="https://ctid.mitre-engenuity.org/"
LABEL "org.opencontainers.image.source"="https://github.com/mitre-attack/joystick"
LABEL "org.opencontainers.image.license"="Apache-2.0"

ENV APP_DIR /app
ENV PYTHONUNBUFFERED 1

# setup venv
RUN mkdir /${APP_DIR} && \
    python -m venv /${APP_DIR}/.venv && \
    /${APP_DIR}/.venv/bin/python -m pip install -U pip wheel setuptools

# add to path
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 \
    PATH=/${APP_DIR}/.venv/bin:${PATH}

WORKDIR ${APP_DIR}

# Install dependencies
COPY . .

RUN --mount=type=cache,target=/root/.cache \
    python -m pip install -r requirements.txt

# create unprivileged service account
RUN useradd -r -u 1001 app_user
EXPOSE 8080
USER app_user

CMD ["python", "/app/joystick.py"]
