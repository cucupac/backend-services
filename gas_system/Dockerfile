FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Environment Variables

# Server
ENV OPENAPI_URL="/openapi.json"
ENV SERVER_PORT=9000
ENV ENVIRONMENT=development

# Database 
ENV DB_URL=postgres://postgres:postgres@localhost:5432/ax_relayer_dev

# EVM
ENV ADMIN_PRIVATE_KEY=inject_at_deployment
ENV ADMIN_ADDRESS=inject_at_deployment
ENV WORMHOLE_BRIDGE_ABI=inject_at_deployment
ENV CHAIN_LOOKUP=inject_at_deployment

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]
