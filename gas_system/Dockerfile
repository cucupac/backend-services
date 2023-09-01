FROM python:3.9

# Create a non-root user and set permissions
RUN useradd -ms /bin/bash dockeruser && \
    mkdir -p /gas_system && \
    chown -R dockeruser:dockeruser /gas_system

# Switch to non-root user
USER dockeruser

WORKDIR /gas_system


# Copy only the requirements.txt first to leverage Docker cache
COPY --chown=dockeruser:dockeruser ./requirements.txt /gas_system/requirements.txt

# Install Python dependencies and switch to non-root user
RUN pip install --no-cache-dir --upgrade -r /gas_system/requirements.txt

COPY --chown=dockeruser:dockeruser ./app /gas_system/app


# Environment Variables

# Server
ENV SERVER_PORT=10000
ENV OPENAPI_URL=inject_at_deployment
ENV ENVIRONMENT=development

# Database 
ENV DB_URL=inject_at_deployment

# Price Client
ENV PRICE_CLIENT_BASE_URL=inject_at_deployment

# EVM
ENV FEE_SETTER_ADDRESS=inject_at_deployment
ENV FEE_SETTER_PRIVATE_KEY=inject_at_deployment
ENV EVM_WORMHOLE_BRIDGE=inject_at_deployment
ENV RELAYER_ADDRESS=inject_at_deployment
ENV PRIORITY_FEE_PERCENTILE=inject_at_deployment

# Fee Updates
ENV REMOTE_FEE_MULTIPLIER=inject_at_deployment
ENV HIGHER_ETHEREUM_FEE_MULTIPLIER=inject_at_deployment
ENV LOWER_ETHEREUM_FEE_MULTIPLIER=inject_at_deployment

# RPC URLs
ENV ETHEREUM_RPC=inject_at_deployment
ENV BSC_RPC=inject_at_deployment
ENV POLYGON_RPC=inject_at_deployment
ENV AVALANCHE_RPC=inject_at_deployment
ENV FANTOM_RPC=inject_at_deployment
ENV ARBITRUM_RPC=inject_at_deployment
ENV CELO_RPC=inject_at_deployment
ENV OPTIMISM_RPC=inject_at_deployment

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]
