FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Environment Variables
# Server
ENV ENVIRONMENT=development
ENV OPENAPI_URL="/openapi.json"
ENV SERVER_PORT=8000

# Wormhole
ENV GUARDIAN_SPY_URL=inject_at_deployment
ENV SPY_SERVICE_FILTERS=inject_at_deployment
ENV RECONNECT_WAIT_TIME=2

# Database 
ENV DB_URL=postgres://postgres:postgres@localhost:5432/ax_relayer_dev

# REDIS
ENV REDIS_HOST=inject_at_deployment
ENV REDIS_PORT=inject_at_deployment
ENV REDIS_DB=inject_at_deployment
ENV REDIS_PASSWORD=inject_at_deployment
ENV REDIS_ZSET=inject_at_deployment

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]


