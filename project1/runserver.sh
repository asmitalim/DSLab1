#! /usr/bin/env bash
EXPECTED_ARGS=1


if [ $# -eq $EXPECTED_ARGS ]
then
        python3 ./server.py --id $1 &

else
        echo "Invalid number of args. Usage: ./runserver.sh <serverID>"
fi;