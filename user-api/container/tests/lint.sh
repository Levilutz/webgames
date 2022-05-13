#!/usr/bin/env bash
# Expects to be run from code root (.../container in repo, /src in container)

mypy user_api --strict
black --check --diff user_api
flake8 --max-line-length=88 user_api

mypy migrations --strict
black --check --diff migrations
flake8 --max-line-length=88 migrations
