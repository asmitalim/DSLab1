#! /usr/bin/env bash
EXPECTED_ARGS=0


if [ $# -eq $EXPECTED_ARGS ]
then
        python3 ./frontend.py &

else
        echo "Invalid number of args. Usage: ./frontend.py"
fi;