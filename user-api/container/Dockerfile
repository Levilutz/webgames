# Base image and shared variables
FROM python:3.9-slim as base


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

COPY user_api /src/user_api
COPY migrations /src/migrations
COPY tests /src/tests

WORKDIR /src
CMD ["echo", "No cmd provided"]
