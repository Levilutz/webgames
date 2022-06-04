#!/#!/usr/bin/env bash
# Expects to be run from code root (.../container in repo, /src in container)

set -e

mypy auth_api --strict
black --check --diff auth_api
flake8 --max-line-length=88 auth_api

# No mypy for tests (gets messy with patching / mocking sometimes)
black --check --diff tests
flake8 --max-line-length=88 tests

# shellcheck disable=SC2038
find . -iname "*.sh" | xargs shellcheck
echo "Shellcheck successful"
