#!/usr/bin/env bash
# Expects to be run from code root (.../container in repo, /src in container)

set -e

export MYPYPATH=stubs

# No black for stubs (formats .pyi files wrong)
mypy stubs --strict
flake8 --max-line-length=88 stubs

mypy user_api --strict
black --check --diff user_api
flake8 --max-line-length=88 user_api

mypy migrations --strict
black --check --diff migrations
flake8 --max-line-length=88 migrations

# No mypy for tests (gets messy with patching / mocking sometimes)
black --check --diff tests
flake8 --max-line-length=88 tests

# git ls-files | grep -P ".*\.sh$" | xargs shellcheck
# shellcheck disable=SC2038
find . -iname "*.sh" | xargs shellcheck
echo "Shellcheck successful"
