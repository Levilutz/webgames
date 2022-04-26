# Base image and shared variables
FROM python:3.9-slim as base
ARG userpath="/root/.local/lib/python3.9/site-packages/"


# Builder image
FROM base as builder

RUN apt-get update -y
RUN apt-get install -y libpq-dev gcc
RUN python3 -m pip install --upgrade pip

COPY requirements.txt /requirements.txt

RUN pip3 install --upgrade --user -r /requirements.txt


# Migrations image
FROM base as migrations
LABEL org.opencontainers.image.authors="Levi Lutz (contact.levilutz@gmail.com)"

COPY --from=builder $userpath $userpath
COPY src /src

WORKDIR /src
CMD ["python3", "entrypoint.py"]
