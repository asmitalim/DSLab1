#! /usr/bin/env bash
maxN=16
for ((i=0;i<$maxN;i++))
    do
        echo "Starting server $i"
        python3 ./server.py --id $i &
    done

python3 ./frontend.py &
python3 ./client.py --id 0 &