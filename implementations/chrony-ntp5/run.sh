#!/bin/bash

MODE=$1

if [[ "$MODE" == "client" ]]; then
    /build/chronyd -n -x -f /build/client.conf -L 8 -t 10 &> /data/client.log;
elif [[ "$MODE" == "server" ]]; then
    /build/chronyd -n -x -f /build/server.conf -L 8 &> /data/server.log;
else
    echo "No mode specified, exiting!";
    exit 1;
fi
