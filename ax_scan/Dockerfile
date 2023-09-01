FROM python:3.9

# Create a non-root user and set permissions
RUN useradd -ms /bin/bash dockeruser && \
    mkdir -p /ax_scan && \
    chown -R dockeruser:dockeruser /ax_scan

# Switch to non-root user
USER dockeruser

WORKDIR /ax_scan

# Copy only the requirements.txt first to leverage Docker cache
COPY --chown=dockeruser:dockeruser ./requirements.txt /ax_scan/requirements.txt

# Install Python dependencies and switch to non-root user
RUN pip install --no-cache-dir --upgrade -r /ax_scan/requirements.txt

COPY --chown=dockeruser:dockeruser ./app /ax_scan/app

# Environment Variables

# Server
ENV SERVER_PORT=11000
ENV OPENAPI_URL=inject_at_deployment
ENV ENVIRONMENT=development

# Database 
ENV DB_URL=inject_at_deployment
ENV DB_SCHEMA=ax_scan

# Ax Protocol
ENV EVM_WORMHOLE_BRIDGE=inject_at_deployment
ENV EVM_LAYERZERO_BRIDGE=inject_at_deployment

# RPC URLS
ENV ETHEREUM_RPC=inject_at_deployment
ENV BSC_RPC=inject_at_deployment
ENV POLYGON_RPC=inject_at_deployment
ENV AVALANCHE_RPC=inject_at_deployment
ENV FANTOM_RPC=inject_at_deployment
ENV ARBITRUM_RPC=inject_at_deployment
ENV CELO_RPC=inject_at_deployment
ENV OPTIMISM_RPC=inject_at_deployment
ENV GNOSIS_RPC=inject_at_deployment

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]
