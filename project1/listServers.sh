#! /usr/bin/env bash
ps -ef | grep server.py | grep -v grep | sed -e "s/   / /g" | sed -e "s/  / /g" | cut -d' ' -f2,9,11 | awk '{print "Server-" $3 " ,PID: " $1}'
ps -ef | grep client.py | grep -v grep | sed -e "s/   / /g" | sed -e "s/  / /g" | cut -d' ' -f2,9,11 | awk '{print "Client-" $3 " ,PID: " $1}'
ps -ef | grep frontend.py | grep -v grep | sed -e "s/   / /g" | sed -e "s/  / /g" | cut -d' ' -f2,9,11 | awk '{print "FrontEnd ,PID: " $1}'
