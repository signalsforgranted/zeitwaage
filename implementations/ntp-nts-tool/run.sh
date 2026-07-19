#!/bin/bash

MODE=$1

if [[ "$MODE" == "client" ]]; then
    /build/ntp_nts_tool ntpv5 ntp-server:1123 -d -draft draft-ietf-ntp-ntpv5-06 &> /data/client.log;
elif [[ "$MODE" == "server" ]]; then
    echo "Server mode not supported!";
    exit 1;
else
    echo "No mode specified, exiting!";
    exit 1;
fi
