#!/bin/bash

MODE=$1

if [[ "$MODE" == "client" ]]; then
    python /build/ntpnode.py -d ntp-server:1123 &> /data/client.log;
elif [[ "$MODE" == "server" ]]; then
    python /build/ntpnode.py -d -l -p 1123 &> /data/server.log;
else
    echo "No mode specified, exiting!";
    exit 1;
fi
