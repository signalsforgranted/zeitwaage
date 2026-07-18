FROM golang:1.24

WORKDIR /build
COPY ntp-go/ .
RUN mkdir -p /build/cmd
COPY main.go /build/cmd

RUN go mod verify

RUN go build -buildvcs=false -o ./ntp-go-client ./cmd/