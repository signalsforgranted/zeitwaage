FROM debian:latest

# Use a shell that exists whenever it encounters errors
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

WORKDIR /build

COPY chrony-ntp5 /build

RUN apt-get update && apt-get install -y gcc libc6 libc6-dev bison make pkg-config libcap-dev libseccomp-dev libgnutls30

RUN ./configure
RUN make