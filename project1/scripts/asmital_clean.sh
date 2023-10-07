#!/bin/bash

sudo docker image rm $(sudo docker image ls --format '{{.Repository}} {{.ID}}' | grep 'asmital' | awk '{print $2}')

sudo docker build . -f dockerfiles/frontend.dockerfile -t asmital/dslab1:frontend --network=host
sudo docker push asmital/dslab1:frontend

sudo docker build . -f dockerfiles/server.dockerfile -t asmital/dslab1:server --network=host
sudo docker push asmital/dslab1:server


