FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Environment Variables

# Server
ENV OPENAPI_URL="/openapi.json"
ENV SERVER_PORT=10000
ENV ENVIRONMENT=development

# Database 
ENV DB_URL=postgres://postgres:postgres@localhost:5432/ax_relayer_dev

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

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]
