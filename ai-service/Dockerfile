# Multi-stage build for ai-service
# Using Rust nightly for 2024 edition support
FROM rustlang/rust:nightly-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY Cargo.toml Cargo.lock ./
COPY src ./src

# Build the service binary (release mode) with locked dependencies
RUN cargo build --release --locked

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN useradd -r -s /bin/false appuser

WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/target/release/ai_service /app/ai_service

# Change ownership
RUN chown -R appuser:appuser /app
USER appuser

ENV RUST_LOG=info

CMD ["./ai_service"]
