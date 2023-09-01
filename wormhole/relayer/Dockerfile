FROM python:3.9

# Create a non-root user and set permissions
RUN useradd -ms /bin/bash dockeruser && \
    mkdir -p /wh_relayer && \
    chown -R dockeruser:dockeruser /wh_relayer

# Switch to non-root user
USER dockeruser

WORKDIR /wh_relayer

# Copy only the requirements.txt first to leverage Docker cache
COPY --chown=dockeruser:dockeruser ./requirements.txt /wh_relayer/requirements.txt

# Install Python dependencies and switch to non-root user
RUN pip install --no-cache-dir --upgrade -r /wh_relayer/requirements.txt

COPY --chown=dockeruser:dockeruser ./app /wh_relayer/app

# Environment Variables

# Server
ENV SERVER_PORT=9000
ENV OPENAPI_URL=inject_at_deployment
ENV ENVIRONMENT=development


# Database 
ENV DB_URL=inject_at_deployment

# RPC Urls
ENV ETHEREUM_RPC=inject_at_deployment
ENV BSC_RPC=inject_at_deployment
ENV POLYGON_RPC=inject_at_deployment
ENV AVALANCHE_RPC=inject_at_deployment
ENV FANTOM_RPC=inject_at_deployment
ENV ARBITRUM_RPC=inject_at_deployment
ENV CELO_RPC=inject_at_deployment
ENV OPTIMISM_RPC=inject_at_deployment

# REDIS
ENV REDIS_ZSET=inject_at_deployment
ENV REDIS_URL=inject_at_deployment

# EVM
ENV RELAYER_PRIVATE_KEY=inject_at_deployment
ENV RELAYER_ADDRESS=inject_at_deployment
ENV EVM_WORMHOLE_BRIDGE=inject_at_deployment

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]
