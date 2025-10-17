# Scraper Dockerfile - Production-Ready Web Scraper
# Multi-stage build with Rust for optimal performance

FROM rust:1.75-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Copy source code
COPY src ./src

# Build release binary
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 scraper

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/target/release/scraper /app/scraper

# Change ownership
RUN chown -R scraper:scraper /app

# Switch to non-root user
USER scraper

# Set environment variables
ENV RUST_LOG=info

# Run the scraper
CMD ["./scraper"]
