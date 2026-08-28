ARG RUST_VERSION=1

FROM rust:${RUST_VERSION}-bookworm AS builder

# Use a shell that exists whenever it encounters errors
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

RUN apt update \
    && apt install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* /tmp/*

WORKDIR /build

COPY ntpd-rs /build

COPY ./*.patch /build/

# This patch (provided by David Venhoek) attempts to disable all the system calls
# to the clock to prevent steering of the OS. It does lead to unstable behaviour,
# but in the context of networking interop, that's fine.
RUN patch -p1 < 0001-Prototype-for-not-touching-the-system-clock.patch

# Even with local-stratum = 1 set, the leap indicator will end up being set to
# "unknown", which clients will interpret as unsynchronised and thus fail.
RUN patch -p1 < 0002-Keep-stratum-1-leap-indicator.patch

# Run the build command.
# Note that this mounts several cache directories to speed up subsequent builds.
# After build, we move the binaries out of the target directory because that directory
# will not be available in the next steps (as it is a cached directory).
RUN --mount=type=cache,target=/usr/local/cargo/git/db \
    --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/build/target/ \
    cargo build --locked --release --features="${NTPDRS_BUILD_FEATURES}" \
    && mkdir -p /build/artifacts \
    && cp target/release/ntp-daemon /build/artifacts \
    && cp target/release/ntp-ctl /build/artifacts \
    && cp target/release/ntp-metrics-exporter /build/artifacts

# Copy both the server and client configuration over
COPY *.toml ./config/
COPY run.sh /