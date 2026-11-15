#!/bin/bash

MODE=$1
# The draft ID is sent on the wire and servers match it exactly. The tool
# only supports draft-ietf-ntp-ntpv5-05 and -06.
NTPV5_DRAFT=${NTPV5_DRAFT:-draft-ietf-ntp-ntpv5-06}

if [[ "$MODE" == "client" ]]; then
    /build/ntp_nts_tool ntpv5 ntp-server:1123 -d -draft "$NTPV5_DRAFT" &> /data/client.log;
elif [[ "$MODE" == "server" ]]; then
    echo "Server mode not supported!";
    exit 1;
else
    echo "No mode specified, exiting!";
    exit 1;
fi
