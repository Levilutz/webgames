#!/usr/bin/env bash

# Expects 1 argument: migration name

set -e

echo "Ensuring arg supplied"
if [ $# != 1 ]
then
    echo "Error: Got $# args, expect 1"
    exit 1
fi

# TODO complain if name doesn't match regex `[a-zA-Z0-9\-_]+`

c_time=$(date +"%s")
filename="m_${c_time}_$1.py"
fullpath="user-api/container/migrations/migrations/$filename"
echo "Creating migration $filename"

cp user-api/container/migrations/template.py "$fullpath"

echo "Written to $fullpath"

echo "Done"
