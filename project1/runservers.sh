#! /usr/bin/env bash
maxN=16
for ((i=0;i<$maxN;i++))
    do
        echo "Starting server $i"
        python3 ./server.py --id $i &
    done

echo "Starting frontend"
python3 ./frontend.py &
echo "Starting client 0"
python3 ./client.py --id 0 &
