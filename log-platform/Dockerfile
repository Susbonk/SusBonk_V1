FROM rust:1.85-slim as builder
RUN apt-get update && apt-get install -y pkg-config libssl-dev gcc && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Copy the entire workspace to preserve the workspace structure
COPY . .

# Build from the services directory
WORKDIR /app/services
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Copy binaries from the correct location in the workspace
COPY --from=builder /app/target/release/ingestd /usr/local/bin/ingestd
COPY --from=builder /app/target/release/alertd  /usr/local/bin/alertd

CMD ["ingestd"]
