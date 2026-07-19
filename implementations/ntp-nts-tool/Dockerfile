FROM golang:1.18

WORKDIR /build
COPY ntp-nts-tool/ .
COPY run.sh /

RUN go mod verify

RUN go build -buildvcs=false