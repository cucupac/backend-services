FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Environment Variables
# Server
ENV OPENAPI_URL="/openapi.json"
ENV SERVER_PORT=8000
ENV ENVIRONMENT=development
ENV SPY_SERVICE_FILTERS=inject_at_deployment

# Wormhole
ENV GUARDIAN_SPY_URL=inject_at_deployment
ENV SPY_SERVICE_FILTERS=inject_at_deployment

# Database 
ENV DB_URL=postgres://postgres:postgres@localhost:5432/ax_relayer_dev

# RMQ
ENV RMQ_HOST=inject_at_deployment
ENV RMQ_PORT=5672
ENV RMQ_USERNAME=inject_at_deployment
ENV RMQ_PASSWORD=inject_at_deployment
ENV EXCHANGE_NAME=vaa_exchange
ENV ROUTING_KEY=wormhole_vaa
ENV QUEUE_NAME=vaa_queue

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]


