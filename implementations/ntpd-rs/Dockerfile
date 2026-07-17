FROM rust:1.95

WORKDIR /usr/src/app

COPY ntpd-rs .

RUN cargo build --release --all

RUN mkdir cert && openssl req -x509 \
    -newkey ed25519 \
    -days 365 \
    -noenc \
    -keyout cert/ntske.key \
    -out cert/ntske.crt \
    -subj "/CN=nts-ke-serve"

COPY config.toml .
