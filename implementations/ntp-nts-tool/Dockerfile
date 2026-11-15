FROM golang:1.18

WORKDIR /build
COPY ntp-nts-tool/ .
COPY run.sh /
COPY *.patch /patches/

# The submodule's .git file points outside the build context, so remove it
# before using git apply (the image has git, but not patch).
# 0001: accept host:port (the tool always appended :123).
RUN rm -f .git && git apply /patches/0001-Allow-host-port.patch

RUN go mod verify

RUN go build -buildvcs=false