#!/usr/bin/env bash
# Expects to be run from code root (.../container in repo, /src in container)

tmp=0

mypy user_api --strict || tmp=$?
black --check --diff user_api || tmp=$?
flake8 --max-line-length=88 user_api || tmp=$?

mypy migrations --strict || tmp=$?
black --check --diff migrations || tmp=$?
flake8 --max-line-length=88 migrations || tmp=$?

# No mypy for tests (gets messy with patching / mocking sometimes)
black --check --diff tests || tmp=$?
flake8 --max-line-length=88 tests || tmp=$?

if [ $tmp -ne 0 ]
then
    echo "Something failed"
    exit $tmp
fi
