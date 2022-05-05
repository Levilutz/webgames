# Base image and shared variables
FROM python:3.9-slim as base


# Builder image
FROM base as builder

RUN apt-get update -y
RUN apt-get install -y libpq-dev gcc
RUN python3 -m pip install --upgrade pip

COPY requirements.txt /requirements.txt

RUN pip3 install --upgrade --user -r /requirements.txt


# Migrations image
FROM base as api
LABEL org.opencontainers.image.authors="Levi Lutz (contact.levilutz@gmail.com)"

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY src /src

WORKDIR /src
CMD ["uvicorn", "--port=80", "--host=0.0.0.0", "routers.main:app"]
