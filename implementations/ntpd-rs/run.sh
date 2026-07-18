#!/bin/bash

MODE=$1

if [[ "$MODE" == "client" ]]; then
    ./artifacts/ntp-daemon -c ./config/client.toml &> /data/client.log;
elif [[ "$MODE" == "server" ]]; then
    ./artifacts/ntp-daemon -c ./config/server.toml &> /data/server.log;
else
    echo "No mode specified, exiting!";
    exit 1;
fi
