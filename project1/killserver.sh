#! /usr/bin/env bash
#ps -ef | grep server.py | grep -v grep | sed -e "s/   / /g" | sed -e "s/  / /g" | cut -d' ' -f2 | awk '{print $1}' | xargs kill -9
#ps -ef | grep client.py | grep -v grep | sed -e "s/   / /g" | sed -e "s/  / /g" | cut -d' ' -f2 | awk '{print $1}' | xargs kill -9
#ps -ef | grep frontend.py | grep -v grep | sed -e "s/   / /g" | sed -e "s/  / /g" | cut -d' ' -f2 | awk '{print $1}' | xargs kill -9

ps -eo pid,cmd | grep server.py | grep -v grep | cut -d' ' -f1,5 | awk '{print $1}' | xargs kill -9

ps -eo pid,cmd | grep server.py |grep -v grep | sed "s/ \+/ /g" | cut -d' ' -f2 | xargs kill -9
