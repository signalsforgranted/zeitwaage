#!/bin/bash

MODE=$1

if [[ "$MODE" == "client" ]]; then
    /build/chronyd -n -x -f /build/client.conf -t 10 &> /data/client.log;
elif [[ "$MODE" == "server" ]]; then
    /build/chronyd -n -x -f /build/server.conf  &> /data/server.log;
else
    echo "No mode specified, exiting!";
    exit 1;
fi
