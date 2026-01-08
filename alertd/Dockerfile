FROM rust:1.83 as builder

WORKDIR /app
COPY Cargo.toml ./
COPY src ./src

RUN cargo build --release

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/target/release/alertd .

ENV RUST_LOG=info
ENV OPENSEARCH_URL=http://opensearch:9200
ENV INDEX_PREFIX=susbonk

EXPOSE 8080

CMD ["./alertd"]
