# Multi-stage build for SusBonk telegram-bot
# Using Rust nightly for 2024 edition and latest crate support
FROM rustlang/rust:nightly-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy workspace files
COPY Cargo.toml Cargo.lock ./
COPY app ./app
COPY config ./config
COPY entity ./entity

# Build the bot binary (release mode)
RUN cargo build --release --bin bot

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN useradd -r -s /bin/false appuser

WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/target/release/bot /app/bot

# Change ownership
RUN chown -R appuser:appuser /app
USER appuser

CMD ["./bot"]

