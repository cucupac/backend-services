FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Environment Variables

# Server
ENV OPENAPI_URL="/openapi.json"
ENV SERVER_PORT=11000
ENV ENVIRONMENT=development

# Database 
ENV DB_URL=postgres://postgres:postgres@localhost:5432/ax_services_dev
ENV DB_SCHEMA=ax_scan

EXPOSE $SERVER_PORT

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


CMD ["python", "-m", "app"]
