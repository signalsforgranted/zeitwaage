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

# The 2.0 alphas ignore local-stratum/reference-id entirely (FIXME upstream), so
# a server always reports stratum 16. This patch adds a [synchronization]
# section to the config and passes it through.
RUN patch -p1 < 0002-Expose-local-stratum-and-reference-id.patch

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