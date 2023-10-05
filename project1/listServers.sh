#! /usr/bin/env bash
ps -eo pid,cmd | grep server.py | grep -v grep | sed "s/ \+/ /g" | cut -d' ' -f2,6 | awk '{print "Server-" $2 " ,PID: " $1}'
ps -eo pid,cmd | grep client.py | grep -v grep | sed "s/ \+/ /g" | cut -d' ' -f2,6 | awk '{print "Client-" $2 " ,PID: " $1}'
ps -eo pid,cmd | grep frontend.py | grep -v grep | sed "s/ \+/ /g" | cut -d' ' -f2,6 | awk '{print "Frontend" $2 " ,PID: " $1}'
