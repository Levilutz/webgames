#!/usr/bin/env bash

# Expects 1 argument: migration name

set -e

echo "Ensuring arg supplied"
if [ $# != 1 ]
then
    echo "Error: Got $# args, expect 1"
    exit 1
fi

c_time=$(date +"%s")
filename="m_${c_time}_$1.py"
echo "Creating migration $filename"

cp user-api/migrate/src/migrations/template.py "user-api/migrate/src/migrations/$filename"

echo "Done"
