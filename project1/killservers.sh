#! /usr/bin/env bash
ps -ef | grep server.py | grep -v grep | sed -e "s/   / /g" | sed -e "s/  / /g" | cut -d' ' -f2 | awk '{print $1}' | xargs kill -9
ps -ef | grep client.py | grep -v grep | sed -e "s/   / /g" | sed -e "s/  / /g" | cut -d' ' -f2 | awk '{print $1}' | xargs kill -9
ps -ef | grep frontend.py | grep -v grep | sed -e "s/   / /g" | sed -e "s/  / /g" | cut -d' ' -f2 | awk '{print $1}' | xargs kill -9
