FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Environment Variables

# Server
ENV ENVIRONMENT=development
ENV OPENAPI_URL="/openapi.json"
ENV SERVER_PORT=9000

# Database 
ENV DB_URL=postgres://postgres:postgres@localhost:5432/ax_relayer_dev

# RPC Urls
ENV ETHEREUM_RPC=inject_at_deployment
ENV BSC_RPC=inject_at_deployment
ENV POLYGON_RPC=inject_at_deployment
ENV AVALANCHE_RPC=inject_at_deployment
ENV FANTOM_RPC=inject_at_deployment
ENV ARBITRUM_RPC=inject_at_deployment
ENV CELO_RPC=inject_at_deployment

# REDIS
ENV REDIS_HOST=inject_at_deployment
ENV REDIS_PORT=inject_at_deployment
ENV REDIS_DB=inject_at_deployment
ENV REDIS_PASSWORD=inject_at_deployment
ENV REDIS_ZSET=inject_at_deployment

# EVM
ENV RELAYER_PRIVATE_KEY=inject_at_deployment
ENV RELAYER_ADDRESS=inject_at_deployment

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]
