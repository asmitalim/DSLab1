#! /usr/bin/env bash
ps -eo user,pid,cmd | grep server.py | grep -v grep | sed "s/ \+/ /g" | cut -d' ' -f2,6 | awk '{print $1}' |     xargs kill -9
ps -eo user,pid,cmd | grep client.py | grep -v grep | sed "s/ \+/ /g" | cut -d' ' -f2,6 | awk '{print $1}' |     xargs kill -9
ps -eo user,pid,cmd | grep frontend.py | grep -v grep | sed "s/ \+/ /g" | cut -d' ' -f2,6 | awk '{print $1}' |     xargs kill -9
