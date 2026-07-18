#!/bin/bash

MODE=$1

if [[ "$MODE" == "client" ]]; then
    ./ntp-go-client -host ntp-server -port 1123 &> /data/client.log;
elif [[ "$MODE" == "server" ]]; then
    echo "Server mode not supported!";
    exit 1;
else
    echo "No mode specified, exiting!";
    exit 1;
fi
