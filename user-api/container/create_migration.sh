#!/usr/bin/env bash
# Expects to be run from code root (.../container in repo, /src in container)

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
fullpath="migrations/migrations/$filename"
echo "Creating migration $filename"

cp migrations/template.py "$fullpath"

echo "Written to $fullpath"

echo "Done"
