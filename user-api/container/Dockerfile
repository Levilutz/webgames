# Base image builder
FROM python:3.9-slim as base-builder

RUN apt-get update -y
RUN apt-get install -y shellcheck


# Base image
FROM python:3.9-slim as base

COPY --from=base-builder /usr/bin/shellcheck /usr/bin/shellcheck


# Builder image
FROM base as builder

RUN apt-get update -y
RUN apt-get install -y libpq-dev gcc
RUN python3 -m pip install --upgrade pip

COPY requirements.txt /requirements.txt

RUN pip3 install --upgrade --user -r /requirements.txt


# Main image
FROM base as main
LABEL org.opencontainers.image.authors="Levi Lutz (contact.levilutz@gmail.com)"

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=$PYTHONPATH:/src

COPY user_api_internal /src/user_api_internal
COPY migrations /src/migrations
COPY tests /src/tests
COPY create_migration.sh src/create_migration.sh

WORKDIR /src
CMD ["echo", "No cmd provided"]
