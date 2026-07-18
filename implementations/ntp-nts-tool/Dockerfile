FROM golang:1.18

WORKDIR /build
COPY ntp-nts-tool/ .

RUN go mod verify

RUN go build -buildvcs=false