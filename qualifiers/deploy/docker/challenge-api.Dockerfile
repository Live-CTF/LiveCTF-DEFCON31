FROM rust:slim-bullseye as builder
WORKDIR /usr/src/livectf

RUN apt-get update \
    && apt-get install -y pkg-config libssl-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Capture dependencies
COPY infrastructure/Cargo.toml infrastructure/Cargo.lock ./

RUN cargo new --lib common
COPY infrastructure/common/Cargo.toml common/

RUN cargo new --lib challenge-api
COPY infrastructure/challenge-api/Cargo.toml challenge-api/

RUN cargo new --lib dashboard
COPY infrastructure/dashboard/Cargo.toml dashboard/

RUN cargo new --lib score-reporter
COPY infrastructure/score-reporter/Cargo.toml score-reporter/

RUN cargo new --lib exploit-runner
COPY infrastructure/exploit-runner/Cargo.toml exploit-runner/

RUN cargo new --lib exploit-builder
COPY infrastructure/exploit-builder/Cargo.toml exploit-builder/

RUN --mount=type=cache,target=/usr/local/cargo/registry \
    cargo build -p challenge-api --release

COPY infrastructure/ .
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    touch challenge-api/src/main.rs \
        exploit-builder/src/main.rs \
        exploit-builder/src/lib.rs \
        exploit-runner/src/main.rs \
        exploit-runner/src/lib.rs \
        common/src/lib.rs && \
        cargo build -p challenge-api --release


FROM debian:bullseye-slim

RUN apt-get update \
    && apt-get install -y ca-certificates libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/livectf/target/release/challenge-api /usr/local/bin/challenge-api
CMD ["challenge-api"]
